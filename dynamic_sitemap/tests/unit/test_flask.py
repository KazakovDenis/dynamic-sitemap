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
def flask_map():
    """Creates an instance of FlaskSitemap"""
    sitemap = FlaskSitemap(FlaskApp, TEST_URL)
    sitemap.config.TEMPLATE_FOLDER = TEST_FOLDER
    sitemap.update()
    return sitemap


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
    assert flask_map.start


def test_flask_build_static(flask_map):
    """Tests a static file creation"""
    filename = 'static.xml'
    flask_map.filename = filename
    flask_map.add_rule('/api', ORMModel, lastmod='created')
    flask_map.build_static(TEST_FOLDER)
    file = os.path.join(TEST_FOLDER, filename)
    assert os.path.exists(file)


def test_flask_view(flask_client):
    """Tests http response"""
    with flask_client() as client:
        response = client.get('/sitemap.xml')

    assert response.status_code == 200
    assert response.content_type == 'application/xml'
