"""This package provides tools to generate a Sitemap according
to the protocol https://www.sitemaps.org/protocol.html.

'Hello world' example:

    from dynamic_sitemap import FlaskSitemap
    from flask import Flask

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com')
    sitemap.build()

Basic example with some Models:

    from dynamic_sitemap import ChangeFreq, FlaskSitemap
    from flask import Flask
    from models import Post, Tag

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com', orm='sqlalchemy')
    sitemap.config.ALTER_PRIORITY = 0.1
    sitemap.ignore('/edit', '/upload')
    sitemap.add_items('/faq', {'loc': '/about', 'priority': 0.7})
    sitemap.add_rule('/blog', Post, loc_from='slug', priority=1.0)
    sitemap.add_rule('/blog/tag', Tag, loc_from='id', changefreq=ChangeFreq.DAILY.value)
    sitemap.build()

Also you can set configurations from your class:

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
__about__ = {
    'title': 'dynamic-sitemap',
    'module': __package__,
    'version': '1.0.0a1',
    'url': 'https://github.com/KazakovDenis/dynamic-sitemap',
    'author': __author__,
    'email': 'denis@kazakov.ru.net',
    'license': 'MIT',
    'copyright': f'Copyright 2020 {__author__}',
}
