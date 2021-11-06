from datetime import datetime

import pytest

from dynamic_sitemap.config import SitemapConfig
from dynamic_sitemap.helpers import Model

from .utils import TEST_URL, SitemapMock


@pytest.fixture
def local_model():
    def extractor():
        return [('slug1', datetime(2020, 1, 1)), ('slug2', datetime(2020, 2, 2))]

    model = Model(extractor)
    model.slug_attr = True
    model.lastmod_attr = True
    return model


@pytest.fixture
def config():
    return SitemapConfig()


@pytest.fixture
def sitemap_cls(config):
    return SitemapMock


@pytest.fixture
def sitemap(config):
    return SitemapMock(TEST_URL, config=config, orm='sqlalchemy')
