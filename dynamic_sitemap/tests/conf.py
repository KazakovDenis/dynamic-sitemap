import os
import pytest

from .. import FlaskSitemap
from .mocks import *


template_folder = os.path.join(os.path.abspath('.'), 'dynamic_sitemap', 'tmp')
template = template_folder + '/sitemap.xml'


@pytest.fixture(autouse=True, scope='session')
def default_map():
    """Creates an instance of a basis sitemap object"""
    return DefaultSitemap(Mock, 'http://site.com', config_obj=config)


@pytest.fixture(autouse=True, scope='session')
def flask_map():
    """Creates an instance of FlaskSitemap"""
    return FlaskSitemap(FlaskApp, 'http://site.com', config_obj=config)


def teardown_module():
    for file in os.listdir(template_folder):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join(template_folder, file))
