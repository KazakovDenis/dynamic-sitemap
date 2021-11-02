"""This module provides a tool to generate a Sitemap of a Flask application.

'Hello world' example:

    from flask import Flask
    from dynamic_sitemap import FlaskSitemap

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com')
    sitemap.build()

Basic example with some Models:

    from dynamic_sitemap import FlaskSitemap, ChangeFreq
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

Also you can set configurations from your class:

    class Config:
        FILENAME = 'static/sitemap.xml'
        IGNORED = {'/admin', '/back-office', '/other-pages'}
        CONTENT_PRIORITY = 0.7

    sitemap = FlaskSitemap(app, 'https://myshop.org', config=Config)
    sitemap.add_rule('/goods', Product, loc_from='id', lastmod_from='updated')
    sitemap.write()
"""
import logging
from typing import Sequence, Union, List

from ..config import ConfType
from ..core import DynamicSitemapBase
from ..exceptions import SitemapValidationError

try:
    from flask import Flask
except ImportError:
    Flask = type


logger = logging.getLogger(__name__)


class FlaskSitemap(DynamicSitemapBase):
    """A sitemap generator for a Flask application. For usage see the module documentation."""
    endpoint = 'dynamic_sitemap'
    rule = '/sitemap.xml'

    def __init__(self,
                 app: Flask,
                 base_url: str = '',
                 items: Sequence[Union[dict, str]] = (),
                 config: ConfType = None,
                 orm: str = None):
        """An instance of a Sitemap.

        :param app: an instance of Flask application
        :param base_url: a base URL such as 'http://site.com'
        :param items: list of strings or dicts to generate static sitemap items
        :param config: a class with configurations
        :param orm: an ORM name used in project
        """
        super().__init__(base_url, items, config, orm)
        self.app = app

        if orm and not app.extensions.get(orm.casefold()):
            raise SitemapValidationError(f'{orm} extension is not found')
        app.add_url_rule(self.rule, self.endpoint, self.view)

    def get_rules(self) -> List[str]:
        """Return a list of URL rules."""
        return [
            rule_obj.rule for rule_obj in self.app.url_map.iter_rules()
            if 'GET' in rule_obj.methods
        ]

    def view(self):
        """Generate a response such as Flask views do."""
        from flask import make_response, request

        self._get_items()
        response = make_response(self.render())
        response.headers['Content-Type'] = self.content_type
        logger.info(f'Sitemap requested by {request.remote_addr}')
        return response
