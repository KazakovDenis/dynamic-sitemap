# -*- coding: utf-8 -*-
"""
This module provides a tool to generate a Sitemap of an application.
"""
# TODO: Module is not ready
from .main import *


DjangoApp = TypeVar('DjangoApp')


class DjangoSitemap(SitemapMeta):
    """A sitemap generator for a Django application"""

    def __init__(self, app: DjangoApp, base_url: str, config_obj=None):
        """Creates an instance of a Sitemap

        :param app: an instance of Django application
        :param base_url: your base URL such as 'http://site/com'
        :param config_obj: a class with configurations
        """
        super().__init__(app, base_url, config_obj)

        if not self.log:
            self.log = self.app.logger.getChild('sitemap')
        if self.config.DEBUG:
            self.set_debug_level()

        self.query = self.queries['django']

        self.template_folder = self.config.TEMPLATE_FOLDER    # or self.app.template_folder

        self._copy_template(self.template_folder)
        self.log.info(f'Sitemap has been initialized')

    def view(self):
        # import django
        self._prepare_data()
        self.log.info(f'["request.method"] Requested by "request.remote_add"')
        pass
