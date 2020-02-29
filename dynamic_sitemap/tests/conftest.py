import os
import pytest

from flask_map import FlaskSitemap
from mocks import *


@pytest.fixture(autouse=True, scope='module')
def flask_map():
    """Creates an instance of FlaskSitemap"""
    return FlaskSitemap(FlaskApp(), 'http://site.com', config_obj=config)


def teardown_module():
    for file in os.listdir('tmp'):
        if file.rsplit('.', 1)[-1] == 'xml':
            os.remove(os.path.join('tmp', file))
