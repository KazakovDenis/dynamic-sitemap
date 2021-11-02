"""This package provides tools to generate a Sitemap according
to the protocol https://www.sitemaps.org/protocol.html.

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
    sitemap.config.ALTER_PRIORITY = 0.1
    sitemap.ignore('/edit', '/upload')
    sitemap.add_items('/faq', {'loc': '/about', 'priority': 0.7})
    sitemap.add_rule('/blog', Post, lastmod_from='created', priority=1.0)
    sitemap.add_rule('/blog/tag', Tag, changefreq=ChangeFreq.DAILY.value)
    sitemap.build()

IGNORED has a priority over add_rule. Also you can set configurations from your class:

    class Config:
        FILENAME = 'static/sitemap.xml'
        IGNORED = {'/admin', '/back-office', '/other-pages'}
        CONTENT_PRIORITY = 0.7

    sitemap = FlaskSitemap(app, 'https://myshop.org', config=Config)
    sitemap.add_rule('/goods', Product, loc_from='id', lastmod_from='updated')
    sitemap.write()
"""
from .config import SitemapConfig
from .contrib.flask import FlaskSitemap
from .core import SimpleSitemap, SimpleSitemapIndex
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
