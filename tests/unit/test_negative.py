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
    (b'Wrong URL type', None, None, TypeError),
    ('Wrong URL', None, None, ValueError),
    (TEST_URL, 'Wrong config type', None, NotImplementedError),
    (TEST_URL, None, b'Wrong ORM type', TypeError),
    (TEST_URL, None, 'Unknown ORM', NotImplementedError),
])
def test_default_create_map(url, orm, config, error):
    """Test exceptions while init"""
    with pytest.raises(error):
        DefaultSitemap(Mock, url, config_obj=config, orm=orm)


@pytest.mark.parametrize('priority, error', [
    (5, AssertionError),
    (-1, AssertionError),
    ('0.5', TypeError),
    ('high', TypeError)
])
def test_default_add_rule_priority(default_map, priority, error):
    """Assertion error should be raised when priority is not in range 0.0-1.0.
    TypeError should be raised when got non-numeric."""
    with pytest.raises(error):
        default_map.add_rule('/app', ORMModel, priority=priority)


@pytest.mark.parametrize('loc', [None, '?arg1=50', TEST_URL])
@pytest.mark.parametrize('lastmod', [None])    # todo
@pytest.mark.parametrize('changefreq', [None, True, 'everyday'])
@pytest.mark.parametrize('priority', [None, -1, 5, '1'])
def test_default_validate_tags(default_map, loc, lastmod, changefreq, priority):
    """Tests how validation works

    'None' arguments is added to avoid situation another parameter raises AssertionError
    assert not any - to avoid situation when every parameter is None
    """
    with pytest.raises(AssertionError):
        default_map.validate_tags(loc=loc, lastmod=lastmod, changefreq=changefreq, priority=priority)
        assert any([loc, lastmod, changefreq, priority])


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
    (None, None, AssertionError),
    (WRONG_FOLDER, None, FileNotFoundError),
    (None, WRONG_FOLDER, FileNotFoundError),
])
def test_default_build_static(default_map, folder, path, error):
    """Tests raising exceptions with no or wrong path set"""
    default_map.filename = 'static.xml'
    default_map.config.STATIC_FOLDER = folder
    default_map.config.IGNORED.update(DYNAMIC_URLS)
    with pytest.raises(error):
        default_map.build_static(path)


@pytest.mark.parametrize('slug, lastmod', [
    ('no_such_attr', None),
    ('slug', 'no_such_attr'),
])
def test_default_replace_patterns_no_attr(default_map, slug, lastmod):
    prefix = '/blog'
    default_map.add_rule(prefix, ORMModel, loc_attr=slug, lastmod_attr=lastmod)
    with pytest.raises(AttributeError):
        default_map._replace_patterns('', [prefix, ''])
