# -*- coding: utf-8 -*-
"""
This package provides tools to generate a Sitemap of an application.

Already implemented:
- metaclass SitemapMeta
- Flask (FlaskSitemap)

'Hello world' example:

    from framework import Framework
    from dynamic_sitemap import FrameworkSitemap

    app = Framework(__name__)
    sitemap = FrameworkSitemap(app, 'https://mysite.com')
    sitemap.update()

Basic example with some Models:

    from framework import Framework
    from dynamic_sitemap import FrameworkSitemap
    from models import Post, Tag

    app = Framework(__name__)
    sitemap = FrameworkSitemap(app, 'https://mysite.com', orm='sqlalchemy')
    sitemap.config.IGNORED.update(['/edit', '/upload'])
    sitemap.config.TEMPLATE_FOLDER = 'templates'
    sitemap.update()
    sitemap.add_elem('/faq', changefreq='monthly', priority=0.4)
    sitemap.add_rule('/blog', Post, lastmod_attr='created', priority=1.0)
    sitemap.add_rule('/blog/tag', Tag, changefreq='daily')

IGNORED has a priority over add_rule. Also you can set configurations from your class:

    sm_logger = logging.getLogger('sitemap')
    sm_logger.setLevel(30)

    class Config:
        TEMPLATE_FOLDER = os.path.join('app', 'templates')
        IGNORED = {'/admin', '/back-office', '/other-pages'}
        ALTER_PRIORITY = 0.1
        LOGGER = sm_logger

    sitemap = FrameworkSitemap(app, 'https://myshop.org', config_obj=Config)
    sitemap.add_elem('/about', changefreq='monthly', priority=0.4)
    sitemap.add_rule('/goods', Product, loc_attr='id', lastmod_attr='updated')

Moreover you can get a static file by using:
    sitemap.build_static()
"""
from abc import ABCMeta, abstractmethod
from datetime import timedelta
from filecmp import cmp
from itertools import tee
from logging import getLogger, StreamHandler
from os.path import join, exists
from pathlib import Path
from re import search, split
from shutil import copyfile
from typing import TypeVar, List
from xml.etree import ElementTree as ET

from .config import *
from .helpers import *
from .validators import get_validated


HTTPResponse = TypeVar('HTTPResponse')

XML_ATTRS = {
    'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xsi:schemaLocation':
        'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd'
}


class Record:
    """A class representing an item of a sitemap"""

    __slots__ = 'loc', 'lastmod', 'changefreq', 'priority'

    def __init__(self, loc: str, lastmod: str = None, changefreq: str = None, priority: float = None):
        self.loc = loc
        self.lastmod = lastmod
        self.changefreq = changefreq
        self.priority = priority

    def as_xml(self):
        """Returns xml.etree.ElementTree element"""
        element = ET.Element('url')
        ET.SubElement(element, 'loc').text = self.loc

        if self.lastmod:
            ET.SubElement(element, 'lastmod').text = self.lastmod

        if self.changefreq:
            ET.SubElement(element, 'changefreq').text = self.changefreq

        if self.priority:
            ET.SubElement(element, 'priority').text = str(self.priority)

        return element

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.loc == other.loc
        else:
            return False

    def __hash__(self):
        return hash(self.loc)

    def __repr__(self):
        return f'<Record loc="{self.loc}">'


class SitemapMeta(metaclass=ABCMeta):
    """The base class to inherit"""

    config = SitemapConfig()
    content_type = 'application/xml'
    filename = 'sitemap.xml'

    def __init__(self, app, base_url: str, config_obj: ConfType = None, orm: str = None):
        """Creates an instance of a Sitemap

        :param app: an application instance
        :param base_url: your base URL such as 'http://site.com'
        :param config_obj: a class with configurations
        :param orm: an ORM name used in project (use 'local' and check helpers.Model out for raw SQL queries)
        """
        self.app = app
        self.url = check_url(base_url)
        self.query = get_query(orm)
        self.start = None
        self.rules = None
        self.log = None

        # containers
        self._records = ()                            # to store prepared Records
        self._models = {}                             # to store Models added by add_rule
        self._static_data = set()                     # to store Record instances added by add_elem
        self._timestamp = datetime.now()

        self.update(config_obj, init=True)

    @property
    def records(self):
        """Returns records prepared to build sitemap"""
        self._records, records = tee(self._records)
        return tuple(records)

    def update(self, config_obj: ConfType = None, init: bool = False):
        """Updates sitemap instance configuration. Use it if you haven't passed config to __init__.

        :param config_obj: SitemapConfig instance or your own Config class
        :param init: True if method is called during initialization

        Example:
            sitemap = FrameworkSitemap(app, 'http://site.com')
            sitemap.config.TEMPLATE_FOLDER = os.path.join('extensions', 'templates')
            sitemap.update()
        """
        if config_obj:
            self.config.from_object(config_obj)

        self.start = get_iso_datetime(datetime.now(), self.config.TIMEZONE)
        self.log = self.get_logger()
        self.rules = self.get_rules()

        if config_obj or not init:
            self._copy_template()

    def add_elem(self, path: str, lastmod: str = None, changefreq: str = None, priority: float = None):
        """Adds a record to a sitemap according to the protocol https://www.sitemaps.org/protocol.html

        :param path: a part of URL, path to a page, should starts with a leading slash
        :param lastmod: a timestamp of last changes
        :param changefreq: how often this URL changes (daily, weekly, etc.)
        :param priority: a priority of URL to be set
        """
        params = get_validated(loc=path, lastmod=lastmod, changefreq=changefreq, priority=priority)
        self._static_data.add(
            Record(loc=urljoin(self.url, params.pop('loc')), **params)
        )

    def add_rule(self, path: str, model, loc_attr: str, lastmod_attr: str = None,
                 changefreq: str = None, priority: float = None):
        """Adds a rule to the builder to generate urls by a template using models of an app
        according to the protocol https://www.sitemaps.org/protocol.html

        :param path: a part of URI is used to get a page generated through a model
        :param model: a model of an app that has a slug, e.g. an instance of SQLAlchemy.Model
        :param loc_attr: an attribute of this model which is used to generate URL
        :param lastmod_attr: an attribute of this model which is an instance of the datetime object
        :param changefreq: how often this URL changes (daily, weekly, etc.)
        :param priority: a priority of URL to be set
        """
        priority = round(priority or 0.0, 1)
        get_validated(loc=path, changefreq=changefreq, priority=priority)

        for attr in (loc_attr, lastmod_attr if lastmod_attr else loc_attr,):
            try:
                getattr(model, attr)
            except AttributeError as exc:
                msg = f'Incorrect attributes are set for the model "{model}" in add_rule():\n' \
                      f'loc_attr = {loc_attr} and/or lastmod_attr = {lastmod_attr}'
                self.log.warning(msg)
                raise AttributeError(msg) from exc

        if not path.endswith('/'):
            path += '/'

        self._models[path] = PathModel(
            model=model,
            attrs={
                'loc_attr': loc_attr,
                'lastmod_attr':  lastmod_attr,
                'changefreq': changefreq or self.config.CONTENT_CHANGES,
                'priority':  priority or self.config.CONTENT_PRIORITY
            }
        )

    def build_static(self, path: DirPathType = None):
        """Builds an XML file. The system user of the app should have rights to write files

        :param path: a path to destination directory
        """
        self._prepare_data()

        folder = path or self.config.STATIC_FOLDER
        assert folder, 'You should set config.STATIC_FOLDER or pass it directly into build_static()'

        fullname = join(folder, self.filename) if isinstance(folder, str) else join(*folder, self.filename)
        self.log.info(f'Creating {fullname}...')

        url_set = ET.Element('urlset', XML_ATTRS)

        for record in self.records:
            url_set.append(record.as_xml())

        tree = ET.ElementTree(url_set)
        try:
            tree.write(fullname, xml_declaration=True, encoding='UTF-8')
        except FileNotFoundError as e:
            error = f'Seems like path "{path}" is not found or credentials required.'
            self.log.error(error)
            raise FileNotFoundError(error) from e

        self.log.info('Static sitemap is ready')

    def get_logger(self) -> Logger:
        """Returns an instance of logging.Logger (set in config)"""
        if self.config.LOGGER:
            logger = self.config.LOGGER
        else:
            logger = getLogger('sitemap')
            handler = StreamHandler()
            logger.addHandler(handler)

        if self.config.DEBUG and logger:
            set_debug_level(logger)
        return logger

    def get_dynamic_rules(self) -> list:
        """Returns all url should be added as a rule or to ignored list"""
        self.rules, all_rules = tee(self.rules)
        return [i for i in all_rules if search(r'<(\w+:)?\w+>', i)]

    def get_root(self) -> str:
        """Returns app's root directory. Set config.APP_ROOT if not suitable"""
        if self.config.APP_ROOT:
            return self.config.APP_ROOT

        if hasattr(self.app, '__package__'):
            str(Path(self.app.__package__).absolute())

        return str(Path(self.app.__module__).parent.absolute())

    @abstractmethod
    def get_rules(self) -> iter:
        """The method to override. Should return an iterator of URL rules"""
        pass

    @abstractmethod
    def view(self, *args, **kwargs) -> HTTPResponse:
        """The method to override. Should return HTTP response"""
        pass

    def _copy_template(self):
        """Copies an xml file with Jinja2 template to an app templates directory

        :raises:
            PermissionError: if unable to copy a template to destination
            FileExistsError: if another sitemap already exists
        """
        root, folder = self.get_root(), self.config.TEMPLATE_FOLDER
        folder_str = folder if isinstance(folder, str) else join(*folder)
        filename = join(root, folder_str, self.filename)

        if not exists(filename):
            try:
                copyfile(self.config.SOURCE_FILE, filename)
                self.log.info(f'The template has been created: {filename}')
            except FileNotFoundError as e:
                error = 'Unable to copy template file. Set config.APP_ROOT or check this path exists: ' + filename
                self.log.error(error)
                raise PermissionError(error) from e
        else:
            if not cmp(self.config.SOURCE_FILE, filename, shallow=False):
                msg = 'It seems another sitemap already exists. Delete it and retry: ' + filename
                self.log.error(msg)
                raise FileExistsError(msg)

    def _exclude(self) -> iter:
        """Excludes URIs in config.IGNORED from self.rules"""
        self.rules, public_uris = tee(self.rules, 2)

        if self.config.DEBUG:
            public_uris = tuple(public_uris)
            self.log.debug(f'Rules before exclusion: {len(public_uris)}')

        for item in self.config.IGNORED:
            public_uris = iter([uri for uri in public_uris if item not in uri])

        if self.config.DEBUG:
            public_uris = tuple(public_uris)
            self.log.debug(f'Rules left: {len(public_uris)}')

        return public_uris

    def _should_use_cache(self) -> bool:
        """Checks whether to use cache or to update data"""
        # app just started
        if not self.records:
            self.log.debug('Data is not ready yet')
            return False

        if self.config.CACHE_PERIOD:
            period = self.config.CACHE_PERIOD
            msg = 'CACHE_PERIOD should be a float greater than 0.0'
            assert isinstance(period, (int, float)), msg
            assert period > 0.0, msg

            hours = int(period)
            minutes = round((period - hours) * 60)
            time_to_cache = self._timestamp + timedelta(hours=hours, minutes=minutes)

            if time_to_cache < datetime.now():
                self.log.debug('Updating data cache...')
                return False

            # caching period not expired
            return True

        # caching disabled
        return False

    def _prepare_data(self):
        """Prepares data to be used by builder"""

        if not self._should_use_cache():
            dynamic_data = set()
            uris = self._exclude()

            for uri in uris:
                self.log.debug(f'Preparing Records for {uri}')
                splitted = split(r'<(\w+:)?\w+>', uri, maxsplit=1)

                if len(splitted) > 1:
                    replaced = self._replace_patterns(uri, splitted)
                    dynamic_data.update(replaced)
                else:
                    static_record = Record(
                        urljoin(self.url, uri), self.start, self.config.ALTER_CHANGES, self.config.ALTER_PRIORITY
                    )
                    dynamic_data.add(static_record)

            dynamic_data.update(self._static_data)
            default_index = Record(self.url, self.start, self.config.INDEX_CHANGES, self.config.INDEX_PRIORITY)
            dynamic_data.add(default_index)

            self._records = iter(sorted(dynamic_data, key=lambda r: len(r.loc)))
            self._timestamp = datetime.now()
            self.log.debug('Data for the sitemap is updated')

        self.log.debug('Using existing data')

    def _replace_patterns(self, uri: str, splitted: List[str]) -> List[Record]:
        """Replaces '/<converter:name>/...' with real URIs

        :param uri: a relative URL without base
        :param splitted: a list with parts of URI
        :returns a list of Records
        """

        prefix, suffix = splitted[0], splitted[-1]

        assert self._models.get(prefix), f"Your should add pattern '{uri}' or it's part to ignored or "\
                                         f"add a new rule with path '{prefix}'"

        model, attrs = self._models[prefix]
        prepared = []

        for record in eval(self.query):
            path = getattr(record, attrs['loc_attr'])
            loc = join_url_path(self.url, prefix, path, suffix)
            lastmod = None

            if attrs['lastmod_attr']:
                lastmod = getattr(record, attrs['lastmod_attr'])
                if isinstance(lastmod, datetime):
                    lastmod = get_iso_datetime(lastmod, self.config.TIMEZONE)

            prepared.append(
                Record(**get_validated(loc, lastmod, attrs['changefreq'], attrs['priority']))
            )

        self.log.debug(f'Included {len(prepared)} records')
        return prepared

    def __repr__(self):
        return f'<Sitemap object of {self.url} based on {self.app}>'
