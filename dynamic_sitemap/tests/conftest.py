from datetime import datetime
import os

import pytest

from .. import *
from ..helpers import Model
from .mocks import *


PY_TYPES = int, float, complex, tuple, list, set, dict, str, bytes, bytearray
FALSE_INSTANCES = (py_type() for py_type in PY_TYPES)
TRUE_INSTANCES = 1, 1.0, 1+1j, (1,), [1], {1}, {1: 1}, 'str', b'bytes', bytearray(b'array')

TEST_TIME = datetime.now()
TEST_URL = 'http://site.com'
TEST_FOLDER = os.path.join(EXTENSION_ROOT, 'tests', 'tmp')
TEST_FILE = os.path.join(TEST_FOLDER, 'sitemap.xml')
os.makedirs(TEST_FOLDER, exist_ok=True)

STATIC_URLS = '/', '/url', '/ign'
DYNAMIC_URLS = '/ign/<slug>', '/api/<int:page>', '/blog/<str:title>'
DEFAULT_URLS = STATIC_URLS + DYNAMIC_URLS


class DefaultSitemap(SitemapMeta):
    def __init__(self, app, base_url: str, config_obj=None):
        super().__init__(app, base_url, config_obj)

    def get_rules(self):
        # todo: change to DEFAULT and make tests
        return iter(STATIC_URLS)

    def view(self):
        return 'response'


record = Mock('slug', 'updated', 'priority')
rule = Mock(methods=['GET'], rule='/url')


class ORMModel:
    # for SQLAlchemy, DjangoORM
    query = objects = Mock(
        all=lambda: [
            record(slug='first-slug', updated=TEST_TIME),
            record(slug='second-slug', updated=TEST_TIME)
        ]
    )

    # for Peewee
    @classmethod
    def select(cls):
        return getattr(cls.query, 'all')()


@pytest.fixture
def local_model():
    """Creates an instance of helpers.Model"""
    def extractor():
        return [('slug1', datetime(2020, 1, 1)), ('slug2', datetime(2020, 2, 2))]
    return Model(extractor)


@pytest.fixture
def config():
    """Creates an instance of a basis sitemap object"""
    config = SitemapConfig()
    config.TEMPLATE_FOLDER = TEST_FOLDER
    return config


@pytest.fixture
def default_map(config):
    """Creates an instance of a basis sitemap object"""
    return DefaultSitemap(Mock, TEST_URL, config_obj=config)


def teardown_module():
    for file in os.listdir(TEST_FOLDER):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join(TEST_FOLDER, file))
