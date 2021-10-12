from dynamic_sitemap.items import SitemapItem
from dynamic_sitemap.validators import get_validated, CHANGE_FREQ
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


def test_record():
    """Tests Record object returns XML object"""
    rec = SitemapItem(loc='/path', lastmod='2020-01-01', changefreq='daily', priority=0.7).as_xml()
    children = rec.getchildren()
    assert children[0].text == '/path'
    assert children[1].text == '2020-01-01'
    assert children[2].text == 'daily'
    assert children[3].text == '0.7'


# Base object tests
def test_default_create_map(default_map, config):
    """Tests an instance creation"""
    assert TEST_DATE_STR in default_map.start


def test_default_add_elem(default_map):
    """Tests a elem creation"""
    default_map.add_elem('/index', lastmod='2020-01-01', changefreq='weekly', priority=0.8)
    default_map.add_elem('/index', lastmod='2020-02-02', changefreq='daily', priority=1)
    assert len(default_map._static_data) == 1
    rec = default_map._static_data.pop()
    assert rec.loc == urljoin(TEST_URL, '/index')
    assert isinstance(rec.lastmod, str)
    assert rec.changefreq in CHANGE_FREQ
    assert isinstance(rec.priority, (float, int))


@pytest.mark.parametrize('priority', [0.5, 0.733, 1])
def test_default_add_rule(default_map, priority):
    """Tests a rule creation"""
    default_map.add_rule('/app', ORMModel, loc_attr='slug', lastmod_attr='updated', priority=priority)
    obj = default_map._models['/app/']
    assert obj.model == ORMModel
    assert isinstance(obj.attrs['loc_attr'], str)
    assert isinstance(obj.attrs['lastmod_attr'], str)
    assert isinstance(obj.attrs['priority'], (float, int))


@pytest.mark.parametrize('loc', ['/index', '/index/page?arg=50'])
@pytest.mark.parametrize('lastmod', ['2020-01-01T01:01:01', '2020-02-02'])
@pytest.mark.parametrize('changefreq', ['daily', 'weekly'])
@pytest.mark.parametrize('priority', [0.5, 0.733, 1])
def test_default_validate_tags(default_map, loc, lastmod, changefreq, priority):
    """Tests a elem creation"""
    get_validated(loc=loc, lastmod=lastmod, changefreq=changefreq, priority=priority)


def test_default_get_dynamic_rules(default_map):
    """Tests that the method returns only dynamic rules"""
    for url in default_map.get_dynamic_rules():
        assert '<' in url


@pytest.mark.parametrize('logger, name', [
    pytest.param(None, 'sitemap', id='Default logger'),
    pytest.param(Logger('test'), 'test', id='User logger')
])
def test_default_get_logger(default_map, logger, name):
    """Tests setting a default logger"""
    default_map.config.LOGGER = logger
    log = default_map.get_logger()
    assert log.name == name


def test_default_logger_debug(default_map):
    """Tests a logger creation and debug level setup"""
    default_map.config.DEBUG = True
    default_map.config.LOGGER = None
    logger = default_map.get_logger()
    assert logger.level == 10
    assert logger.handlers[0].level == 10


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
    default_map.config.IGNORED.update({'/ign'})
    for url in default_map._exclude():
        assert 'ign' not in url


@pytest.mark.parametrize('result, records, cache_period, timestamp', [
    pytest.param(False, [], None, datetime.now(), id='No data, cache disabled'),
    pytest.param(False, [], 1, datetime.now(), id='No data, cache enabled'),
    pytest.param(False, [1], None, datetime.now(), id='Data exists, cache disabled'),
    pytest.param(False, [1], 1, datetime(2020, 1, 1), id='Data exists, cache enabled, time not expired'),
    pytest.param(True, [1], 1, datetime(2050, 1, 1), id='Data exists, cache enabled, time expired')
])
def test_default_should_use_cache(default_map, result, records, cache_period, timestamp):
    """Tests conditions to use cache"""
    default_map.config.CACHE_PERIOD = cache_period
    default_map._records = records
    default_map._timestamp = timestamp
    assert default_map._should_use_cache() == result


def test_default_prepare_data_static(default_map):
    """Tests preparing data by pattern"""
    assert not default_map.records
    default_map.config.INDEX_PRIORITY = 1.0
    default_map.config.ALTER_PRIORITY = 0.3
    default_map.config.IGNORED.update(DYNAMIC_URLS)
    default_map._prepare_data()
    assert TEST_URL in default_map.records[-1].loc
    assert TEST_DATE_STR in default_map.records[-1].lastmod
    assert default_map.records[0].priority == 1.0
    assert default_map.records[-1].priority == 0.3


def test_default_prepare_data_dynamic(default_map):
    """Tests preparing data by pattern"""
    assert not default_map.records
    default_map.config.INDEX_PRIORITY = 1.0
    default_map.config.ALTER_PRIORITY = 0.3
    default_map.config.IGNORED = {'/api', '/blog'}
    default_map.add_rule('/ign', ORMModel, loc_attr='slug', lastmod_attr='updated', priority=0.91)
    default_map._prepare_data()
    assert TEST_URL in default_map.records[-1].loc
    assert TEST_DATE_STR in default_map.records[-1].lastmod
    assert default_map.records[0].priority == 1.0
    assert default_map.records[1].priority == 0.3
    assert default_map.records[-1].priority == 0.9


@pytest.mark.parametrize('prefix', ['', '/', '/prefix', '/pr_e/f1x/'])
@pytest.mark.parametrize('suffix', ['', '/', '/suffix'])
@pytest.mark.parametrize('model', [ORMModel, local_model])
def test_default_replace_patterns(default_map, prefix, suffix, model):
    """Tests Record item data"""
    uri = prefix + '/<slug>'
    slug = '/' + ORMModel.query.all()[0].slug
    default_map.add_rule(prefix, ORMModel, loc_attr='slug', lastmod_attr='updated', priority=0.7)
    prefix = prefix if prefix.endswith('/') else prefix + '/'
    rec = default_map._replace_patterns(uri, [prefix, suffix])[0]
    assert rec.loc == join_url_path(default_map.url, prefix, slug, suffix)
    assert rec.lastmod == TEST_TIME_STR
    assert rec.priority == 0.7


@pytest.mark.parametrize('priority', [None, 0.5])
def test_default_build_static(default_map, priority):
    """Tests a static file creation"""
    filename = 'static.xml'
    default_map.filename = filename
    default_map.config.ALTER_PRIORITY = priority
    default_map.config.IGNORED.update(DYNAMIC_URLS)
    default_map.build_static(TEST_FOLDER)
    file = os.path.join(TEST_FOLDER, filename)
    assert os.path.exists(file)


def test_helpers_model(local_model):
    """Tests helpers.Model"""
    rows = tuple(local_model.all())
    assert rows[1].slug == 'slug2'
    assert rows[1].lastmod == datetime(2020, 2, 2)


def test_helpers_model_add_rule(default_map, local_model):
    """Tests add_rule with helpers.Model"""
    default_map.add_rule('/path', local_model, loc_attr='slug_attr', lastmod_attr='lastmod_attr', priority=0.91)
    path_model = default_map._models['/path/']
    assert path_model.attrs['loc_attr'] == 'slug_attr'
    assert path_model.attrs['lastmod_attr'] == 'lastmod_attr'
    assert path_model.attrs['priority'] == 0.9
