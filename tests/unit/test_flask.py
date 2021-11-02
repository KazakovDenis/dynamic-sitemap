import os
from uuid import uuid4

import pytest

from dynamic_sitemap import FlaskSitemap
from tests.utils import TEST_URL

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    Flask = SQLAlchemy = None
    pytestmark = pytest.mark.not_installed


class _FlaskConfig:
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.config.from_object(_FlaskConfig)
    SQLAlchemy(app)
    return app


@pytest.fixture
def flask_map(flask_app):
    sitemap = FlaskSitemap(flask_app, TEST_URL)
    sitemap.build()
    return sitemap


@pytest.fixture
def flask_client(flask_app):
    return flask_app.test_client


def test_flask_get_rules(flask_map):
    """Test rules generation."""
    assert '/sitemap.xml' in flask_map.get_rules()


def test_flask_render(flask_map):
    """Test an instance creation."""
    assert flask_map.render()


@pytest.mark.parametrize('fn1, fn2', [
    (str(uuid4()), None),
    (None, str(uuid4())),
])
def test_flask_write(request, flask_map, fn1, fn2):
    """Test a static file is written."""
    filename = fn1 or fn2

    def teardown():
        if os.path.exists(filename):
            os.remove(filename)
    request.addfinalizer(teardown)

    flask_map.config.FILENAME = fn1
    flask_map.write(fn2)
    assert os.path.exists(filename)


def test_flask_view(flask_client, flask_map):
    """Test http response."""
    with flask_client() as client:
        response = client.get('/sitemap.xml')

    assert response.status_code == 200
    assert response.content_type == 'application/xml'
