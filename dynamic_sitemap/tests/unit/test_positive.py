from ..conftest import *


# Config tests
@pytest.mark.parametrize('obj', [
    SitemapConfig(),
    type('Config', tuple(), {}),
])
def test_config_from_obj(config, obj):
    """Tests configuration's setters and getters"""
    obj.TEST = True
    obj.ALTER_PRIORITY = 0.4
    config.from_object(obj)
    assert hasattr(config, 'TEST')
    assert config['ALTER_PRIORITY']


# Base object tests
def test_default_create_map(default_map, config):
    """Tests an instance creation"""
    time = TEST_TIME.strftime('%Y-%m-%dT%H')
    assert isinstance(default_map.start, str)
    assert time in default_map.start


@pytest.mark.parametrize('priority', [0.5, 0.733, 1])
def test_default_add_rule(default_map, priority):
    """Tests a rule creation"""
    default_map.add_rule('/app', ORMModel, priority=priority, lastmod='updated')
    obj = default_map.models['/app']
    assert obj.model == ORMModel
    assert isinstance(obj.attrs['slug'], str)
    assert isinstance(obj.attrs['lastmod'], str)
    assert isinstance(obj.attrs['priority'], (float, int))


def test_default_get_dynamic_rules(default_map):
    """Tests that the method returns only dynamic rules"""
    for url in default_map.get_dynamic_rules():
        assert '<' in url


def test_default_get_logger(default_map):
    """Tests a logger creation and debug level setup"""
    default_map.config.DEBUG = True
    default_map.get_logger()
    assert default_map.log.level == 10


def test_default_copy_template(default_map, request):
    """Tests a static file copying to source folder"""
    new_dir = os.path.join(TEST_FOLDER, 'new_dir')

    def teardown():
        from shutil import rmtree
        rmtree(new_dir)
    request.addfinalizer(teardown)

    os.makedirs(new_dir, exist_ok=True)
    default_map.config.TEMPLATE_FOLDER = new_dir
    default_map._copy_template()
    assert os.path.exists(new_dir)


@pytest.mark.parametrize('debug', [False, True])
def test_default_exclude(default_map, debug):
    """Tests that ignored urls was excluded"""
    default_map.config.DEBUG = debug
    default_map.config.IGNORED = ['/ign']
    for url in default_map._exclude():
        assert 'ign' not in url


def test_default_prepare_data(default_map):
    """Tests preparing data by pattern"""
    assert not default_map.data
    default_map.config.INDEX_PRIORITY = 1.0
    default_map.config.ALTER_PRIORITY = 0.3
    default_map.update()
    default_map._prepare_data()
    assert default_map.data[-1].loc
    assert default_map.data[-1].lastmod
    assert default_map.data[-1].priority == 0.3


@pytest.mark.parametrize('prefix', ['', '/', '/prefix', '/pr_e/f1x'])
@pytest.mark.parametrize('suffix', ['', '/', '/suffix'])
def test_default_replace_patterns(default_map, prefix, suffix):
    """Tests Record item data"""
    uri = prefix + '/<slug>'
    slug = '/' + ORMModel.query.all()[0].slug
    default_map.add_rule(prefix, ORMModel, lastmod='updated', priority=0.7)
    rec = default_map._replace_patterns(uri, [prefix, suffix])[0]
    assert rec.loc == f'{default_map.url}{prefix}{slug}{suffix}'
    assert rec.lastmod == TEST_TIME.strftime('%Y-%m-%dT%H:%M:%S')
    assert rec.priority == 0.7


def test_default_build_static(default_map):
    """Tests a static file creation"""
    path = os.path.join(TEST_FOLDER, 'static.xml')
    default_map.build_static(path)
    assert os.path.exists(path)


def test_helpers_model(local_model):
    """Tests helpers.Model"""
    rows = tuple(local_model.all())
    assert rows[1].slug == 'slug2'
    assert rows[1].lastmod == datetime(2020, 2, 2)
