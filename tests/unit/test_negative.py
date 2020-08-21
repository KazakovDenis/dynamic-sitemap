from dynamic_sitemap.config import validate_tags
from ..conftest import *


# Config tests
@pytest.mark.parametrize('obj', TRUE_INSTANCES)
def test_config_from_obj(config, obj):
    """Tests configuration's from_object method exception"""
    with pytest.raises(NotImplementedError):
        config.from_object(obj)


def test_config_set(default_map):
    """Tests impossibility of another config object setting"""
    another = SitemapConfig()
    with pytest.raises(PermissionError):
        default_map.config = another


# Base object tests
@pytest.mark.parametrize('url, config, orm, error', [
    pytest.param(b'Wrong URL type', None, None, TypeError, id='Wrong URL argument type'),
    pytest.param('Wrong URL', None, None, ValueError, id='Wrong URL'),
    pytest.param(TEST_URL, 'Wrong config type', None, NotImplementedError, id='Wrong config type'),
    pytest.param(TEST_URL, None, b'Wrong ORM type', TypeError, id='Wrong ORM argument type'),
    pytest.param(TEST_URL, None, 'Unknown ORM', NotImplementedError, id='Unknown ORM'),
])
def test_default_create_map(url, orm, config, error):
    """Test exceptions while init"""
    with pytest.raises(error):
        DefaultSitemap(Mock, url, config_obj=config, orm=orm)


@pytest.mark.parametrize('priority, error', [
    pytest.param(5, AssertionError, id='Greater priority'),
    pytest.param(-1, AssertionError, id='Negative priority'),
    pytest.param('0.5', TypeError, id='String priority'),
    pytest.param('high', TypeError, id='Wrong type priority')
])
def test_default_add_rule_priority(default_map, priority, error):
    """Assertion error should be raised when priority is not in range 0.0-1.0.
    TypeError should be raised when got non-numeric."""
    with pytest.raises(error):
        default_map.add_rule('/app', ORMModel, loc_attr='slug', priority=priority)


@pytest.mark.parametrize('loc', [1, {1: 1}, '?arg1=50', TEST_URL])
def test_default_validate_loc(default_map, loc):
    """Tests how loc validation works"""
    with pytest.raises(AssertionError):
        validate_tags(loc=loc)


@pytest.mark.parametrize('lastmod', [*TRUE_INSTANCES, '01:23', '01-01-2020'])
def test_default_validate_lastmod(default_map, lastmod):
    """Tests how lastmod validation works"""
    with pytest.raises(AssertionError):
        validate_tags(lastmod=lastmod)


@pytest.mark.parametrize('changefreq', TRUE_INSTANCES)
def test_default_validate_changefreq(default_map, changefreq):
    """Tests how changefreq validation works"""
    with pytest.raises(AssertionError):
        validate_tags(changefreq=changefreq)


@pytest.mark.parametrize('priority', [-1, 5, '1'])
def test_default_validate_priority(default_map, priority):
    """Tests how priority validation works"""
    with pytest.raises(AssertionError):
        validate_tags(priority=priority)


def test_default_copy_template_file_exists(request, default_map):
    """Tests exception which should be raised when sitemap.xml already exists"""
    def teardown():
        os.remove(TEST_FILE)
    request.addfinalizer(teardown)
    
    with open(TEST_FILE, 'w') as f:
        f.write('Another sitemap file')

    with pytest.raises(FileExistsError):
        default_map._copy_template()


def test_default_copy_template_no_permission(default_map):
    """Tests exception which should be raised when putting into not existing directory"""
    default_map.config.TEMPLATE_FOLDER = 'no_such_dir'
    with pytest.raises(PermissionError):
        default_map._copy_template()


@pytest.mark.parametrize('folder, path, error', [
    pytest.param(None, None, AssertionError, id='No folder set'),
    pytest.param(WRONG_FOLDER, None, FileNotFoundError, id='Wrong folder in config'),
    pytest.param(None, WRONG_FOLDER, FileNotFoundError, id='Wrong path in arguments'),
])
def test_default_build_static(default_map, folder, path, error):
    """Tests raising exceptions with no or wrong path set"""
    default_map.filename = 'static.xml'
    default_map.config.STATIC_FOLDER = folder
    default_map.config.IGNORED.update(DYNAMIC_URLS)
    with pytest.raises(error):
        default_map.build_static(path)


@pytest.mark.parametrize('slug, lastmod', [
    pytest.param('no_such_attr', None, id='Wrong "loc" attribute'),
    pytest.param('slug', 'no_such_attr', id='Wrong "lastmod" attribute'),
])
def test_default_replace_patterns_no_attr(default_map, slug, lastmod):
    prefix = '/blog'
    default_map.add_rule(prefix, ORMModel, loc_attr=slug, lastmod_attr=lastmod)
    with pytest.raises(AttributeError):
        default_map._replace_patterns('', [prefix, ''])
