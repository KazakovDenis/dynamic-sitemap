import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Sequence, Set, Type, Union
from urllib.parse import urljoin

from . import config as conf
from . import helpers
from .exceptions import (
    SitemapIOError, SitemapItemError, SitemapValidationError,
)
from .helpers import Model, ORMModel
from .items import SitemapIndexItem, SitemapItem, SitemapItemBase
from .renderers import (
    RendererBase, SitemapIndexXMLRenderer, SitemapXMLRenderer,
)
from .validators import get_validated


logger = logging.getLogger(__name__)


class SitemapBase:
    """The base class for all sitemaps."""
    renderer_cls: Type[RendererBase]
    item_cls: Type[SitemapItemBase]

    def __init__(self, base_url: str = '', items: Sequence[Union[dict, str]] = ()):
        self.url = helpers.check_url(base_url)
        self.initial_items = list(items)
        self.initialized = False
        self.items = set()               # type: Set[Union[SitemapItem, SitemapIndexItem]]

    def render(self) -> str:
        """Get a string sitemap representation."""
        renderer = self._get_renderer()
        return renderer.render()

    def write(self, filename: str = 'sitemap.xml'):
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

    def add_items(self, *items: Union[dict, str]):
        """Add static items to a sitemap."""
        if self.initialized:
            raise SitemapItemError('Sitemap has already been initialized.')
        self.initial_items.extend(items)

    def _get_renderer(self) -> RendererBase:
        self.initialized = True
        return self.renderer_cls(self._get_items())

    def _get_items(self):
        if not self.items:
            self.items = helpers.get_items(self.initial_items, self.item_cls, self.url)
        return self.items

    def __repr__(self):
        return f'<{self.__class__.__name__} of "{self.url}">'


class SimpleSitemapIndex(SitemapBase):
    """The simple sitemap index generator."""
    renderer_cls = SitemapIndexXMLRenderer
    item_cls = SitemapIndexItem


class SimpleSitemap(SitemapBase):
    """The simple sitemap generator."""
    renderer_cls = SitemapXMLRenderer
    item_cls = SitemapItem


class ConfigurableSitemap(SimpleSitemap):
    """The class to create configurable sitemaps."""
    config = conf.SitemapConfig()
    content_type = 'application/xml'

    def __init__(self, base_url: str = '', items: Sequence[Union[dict, str]] = (), config: conf.ConfType = None):
        super().__init__(base_url, items)
        self.config.from_object(config)
        self.started_at = helpers.get_iso_datetime(datetime.now(), self.config.TIMEZONE)

    def write(self, filename: str = 'sitemap.xml'):
        if filename == 'sitemap.xml' or not filename:
            filename = self.config.FILENAME or filename
        super().write(filename)

    def ignore(self, *patterns):
        """Add URLs which would be igrnored."""
        self.config.IGNORED = set(patterns)

    def _get_items(self):
        if self.initialized:
            return self.items

        self.items = helpers.get_items(
            self.initial_items,
            self.item_cls,
            self.url,
            self.config.ALTER_CHANGES,
            self.config.ALTER_PRIORITY,
        )
        self.items.add(self._get_index())
        return self.items

    def _get_index(self):
        """Get default index page."""
        return SitemapItem(
            urljoin(self.url, '/'),
            self.started_at,
            self.config.INDEX_CHANGES,
            self.config.INDEX_PRIORITY,
        )


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
        self._rules = []                  # type: List[str]
        self._models = {}                 # type: dict
        self._dynamic_items = set()       # type: Set[SitemapItem]
        self._cached_at = datetime.now()
        self.cache_period = timedelta(0)

        if self.config.CACHE_PERIOD:
            hours = int(self.config.CACHE_PERIOD)
            minutes = round((self.config.CACHE_PERIOD - hours) * 60)
            self.cache_period = timedelta(hours=hours, minutes=minutes)

    def build(self):
        """Prepare a sitemap to be rendered or written to a file.

        Example:
            >>> from dynamic_sitemap import FrameworkSitemap
            >>>
            >>> sitemap = FrameworkSitemap(app, 'http://site.com')
            >>> sitemap.add_items('/about', '/contacts')
            >>> sitemap.build()
        """
        self._get_rules()
        self._get_items()
        self.initialized = True

    def add_rule(self,
                 path: str,
                 model: ORMModel,
                 loc_from: str,
                 lastmod_from: str = None,
                 changefreq: str = None,
                 priority: float = None):
        """Add a rule to generate urls by a template using a specified model.

        :param path: a part of URI is used to get a page generated through a model
        :param model: a model of an app that has a slug, e.g. an instance of SQLAlchemy.Model
        :param loc_from: an attribute of this model which is used to generate URL
        :param lastmod_from: an attribute of this model which is an instance of the datetime object
        :param changefreq: how often this URL changes (daily, weekly, etc.)
        :param priority: a priority of URL to be set
        """
        try:
            priority = round(priority or 0.0, 1)
        except TypeError:
            raise SitemapValidationError('Priority should be float.')
        get_validated(loc=path, changefreq=changefreq, priority=priority)

        to_check = [loc_from]
        if lastmod_from:
            to_check.append(lastmod_from)

        for attr in to_check:
            try:
                getattr(model, attr)
            except AttributeError:
                msg = f'Incorrect attribute set for the model "{model}": {attr}'
                logger.exception(msg)
                raise SitemapValidationError(msg)

        if not path.endswith('/'):
            path += '/'

        self._models[path] = helpers.PathModel(
            model=model,
            attrs={
                'loc_from': loc_from,
                'lastmod_from': lastmod_from,
                'changefreq': changefreq or self.config.CONTENT_CHANGES,
                'priority': priority or self.config.CONTENT_PRIORITY,
            },
        )

    def add_raw_rule(self, path: str, model: Model, changefreq: str = None, priority: float = None):
        """Add a rule for non-ORM project.

        :param path: a part of URI is used to get a page generated through a model
        :param model: helpers.Model with some extractor
        :param changefreq: how often this URL changes (daily, weekly, etc.)
        :param priority: a priority of URL to be set
        """
        self.add_rule(path, model, 'slug', 'lastmod', changefreq, priority)

    @abstractmethod
    def view(self, *args, **kwargs):
        """The method to override. Should return HTTP response."""

    def _get_items(self):
        dynamic_items = self._get_dynamic_items()
        static_items = super()._get_items()
        self.items = dynamic_items ^ static_items
        return self.items

    def _get_dynamic_items(self):
        """Prepares data to be used by renderer."""
        if self._should_use_cache():
            logger.debug('Using existing data')
            return self._dynamic_items

        self._dynamic_items.clear()

        for rule in self._without_ignored():
            logger.debug(f'Preparing items for {rule}')
            splitted = RULE_EXP.split(rule, maxsplit=1)
            replaced = self._replace_patterns(rule, splitted)
            self._dynamic_items.update(replaced)

        return self._dynamic_items

    def _should_use_cache(self) -> bool:
        """Checks whether to use cache or to update data"""
        if not self.items:
            logger.debug('Data is not ready yet')
            return False

        if (self._cached_at + self.cache_period) < datetime.now():
            logger.debug('Updating sitemap cache')
            return False

        logger.debug('Using sitemap cache')
        return True

    def _get_rules(self) -> list:
        """The method to override. Should return a list of URL rules."""
        if not self._rules:
            self._rules = []
        return self._rules

    def _without_ignored(self) -> list:
        """Excludes URIs in config.IGNORED from self.rules"""
        paths = self._rules
        for ignored in self.config.IGNORED:
            paths = list(filter(lambda x: not x.startswith(ignored), paths))
        return paths

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
