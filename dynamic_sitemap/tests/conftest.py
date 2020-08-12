import pytest

from .. import FlaskSitemap, SitemapConfig
from .mocks import *


PY_TYPES = int, float, complex, tuple, list, set, dict, str, bytes, bytearray
FALSE_INSTANCES = (py_type() for py_type in PY_TYPES)
TRUE_INSTANCES = 1, 1.0, 1+1j, (1,), [1], {1}, {1: 1}, 'str', b'bytes', bytearray(b'array')

TEMPLATE_FOLDER = os.path.join(EXTENSION_ROOT, 'tests', 'tmp')
TEMPLATE_FILE = os.path.join(TEMPLATE_FOLDER, 'sitemap.xml')
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
TEST_URL = 'http://site.com'


@pytest.fixture(autouse=True, scope='session')
def config():
    """Creates an instance of a basis sitemap object"""
    config = SitemapConfig()
    config.LOGGER = getLogger('sitemap')
    config.TEMPLATE_FOLDER = TEMPLATE_FOLDER
    return config


@pytest.fixture(autouse=True, scope='session')
def default_map(config):
    """Creates an instance of a basis sitemap object"""
    return DefaultSitemap(Mock, TEST_URL, config_obj=config)


@pytest.fixture(autouse=True, scope='session')
def flask_map(config):
    """Creates an instance of FlaskSitemap"""
    return FlaskSitemap(FlaskApp, TEST_URL, config_obj=config)


def teardown_module():
    for file in os.listdir(TEMPLATE_FOLDER):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join(TEMPLATE_FOLDER, file))
