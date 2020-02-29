import os
import pytest

from ..flask_map import FlaskSitemap
from .mocks import *


@pytest.fixture(autouse=True, scope='session')
def flask_map():
    """Creates an instance of FlaskSitemap"""
    return FlaskSitemap(FlaskApp(), 'http://site.com', config_obj=config)


def teardown_module():
    tmp = os.path.join(os.path.abspath('.'), 'dynamic_sitemap', 'tmp')
    for file in os.listdir(tmp):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join(tmp, file))
