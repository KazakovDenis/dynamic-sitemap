from collections import namedtuple
from typing import Callable


PathModel = namedtuple('PathModel', 'model attrs')
Record = namedtuple('Record', 'loc lastmod priority')
_Row = namedtuple('Row', 'slug lastmod')


def set_debug_level(logger):
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
        sitemap = FlaskSitemap(app, 'https://mysite.com')
        sitemap.add_rule('/post', post, slug='slug', lastmod='lastmod')    # should be only 'slug' and 'lastmod'

    """

    def __init__(self, extractor: Callable):
        self.extract = extractor

    def all(self):
        return iter(_Row(slug=i[0], lastmod=i[1]) for i in self.extract())
