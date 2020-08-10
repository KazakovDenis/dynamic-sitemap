import pytest

from .. import FlaskSitemap, SitemapConfig
from .mocks import *


template_folder = os.path.join(EXTENSION_ROOT, 'tmp')
template = template_folder + '/sitemap.xml'


@pytest.fixture(autouse=True, scope='session')
def config():
    """Creates an instance of a basis sitemap object"""
    config = SitemapConfig()
    config.LOGGER = getLogger('sitemap')
    config.TEMPLATE_FOLDER = template_folder
    return config


@pytest.fixture(autouse=True, scope='session')
def default_map(config):
    """Creates an instance of a basis sitemap object"""
    return DefaultSitemap(Mock, 'http://site.com', config_obj=config)


@pytest.fixture(autouse=True, scope='session')
def flask_map(config):
    """Creates an instance of FlaskSitemap"""
    return FlaskSitemap(FlaskApp, 'http://site.com', config_obj=config)


def teardown_module():
    for file in os.listdir(template_folder):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join(template_folder, file))
