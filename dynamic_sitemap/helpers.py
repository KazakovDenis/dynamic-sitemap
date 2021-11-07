from collections import namedtuple
from datetime import datetime
from typing import (
    Callable, Collection, Iterable, Iterator, Optional, Set, Tuple, Type,
)
from urllib.parse import urljoin, urlparse

from pytz import timezone

from .exceptions import SitemapItemError, SitemapValidationError
from .items import SitemapItemBase


PathModel = namedtuple('PathModel', 'model attrs')
_Row = namedtuple('_Row', 'slug lastmod')

_QUERIES = {
    'django': lambda model: model.objects.all(),
    'peewee': lambda model: model.select(),
    'sqlalchemy': lambda model: model.query.all(),
    'local': lambda model: model.all(),
}


class ORMModel:
    """Just the mock representing models of different ORMs."""


Extractor = Callable[..., Iterable[Tuple[str, datetime]]]


class Model(ORMModel):
    """The class to use instead of ORM models.
    Used with ``add_raw_rule``.

    :param extractor: a function that fetches loc & lastmod from a database.

    Example:
        >>> from flask import Flask
        >>> from db import connect
        >>>
        >>> app = Flask(__name__)
        >>> db = connect(DB_ADDRESS)
        >>>
        >>> def extract_posts():
        >>>     query = 'SELECT slug, updated FROM posts;'
        >>>     with db.execute(query) as cursor:
        >>>         rows = cursor.fetchall()
        >>>     return iter(rows)
        >>>
        >>> post = Model(extract_posts)
        >>> sitemap = FlaskSitemap(app, 'https://site.com')
        >>> sitemap.add_raw_rule('/posts/', post)
    """
    slug = lastmod = True

    def __init__(self, extractor: Extractor):
        self.extract = extractor

    def all(self) -> Iterator[_Row]:     # noqa: A003
        return (_Row(slug=i[0], lastmod=i[1]) for i in self.extract())


def check_url(url: str) -> str:
    """Check URL correct."""
    if not isinstance(url, str):
        raise SitemapValidationError('URL should be a string')

    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        raise SitemapValidationError('Wrong URL. It should have a scheme and a hostname: ' + url)
    return url


def join_url_path(base_url: str, *path: str) -> str:
    """Append parts of a path to a base_url."""
    if not path:
        return base_url

    url = urljoin(base_url, path[0])

    for part in path[1:]:
        if not url.endswith('/'):
            url += '/'
        url += part.lstrip('/')

    return url


def get_iso_datetime(dt: datetime, tz: str = None) -> str:
    """Return the time with a timezone formatted according to W3C datetime format."""
    if tz is None:
        return dt.isoformat(timespec='seconds')

    zone = timezone(tz)    # type: ignore
    return dt.astimezone(zone).isoformat(timespec='seconds')


def get_query(orm_name: str = None) -> Callable:
    """Return ORM query which evaluation returning Records."""
    if orm_name is None:
        return _QUERIES['local']

    if isinstance(orm_name, str):
        orm = orm_name.casefold()
        if orm in _QUERIES:
            return _QUERIES[orm]

        raise SitemapValidationError('ORM is not supported yet: ' + orm_name)
    raise SitemapValidationError('"orm" argument should be str or None')


def get_items(raw_data: Collection,
              cls: Type[SitemapItemBase],
              base_url: str = '',
              default_changefreq: Optional[str] = None,
              default_priority: Optional[float] = None,
              ) -> Set[SitemapItemBase]:
    """Get prepared sitemap items from a raw data."""
    items = set()

    for item in raw_data:
        if isinstance(item, dict):
            data = item
        elif isinstance(item, str):    # noqa: SIM106
            data = {'loc': item}
        else:
            raise SitemapItemError('Bad item', item)

        data.setdefault('changefreq', default_changefreq)
        data.setdefault('priority', default_priority)

        if base_url:
            data['loc'] = urljoin(base_url, data['loc'])
        items.add(cls(**data))

    return items
