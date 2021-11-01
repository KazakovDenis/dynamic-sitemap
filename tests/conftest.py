from datetime import datetime

import pytest

from dynamic_sitemap.core import DynamicSitemapBase
from dynamic_sitemap.config import SitemapConfig
from dynamic_sitemap.helpers import Model

from .utils import TEST_URL


class TestSitemap(DynamicSitemapBase):

    def _get_rules(self) -> list:
        return []

    def view(self):
        return 'response'


@pytest.fixture
def local_model():
    """Creates an instance of helpers.Model"""
    def extractor():
        return [('slug1', datetime(2020, 1, 1)), ('slug2', datetime(2020, 2, 2))]

    model = Model(extractor)
    model.slug_attr = True
    model.lastmod_attr = True
    return model


@pytest.fixture
def config():
    """Creates an instance of a basis sitemap object"""
    return SitemapConfig()


@pytest.fixture
def sitemap_cls(config):
    return TestSitemap


@pytest.fixture
def sitemap(config):
    # todo: test orm=None
    return TestSitemap(TEST_URL, config=config, orm='sqlalchemy')
