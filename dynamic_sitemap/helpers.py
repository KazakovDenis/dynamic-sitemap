from collections import namedtuple
from datetime import datetime
from logging import Logger
from typing import Callable, Iterable, Iterator, Tuple
from urllib.parse import urlparse


PathModel = namedtuple('PathModel', 'model attrs')
Record = namedtuple('Record', 'loc lastmod changefreq priority')
_Row = namedtuple('Row', 'slug lastmod')

_QUERIES = {
    'django': 'model.objects.all()',
    'peewee': 'model.select()',
    'sqlalchemy': 'model.query.all()',
    'local': 'model.all()',
}


def check_url(url: str) -> str:
    """Checks URL correct"""
    if not isinstance(url, str):
        raise TypeError('URL should be a string')

    parsed = urlparse(url)
    if not all([parsed.scheme, parsed.netloc]):
        raise ValueError('Wrong URL. It should have a scheme and a hostname: ' + url)
    return url


def get_query(orm_name: str = None) -> str:
    """Returns ORM query which evaluation returning Records"""
    if orm_name is None:
        return _QUERIES['local']

    if isinstance(orm_name, str):
        orm = orm_name.casefold()
        if orm in _QUERIES:
            return _QUERIES[orm]
        else:
            raise NotImplementedError('ORM is not supported yet: ' + orm_name)

    raise TypeError('"orm" argument should be str or None')


def set_debug_level(logger: Logger):
    """Sets up logger and its handlers levels to Debug

    :param logger: an instance of logging.Logger
    """
    logger.setLevel(10)
    for handler in logger.handlers:
        handler.setLevel(10)


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

    def __init__(self, extractor: Callable[[], Iterable[Tuple[str, datetime]]]):
        self.extract = extractor

    def all(self) -> Iterator[_Row]:
        return (_Row(slug=i[0], lastmod=i[1]) for i in self.extract())
