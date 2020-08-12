from ..conftest import *


def test_flask_create_map(request, flask_map):
    """Tests an instance creation"""
    def teardown():
        flask_map.config.DEBUG = False
        flask_map.update()
    request.addfinalizer(teardown)

    flask_map.config.DEBUG = True
    flask_map.update()
    assert flask_map.query == 'model.query.all()'
    assert tuple(flask_map.rules) == DEFAULT_URLS


def test_flask_build_static(flask_map):
    """Tests a static file creation"""
    path = os.path.join(TEMPLATE_FOLDER, 'static.xml')
    flask_map.add_rule('/api', Model, lastmod='created')
    flask_map.config.IGNORED = ['/ign', '/blog']
    flask_map.build_static(path)
    assert os.path.exists(path)
