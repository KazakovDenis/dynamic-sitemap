from conftest import *


def test_create_flask_map(flask_map):
    assert flask_map.query == 'model.query.all()'


@pytest.mark.parametrize('priority', [0.5, 1])
def test_add_rule(flask_map, priority):
    flask_map.add_rule('/app', Model, priority=priority, lastmod='created')
    assert flask_map.models


def test_build_static(flask_map):
    path = os.path.join(os.path.abspath('.'), 'tmp', 'static.xml')
    flask_map.add_rule('/app', Model, lastmod='created')
    flask_map.build_static(path)
    assert os.path.exists(path)


if __name__ == '__main__':
    # for manual test
    sitemap = FlaskSitemap(FlaskApp, 'http://site.com', config)
    sitemap.add_rule('/app', Model)
    sitemap.build_static()
