# -*- coding: utf-8 -*-
"""
This package provides tools to generate a Sitemap of an application.

Already implemented:
- Flask

Basic example:

    from flask import Flask
    from sitemap_ext import FlaskSitemap

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com')
    sitemap.config.IGNORED.extend(['/edit', '/upload'])
    sitemap.config.TEMPLATE_FOLDER = ['app', 'templates']
    sitemap.update()
    sitemap.add_rule('/app', Post, lastmod='created')
    sitemap.add_rule('/app/tag', Tag, priority=0.4)

IGNORED has a priority over add_rule. Also you can set configurations from your class:

    sm_logger = logging.getLogger('sitemap')
    sm_logger.setLevel(30)

    class Config:
        TEMPLATE_FOLDER = ['app', 'templates']
        IGNORED = ['/admin', '/back-office', '/other-pages']
        ALTER_PRIORITY = 0.1
        LOGGER = sm_logger

    sitemap = FlaskSitemap(app, 'https://myshop.org', config_obj=Config)
    sitemap.add_rule('/goods', Product, slug='id', lastmod='updated')

Moreover you can get a static file by using:
    sitemap.build_static()
"""
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from datetime import datetime
from filecmp import cmp
from itertools import tee
from logging import getLogger
from os.path import abspath, join, exists
from re import search, split
from shutil import copyfile
from typing import TypeVar
from xml.etree import ElementTree as ET

from .helpers import set_debug_level


EXTENSION_ROOT = abspath(__file__).rsplit('/', 1)[0]
Record = namedtuple('Record', 'loc lastmod priority')
HTTPResponse = TypeVar('HTTPResponse')

QUERIES = {
    'django': 'model.objects.all()',
    'peewee': 'model.select()',
    'sqlalchemy': 'model.query.all()',
}

XML_ATTRS = {
    'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xsi:schemaLocation':
        'http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd'
}


class SitemapConfig:
    """A class to set configurations

    DEBUG - if True sets up logging to DEBUG level
    STATIC_FOLDER - a str or a collection of folders to make path where to put a STATIC sitemap.xml,
    TEMPLATE_FOLDER - where to put a template for a dynamic sitemap, a tuple of folders
        folders examples:
            STATIC_FOLDER = os.path.join('app', 'static')
            TEMPLATE_FOLDER = ['app', 'templates']
    IGNORED - a list of strings which ignored URIs contain
    INDEX_PRIORITY - float, a priority of the index page
    CONTENT_PRIORITY - float, a priority of pages generated by models
    ALTER_PRIORITY - float, a priority of other pages
    LOGGER - an instance of logging.Logger, creates child of app.logger if not set
    """

    DEBUG = False
    SOURCE_FILE = join(EXTENSION_ROOT, 'templates', 'jinja2.xml')
    STATIC_FOLDER = TEMPLATE_FOLDER = None
    IGNORED = ['/admin', '/static', ]
    INDEX_PRIORITY = CONTENT_PRIORITY = ALTER_PRIORITY = None
    LOGGER = None

    def from_object(self, obj: (type, 'SitemapConfig')):
        """Updates values from the given object

        :param obj: a class with the same attributes as this one or it's instance
        """
        if isinstance(obj, type) or isinstance(obj, type(self)):
            for key in dir(obj):
                if key.isupper():
                    self[key] = getattr(obj, key)
        else:
            raise NotImplementedError('This type of object is not supported yet')

    def __set__(self, instance, value):
        raise PermissionError(
            'You could not change configuration this way. Use "from_object" method or set specific attribute'
        )

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        return self.__dict__.get(item)

    def __repr__(self):
        return '<Sitemap configurations object>'


class SitemapMeta(metaclass=ABCMeta):
    """The base class to inherit"""

    config = SitemapConfig()

    def __init__(self, app, base_url: str, config_obj=None, orm: str = 'sqlalchemy'):
        """Creates an instance of a Sitemap

        :param app: an application instance
        :param base_url: your base URL such as 'http://site.com'
        :param config_obj: a class with configurations
        :param orm: an ORM name used in project
        """

        self.app = app
        self.url = base_url
        self.start = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        self.query = QUERIES[orm.casefold()]    # a query to get all objects of a model
        self.rules = None
        self.log = None

        # containers
        self.data = []                               # to store Record instances
        self.models = {}                             # to store db objects added by add_rule

        self.update(config_obj)

    def add_rule(self, path: str, model, slug='slug', lastmod: str = None, priority: float = None):
        """Adds a rule to the builder to generate urls by a template using models of an app

        :param path: a part of URI is used to get a page generated through a model
        :param model: a model of an app that has a slug, e.g. an instance of SQLAlchemy.Model
        :param slug: a slug attribute of this model
        :param lastmod: an attribute of this model which is an instance of the datetime object
        :param priority: a priority of URL to be set
        """
        if priority:
            priority = round(priority or self.config.CONTENT_PRIORITY, 1)
            assert 0.0 < priority <= 1.0, 'Priority should be a float between 0.0 and 1.0'

        self.models[path] = model, slug, lastmod, priority

    def build_static(self, filename='sitemap.xml'):
        """Builds an XML file. The system user of the app should have rights to write files

        :param filename: the name of target file (without path)
        """
        self._prepare_data()

        folder = self.config.STATIC_FOLDER
        fullname = filename if not isinstance(folder, str) else join(*folder, filename)
        self.log.info(f'Creating {fullname}...')

        url_set = ET.Element('urlset', XML_ATTRS)
        sub = ET.SubElement

        for record in self.data:
            url = sub(url_set, "url")
            sub(url, "loc").text = record.loc

            if record.lastmod:
                sub(url, "lastmod").text = record.lastmod

            if record.priority:
                sub(url, "priority").text = str(record.priority)

        tree = ET.ElementTree(url_set)
        try:
            tree.write(fullname, xml_declaration=True, encoding='UTF-8')
        except FileNotFoundError as e:
            error = f'Seems like {fullname} is not found or credentials required.'
            self.log.error(error)
            raise Exception(error) from e

        self.log.info('Static sitemap is ready')

    def update(self, config_obj=None):
        """Updates its config and rules"""
        if config_obj:
            self.config.from_object(config_obj)

        self.log = self.get_logger()
        self.rules = self.get_rules()
        self._copy_template()

    def get_logger(self):
        """Returns an instance of logging.Logger (set in config)"""
        logger = self.config.LOGGER if self.config.LOGGER else getLogger('sitemap')
        if self.config.DEBUG and logger:
            set_debug_level(logger)
        return logger

    def get_dynamic_rules(self) -> list:
        """Returns alls url should be added as a rule or to ignored list"""
        self.rules, all_rules = tee(self.rules)
        return [i for i in all_rules if search(r'<[\w:]+>', i)]

    @abstractmethod
    def get_rules(self) -> iter:
        """The method to override. Should return an iterator of URL rules"""
        pass

    @abstractmethod
    def view(self) -> HTTPResponse:
        """The method to override. Should return HTTP response"""
        pass

    def _copy_template(self):
        """Copies an xml file with Jinja2 template to an app templates directory

        :raises:
            PermissionError: if unable to copy a template to destination
            FileExistsError: if another sitemap already exists
        """
        root = abspath(self.app.__module__).rsplit('/', 1)[0]
        folder = self.config.TEMPLATE_FOLDER
        path = folder if isinstance(folder, str) else join(*folder)
        filename = join(root, path, 'sitemap.xml')

        if not exists(filename):
            try:
                copyfile(self.config.SOURCE_FILE, filename)
                self.log.info(f'The template has been created: {filename}')
            except FileNotFoundError as e:
                error = 'Unable to place file at this path: ' + filename
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

    def _prepare_data(self):
        """Prepares data to be used by builder"""
        self.data.clear()
        self.data.append(Record(self.url, self.start, self.config.INDEX_PRIORITY))
        uris = self._exclude()

        for uri in uris:
            self.log.debug(f'Preparing Records for {uri}')
            splitted = split(r'/<[\w:]+>', uri, maxsplit=1)

            if len(splitted) > 1:
                replaced = self._replace_patterns(uri, splitted)
                self.data.extend(replaced)
            else:
                self.data.append(Record(self.url + uri, self.start, self.config.ALTER_PRIORITY))

        self.log.debug('Data for the sitemap is ready')

    def _replace_patterns(self, uri: str, splitted: list) -> list:
        """Replaces '/<converter:name>/...' with real URIs

        :param uri: a relative URL without base
        :param splitted: a list with parts of URI
        :returns a list of Records
        """

        prefix, suffix = splitted[0], splitted[-1]

        assert self.models.get(prefix), f"Your should add '{uri}' or it's part to ignored or "\
                                        f"add a new rule with path '{prefix}'"

        model, slug, updated, priority = self.models.get(prefix)
        prepared = []

        try:
            for record in eval(self.query):
                uri = '/' + getattr(record, slug) if slug else ''
                loc = f'{self.url}{prefix}{uri}{suffix}'

                if updated:
                    lastmod = getattr(record, updated)
                    if isinstance(lastmod, datetime):
                        lastmod = lastmod.strftime('%Y-%m-%dT%H:%M:%S')
                else:
                    lastmod = None

                prepared.append(Record(loc, lastmod, priority))
        except AttributeError:
            self.log.warning(f'{model} has no attributes: {slug} and/or {updated}')

        self.log.debug(f'Included {len(prepared)} records')
        return prepared

    def __repr__(self):
        return f'<Sitemap object of {self.url} based on {self.app} >'
