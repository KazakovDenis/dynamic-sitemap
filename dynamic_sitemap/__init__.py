from .config import SitemapConfig
from .main import SitemapMeta, SimpleSitemap, SimpleSitemapIndex
from .flask_map import FlaskSitemap
from .validators import ChangeFreq


__author__ = 'Denis Kazakov'
__about__ = dict(
    __title__='dynamic-sitemap',
    __module__=__package__,
    __version__='0.2.0a',
    __url__='https://github.com/KazakovDenis/dynamic-sitemap',

    __author__=__author__,
    __email__='denis@kazakov.ru.net',

    __license__='MIT',
    __copyright__=f'Copyright 2020 {__author__}',
)
