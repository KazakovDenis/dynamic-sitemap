from ..conftest import *


try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    FlaskApp = Flask('FlaskApp', template_folder=TEST_FOLDER)
    FlaskApp.testing = True
    db = SQLAlchemy(FlaskApp)

except ImportError:
    pytestmark = pytest.mark.not_installed


@pytest.fixture(autouse=True, scope='session')
def flask_map(config):
    """Creates an instance of FlaskSitemap"""
    return FlaskSitemap(FlaskApp, TEST_URL, config_obj=config)


@pytest.fixture(autouse=True, scope='session')
def flask_client():
    """Emulates user"""
    return FlaskApp.test_client


def test_flask_create_map(request, flask_map):
    """Tests an instance creation"""
    def teardown():
        flask_map.config.DEBUG = False
        flask_map.update()
    request.addfinalizer(teardown)

    flask_map.config.DEBUG = True
    flask_map.update()
    assert flask_map.query == 'model.query.all()'


def test_flask_build_static(flask_map):
    """Tests a static file creation"""
    path = os.path.join(TEST_FOLDER, 'static.xml')
    flask_map.add_rule('/api', Model, lastmod='created')
    flask_map.build_static(path)
    assert os.path.exists(path)


def test_flask_view(flask_client):
    """Tests http response"""
    with flask_client() as client:
        response = client.get('/sitemap.xml')

    assert response.status_code == 200
    assert response.content_type == 'application/xml'
