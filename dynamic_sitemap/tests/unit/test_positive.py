from ..conf import *

now = datetime.now().strftime('%Y-%m-%dT%H')


# Base object tests
def test_default_create_map(default_map):
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


def test_default_exclude(default_map):
    default_map.rules = ['/', '/url', '/<slug>', '/ign']
    for url in default_map._exclude():
        assert 'ign' not in url


def test_default_prepare_data(default_map):
    assert not default_map.data
    default_map.config.IGNORED.extend(['/<slug>'])
    default_map._prepare_data()
    default_map.config.IGNORED.pop(default_map.config.IGNORED.index('/<slug>'))
    assert default_map.data


def test_get_rules(default_map):
    for url in default_map.get_dynamic_rules():
        assert '<' in url


@pytest.mark.parametrize('prefix', ['/', '/prefix', '/pre/fix'])
@pytest.mark.parametrize('suffix', ['', '/', '/suffix'])
def test_default_replace_patterns(default_map, prefix, suffix):
    uri = '/<slug>'
    assert uri in default_map.get_dynamic_rules()
    default_map.query = SitemapMeta.queries['flask']
    default_map.add_rule(prefix, Model)
    slug = '/' + Model.query.all()[0].slug
    record = default_map._replace_patterns(uri, [prefix, suffix])[0]
    assert record.loc == f'{default_map.url}{prefix}{slug}{suffix}'
    assert hasattr(record, 'lastmod')
    assert hasattr(record, 'priority')


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
