"""
This package provides tools to generate a Sitemap according
to the protocol https://www.sitemaps.org/protocol.html.

Already implemented:
- metaclass SitemapMeta
- Flask (FlaskSitemap)

'Hello world' example:

    from dynamic_sitemap import FlaskSitemap
    from flask import Flask

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com')
    sitemap.build()

Basic example with some Models:

    from dynamic_sitemap import FrameworkSitemap
    from flask import Flask
    from models import Post, Tag

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com', orm='sqlalchemy')
    sitemap.config.IGNORED.update(['/edit', '/upload'])
    sitemap.config.ALTER_PRIORITY = 0.1
    sitemap.add_items(['/faq', {'loc': '/about', 'priority': 0.7}])
    sitemap.add_rule('/blog', Post, lastmod_from='created', priority=1.0)
    sitemap.add_rule('/blog/tag', Tag, changefreq=ChangeFreq.DAILY.value)
    sitemap.build()

IGNORED has a priority over add_rule. Also you can set configurations from your class:

    class Config:
        FILENAME = 'static/sitemap.xml'
        IGNORED = {'/admin', '/back-office', '/other-pages'}
        CONTENT_PRIORITY = 0.7

    sitemap = FlaskSitemap(app, 'https://myshop.org', config=Config)
    sitemap.add_rule('/goods', Product, loc_attr='id', lastmod_attr='updated')
    sitemap.write()
"""
import logging
import re
from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from typing import List, Sequence, Type, Union
from urllib.parse import urljoin

from . import config as conf, helpers
from .exceptions import SitemapIOError, SitemapItemError, SitemapValidationError
from .items import SitemapItem, SitemapIndexItem, SitemapItemBase
from .renderers import SitemapXMLRenderer, RendererBase, SitemapIndexXMLRenderer
from .validators import get_validated


logger = logging.getLogger(__name__)


class SitemapBase:
    """The base class for all sitemaps."""
    renderer_cls: Type[RendererBase]
    item_cls: Type[SitemapItemBase]

    def __init__(self, base_url: str = '', items: Sequence[Union[dict, str]] = ()):
        self.url = helpers.check_url(base_url)
        self.initial_items = list(items)
        self.items = []

    def render(self) -> str:
        """Get a string sitemap representation."""
        renderer = self._get_renderer()
        return renderer.render()

    def write(self, filename: str):
        """Write a sitemap to a file."""
        renderer = self._get_renderer()
        try:
            renderer.write(filename)
        except FileNotFoundError:
            error = f'Path "{filename}" is not found or credentials required.'
            logger.exception(error)
            raise SitemapIOError(error)
        else:
            logger.info('Static sitemap is ready: %s', filename)

    def add_items(self, items: Sequence[Union[dict, str]]):
        """Add static items to a sitemap."""
        if self.items:
            raise SitemapItemError('Sitemap has already been initialized.')
        self.initial_items.extend(items)

    def _get_renderer(self) -> RendererBase:
        return self.renderer_cls(self._get_items())

    def _get_items(self):
        if not self.items:
            self.items = helpers.get_items(self.initial_items, self.item_cls, self.url)
        return self.items

    def __repr__(self):
        return f'<{self.__class__.__name__} of "{self.url}">'


class SimpleSitemapIndex(SitemapBase):
    renderer_cls = SitemapIndexXMLRenderer
    item_cls = SitemapIndexItem


class SimpleSitemap(SitemapBase):
    renderer_cls = SitemapXMLRenderer
    item_cls = SitemapItem


class ConfigurableSitemap(SimpleSitemap):
    config = conf.SitemapConfig()
    content_type = 'application/xml'

    def __init__(self, base_url: str = '', items: Sequence[Union[dict, str]] = (), config: conf.ConfType = None):
        super().__init__(base_url, items)
        self.config.from_object(config)

    def write(self, filename: str = ''):
        super().write(filename or self.config.FILENAME)


RULE_EXP = re.compile(r'<(\w+:)?\w+>')


class DynamicSitemapBase(ConfigurableSitemap, ABC):

    def __init__(self,
                 base_url: str = '',
                 items: Sequence[Union[dict, str]] = (),
                 config: conf.ConfType = None,
                 orm: str = None):
        """An instance of a Sitemap.

        :param base_url: base URL such as 'http://site.com'
        :param items: list of strings or dicts to generate static sitemap items
        :param config: a class with configurations
        :param orm: an ORM name used in project (use 'local' and check helpers.Model out for raw SQL queries)
        """
        super().__init__(base_url, items, config)
        self.fetch = helpers.get_query(orm)
        self.start = None
        self.rules = None
        self._models = {}
        self._cached_at = datetime.now()

    def build(self):
        """Prepare a sitemap to be rendered or written to a file.

        Example:
            sitemap = FrameworkSitemap(app, 'http://site.com')
            sitemap.add_items(['/about', '/contacts'])
            sitemap.build()
        """
        self.start = helpers.get_iso_datetime(datetime.now(), self.config.TIMEZONE)
        self.rules = self.get_rules()
        self._get_items()

    def add_rule(self,
                 path: str,
                 model: type,
                 loc_from: str,
                 lastmod_from: str = None,
                 changefreq: str = None,
                 priority: float = None):
        """Add a rule to generate urls by a template using models of an app.

        :param path: a part of URI is used to get a page generated through a model
        :param model: a model of an app that has a slug, e.g. an instance of SQLAlchemy.Model
        :param loc_from: an attribute of this model which is used to generate URL
        :param lastmod_from: an attribute of this model which is an instance of the datetime object
        :param changefreq: how often this URL changes (daily, weekly, etc.)
        :param priority: a priority of URL to be set
        """
        priority = round(priority or 0.0, 1)
        get_validated(loc=path, changefreq=changefreq, priority=priority)

        for attr in (loc_from, lastmod_from if lastmod_from else loc_from,):
            try:
                getattr(model, attr)
            except AttributeError:
                msg = (
                    f'Incorrect attributes are set for the model "{model}" in add_rule():\n'
                    f'loc_from = {loc_from} and/or lastmod_from = {lastmod_from}'
                )
                logger.exception(msg)
                raise SitemapValidationError(msg)

        if not path.endswith('/'):
            path += '/'

        self._models[path] = helpers.PathModel(
            model=model,
            attrs={
                'loc_from': loc_from,
                'lastmod_from':  lastmod_from,
                'changefreq': changefreq or self.config.CONTENT_CHANGES,
                'priority':  priority or self.config.CONTENT_PRIORITY,
            }
        )

    @abstractmethod
    def get_rules(self) -> list:
        """The method to override. Should return a list of URL rules."""

    @abstractmethod
    def view(self, *args, **kwargs):
        """The method to override. Should return HTTP response."""

    def get_dynamic_rules(self) -> list:
        """Return all urls should be added as a rule or to ignored list."""
        return [i for i in self.rules if RULE_EXP.search(i)]

    def _get_items(self):
        """Prepares data to be used by renderer."""
        if self._should_use_cache():
            logger.debug('Using existing data')
            return

        dynamic_data = set()
        uris = self._exclude()

        for uri in uris:
            logger.debug(f'Preparing Records for {uri}')
            splitted = RULE_EXP.split(uri, maxsplit=1)

            if len(splitted) > 1:
                replaced = self._replace_patterns(uri, splitted)
                dynamic_data.update(replaced)
            else:
                static_record = SitemapItem(
                    urljoin(self.url, uri), self.start, self.config.ALTER_CHANGES, self.config.ALTER_PRIORITY
                )
                dynamic_data.add(static_record)

        static_data = super()._get_items()
        dynamic_data.update(static_data)
        dynamic_data.add(self._get_index())

        self.items = iter(sorted(dynamic_data, key=lambda r: r.loc))
        self._cached_at = datetime.now()
        logger.debug('Data for the sitemap is updated')
        return self.items

    def _should_use_cache(self) -> bool:
        """Checks whether to use cache or to update data"""
        if not self.items:
            logger.debug('Data is not ready yet')
            return False

        if not self.config.CACHE_PERIOD:
            # caching disabled
            return False

        hours = int(self.config.CACHE_PERIOD)
        minutes = round((self.config.CACHE_PERIOD - hours) * 60)
        time_to_cache = self._cached_at + timedelta(hours=hours, minutes=minutes)

        if time_to_cache < datetime.now():
            logger.debug('Updating data cache...')
            return False

        return True

    def _exclude(self) -> list:
        """Excludes URIs in config.IGNORED from self.rules"""
        public_uris = self.rules
        for item in self.config.IGNORED:
            public_uris = filter(lambda x: not x.startswith(item), public_uris)
        return list(public_uris)

    def _replace_patterns(self, uri: str, splitted: List[str]) -> List[SitemapItem]:
        """Replaces '/<converter:name>/...' with real URIs

        :param uri: a relative URL without base
        :param splitted: a list with parts of URI
        :returns a list of Records
        """

        prefix, suffix = splitted[0], splitted[-1]

        if not self._models.get(prefix):
            raise SitemapValidationError(
                f"Add pattern '{uri}' or it's part to ignored or add a new rule with a path '{prefix}'",
            )

        model, attrs = self._models[prefix]
        prepared = []

        for record in self.fetch(model):
            path = getattr(record, attrs['loc_from'])
            loc = helpers.join_url_path(self.url, prefix, path, suffix)
            lastmod = None

            if attrs['lastmod_from']:
                lastmod = getattr(record, attrs['lastmod_from'])
                if isinstance(lastmod, datetime):
                    lastmod = helpers.get_iso_datetime(lastmod, self.config.TIMEZONE)

            item = SitemapItem(loc, lastmod, attrs['changefreq'], attrs['priority'])
            prepared.append(item)

        logger.debug(f'Included {len(prepared)} items')
        return prepared

    def _get_index(self):
        """Get default index page."""
        url = urljoin(self.url, '/')
        return SitemapItem(url, self.start, self.config.INDEX_CHANGES, self.config.INDEX_PRIORITY)
