import os
import pytest

from dynamic_sitemap import *
from dynamic_sitemap.config import EXTENSION_ROOT
from dynamic_sitemap.helpers import *
from .mocks import *


PY_TYPES = int, float, complex, tuple, list, set, dict, str, bytes, bytearray
FALSE_INSTANCES = (py_type() for py_type in PY_TYPES)
TRUE_INSTANCES = 1, 1.0, 1+1j, (1,), [1], {1}, {1: 1}, 'str', b'bytes', bytearray(b'array')

TEST_URL = 'http://site.com'
TEST_TIME = datetime.now()
TEST_DATE_STR = TEST_TIME.strftime('%Y-%m-%dT')
TEST_TIME_STR = TEST_TIME.strftime('%Y-%m-%dT%H:%M:%S')
TEST_FOLDER = os.path.join(EXTENSION_ROOT, 'tmp')
TEST_FILE = os.path.join(TEST_FOLDER, 'sitemap.xml')
WRONG_FOLDER = os.path.join(TEST_FOLDER, 'no_such_dir')
os.makedirs(TEST_FOLDER, exist_ok=True)

STATIC_URLS = '/', '/url', '/ign'
DYNAMIC_URLS = '/ign/<slug>', '/api/<int:page>', '/blog/<str:title>'
DEFAULT_URLS = STATIC_URLS + DYNAMIC_URLS


class DefaultSitemap(SitemapMeta):
    def __init__(self, app, base_url: str, config_obj=None, orm=None):
        super().__init__(app, base_url, config_obj, orm)

    def get_rules(self):
        return iter(DEFAULT_URLS)

    def view(self):
        return 'response'


record = Mock('slug', 'updated', 'priority')
rule = Mock(methods=['GET'], rule='/url')


class ORMModel:

    slug = updated = created = True

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

    model = Model(extractor)
    model.slug_attr = True
    model.lastmod_attr = True
    return model


@pytest.fixture
def config():
    """Creates an instance of a basis sitemap object"""
    config = SitemapConfig()
    config.TEMPLATE_FOLDER = TEST_FOLDER
    return config


@pytest.fixture
def default_map(config):
    """Creates an instance of a basis sitemap object"""
    # todo: test orm=None
    return DefaultSitemap(Mock, TEST_URL, config_obj=config, orm='sqlalchemy')


def teardown_module():
    for file in os.listdir(TEST_FOLDER):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join(TEST_FOLDER, file))
