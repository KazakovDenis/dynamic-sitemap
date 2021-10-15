import os
import pytest

from dynamic_sitemap.core import DynamicSitemapBase
from dynamic_sitemap.config import SitemapConfig
from dynamic_sitemap.helpers import *

from .utils import DEFAULT_URLS, TEST_FOLDER, TEST_URL


class TestSitemap(DynamicSitemapBase):

    def get_rules(self):
        return list(DEFAULT_URLS)

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
def default_map(config):
    """Creates an instance of a basis sitemap object"""
    # todo: test orm=None
    return TestSitemap(TEST_URL, config=config, orm='sqlalchemy')


@pytest.fixture(scope='module', autouse=True)
def teardown_module():
    yield
    for file in os.listdir(TEST_FOLDER):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join(TEST_FOLDER, file))
