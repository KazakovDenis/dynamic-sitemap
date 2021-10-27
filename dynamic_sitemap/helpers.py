from collections import namedtuple
from datetime import datetime
from logging import Logger
from pytz import timezone
from typing import Callable, Iterable, Iterator, Tuple, Collection, Type, List
from urllib.parse import urlparse, urljoin

from .exceptions import SitemapItemError, SitemapValidationError
from .items import SitemapItemBase


PathModel = namedtuple('PathModel', 'model attrs')
_Row = namedtuple('Row', 'slug lastmod')

_QUERIES = {
    'django': lambda model: model.objects.all(),
    'peewee': lambda model: model.select(),
    'sqlalchemy': lambda model: model.query.all(),
    'local': lambda model: model.all(),
}


class Model:
    """A class that helps you to introduce an SQL query as ORM Model

    Example:
        app = Flask(__name__)
        db = connect(DB_ADDRESS)

        def extract_posts():
            query = 'SELECT slug, updated FROM posts'
            with db.execute(query) as cursor:
                rows = cursor.fetchall()
            return iter(rows)

        post = Model(extract_posts)
        sitemap = FlaskSitemap(app, 'https://mysite.com', orm=None)
        sitemap.add_rule('/post', post, loc_attr='slug', lastmod_attr='lastmod')   # should be only 'slug' and 'lastmod'
    """

    def __init__(self, extractor: Callable[..., Iterable[Tuple[str, datetime]]]):
        self.extract = extractor

    def all(self) -> Iterator[_Row]:
        return (_Row(slug=i[0], lastmod=i[1]) for i in self.extract())


def check_url(url: str) -> str:
    """Checks URL correct"""
    if not isinstance(url, str):
        raise SitemapValidationError('URL should be a string')

    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        raise SitemapValidationError('Wrong URL. It should have a scheme and a hostname: ' + url)
    return url


def join_url_path(base_url: str, *path: str) -> str:
    """Appends parts of a path to a base_url"""
    if not path:
        return base_url

    url = urljoin(base_url, path[0])

    for part in path[1:]:
        if not url.endswith('/'):
            url += '/'
        url += part.lstrip('/')

    return url


def get_iso_datetime(dt: datetime, tz: str = None) -> str:
    """Returns the time with a timezone formatted according to W3C datetime format"""
    if tz is None:
        return dt.isoformat(timespec='seconds')

    tz = timezone(tz)
    return dt.astimezone(tz).isoformat(timespec='seconds')


def get_query(orm_name: str = None) -> Callable:
    """Returns ORM query which evaluation returning Records"""
    if orm_name is None:
        return _QUERIES['local']

    if isinstance(orm_name, str):
        orm = orm_name.casefold()
        if orm in _QUERIES:
            return _QUERIES[orm]

        raise SitemapValidationError('ORM is not supported yet: ' + orm_name)
    raise SitemapValidationError('"orm" argument should be str or None')


def set_debug_level(logger: Logger):
    """Sets up logger and its handlers levels to Debug

    :param logger: an instance of logging.Logger
    """
    logger.setLevel(10)
    for handler in logger.handlers:
        handler.setLevel(10)


def get_items(raw_data: Collection, cls: Type[SitemapItemBase], base_url: str = '') -> List[SitemapItemBase]:
    """Get prepared sitemap items from a raw data."""
    items = []

    for item in raw_data:
        if isinstance(item, dict):
            data = item
        elif isinstance(item, str):
            data = {'loc': item}
        else:
            raise SitemapItemError('Bad item', item)

        if base_url:
            data['loc'] = urljoin(base_url, data['loc'])
        items.append(cls(**data))

    return items
