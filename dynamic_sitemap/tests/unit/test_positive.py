from ..conf import *


# Base object tests
def test_default_create_map(default_map):
    now = datetime.now().strftime('%Y-%m-%dT%H')
    assert isinstance(default_map.start, str)
    assert now in default_map.start


@pytest.mark.parametrize('priority', [0.5, 0.733, 1])
def test_default_add_rule(default_map, priority):
    default_map.add_rule('/app', Model, priority=priority, lastmod='updated')
    model = default_map.models['/app']
    assert model[0] == Model
    assert isinstance(model[1], str)
    assert isinstance(model[2], str)
    assert isinstance(model[3], (float, int))


def test_default_debug_level(default_map):
    default_map.set_debug_level()
    assert default_map.log.level == 10


def test_default_copy_template(default_map):
    default_map._copy_template(template_folder)
    assert os.path.exists(template)


def test_default_copy_exception(default_map, request):
    def test_default_copy_exception_teardown():
        default_map.config.DEBUG = True
    request.addfinalizer(test_default_copy_exception_teardown)
    default_map.config.DEBUG = False
    with pytest.raises(FileExistsError):
        default_map._copy_template(template_folder)

# todo
# test_default_exclude
# test_default_prepare_data
# test_default_replace_patterns


# FlaskSitemap tests
def test_flask_create_map(flask_map):
    assert flask_map.query == 'model.query.all()'


def test_flask_build_static(flask_map):
    path = os.path.join(os.path.abspath('.'), 'dynamic_sitemap', 'tmp', 'static.xml')
    flask_map.add_rule('/app', Model, lastmod='created')
    flask_map.build_static(path)
    assert os.path.exists(path)


if __name__ == '__main__':
    # for manual test
    sitemap = FlaskSitemap(FlaskApp, 'http://site.com', config)
    sitemap.add_rule('/app', Model)
    sitemap.build_static()
