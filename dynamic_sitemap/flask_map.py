# -*- coding: utf-8 -*-
"""
This module provides a tool to generate a Sitemap of a Flask application.

'Hello world' example:

    from flask import Flask
    from dynamic_sitemap import FlaskSitemap

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com')
    sitemap.update()

Basic example with some Models:

    from flask import Flask
    from dynamic_sitemap import FlaskSitemap
    from models import Post, Tag

    app = Flask(__name__)
    sitemap = FlaskSitemap(app, 'https://mysite.com', orm='sqlalchemy')
    sitemap.config.IGNORED.update(['/edit', '/upload'])
    sitemap.config.ALTER_PRIORITY = 0.1
    sitemap.update()
    sitemap.add_elem('/faq', changefreq='monthly', priority=0.4)
    sitemap.add_rule('/blog', Post, lastmod_attr='created', priority=1.0)
    sitemap.add_rule('/blog/tag', Tag, changefreq='daily')

IGNORED has a priority over add_rule. Also you can set configurations from your class:

    sm_logger = logging.getLogger('sitemap')
    sm_logger.setLevel(30)

    class Config:
        STATIC_FOLDER = ('public',)
        IGNORED = {'/admin', '/back-office', '/other-pages'}
        CONTENT_PRIORITY = 0.7
        LOGGER = sm_logger

    sitemap = FlaskSitemap(app, 'https://myshop.org', config_obj=Config)
    sitemap.add_rule('/goods', Product, loc_attr='id', lastmod_attr='updated')

Moreover you can get a static file by using:
    sitemap.build_static()
"""
from .main import *


FlaskApp = TypeVar('Flask')


class FlaskSitemap(SitemapMeta):
    """A sitemap generator for a Flask application. For usage see the module documentation"""

    def __init__(self, app: FlaskApp, base_url: str, config_obj: ConfType = None, orm: str = None):
        """Creates an instance of a Sitemap

        :param app: an instance of Flask application
        :param base_url: your base URL such as 'http://site.com'
        :param config_obj: a class with configurations
        :param orm: an ORM name used in project
        """
        if orm:
            assert app.extensions.get(orm), f'{orm} extension is not found'
        self.config.LOGGER = app.logger.getChild('sitemap')
        self.config.TEMPLATE_FOLDER = join(app.root_path, app.template_folder)
        super().__init__(app, base_url, config_obj, orm)
        app.add_url_rule('/sitemap.xml', endpoint='dynamic_sitemap', view_func=self.view)

    def get_rules(self) -> iter:
        """Returns an iterator of URL rules"""
        rules = [rule_obj.rule for rule_obj in self.app.url_map.iter_rules() if 'GET' in rule_obj.methods]
        rules.sort(key=len)
        return iter(rules)

    def view(self):
        """Generates a response such as Flask views do"""
        from flask import make_response, render_template, request

        self._prepare_data()
        template = render_template('sitemap.xml', data=self._dynamic_data)
        response = make_response(template)
        response.headers['Content-Type'] = self.content_type
        self.log.info(f'[{request.method}] Sitemap requested by {request.remote_addr}')
        return response
