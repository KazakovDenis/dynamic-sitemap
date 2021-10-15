import pytest

from dynamic_sitemap import SitemapConfig
from dynamic_sitemap.core import DynamicSitemapBase
from dynamic_sitemap.validators import get_validated

from ..utils import TRUE_INSTANCES, TEST_URL, ORMModel, WRONG_FOLDER, DYNAMIC_URLS


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
        DynamicSitemapBase(url, config=config, orm=orm)


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
        default_map.add_rule('/app', ORMModel, loc_from='slug', priority=priority)


@pytest.mark.parametrize('slug, lastmod', [
    pytest.param('no_such_attr', None, id='Wrong "loc" attribute'),
    pytest.param('slug', 'no_such_attr', id='Wrong "lastmod" attribute'),
])
def test_default_add_rule_no_attr(default_map, slug, lastmod):
    with pytest.raises(AttributeError):
        default_map.add_rule('/blog/', ORMModel, loc_from=slug, lastmod_from=lastmod)


@pytest.mark.parametrize('loc', [1, {1: 1}, '?arg1=50', TEST_URL])
def test_default_validate_loc(default_map, loc):
    """Tests how loc validation works"""
    with pytest.raises(AssertionError):
        get_validated(loc=loc)


@pytest.mark.parametrize('lastmod', [*TRUE_INSTANCES, '01:23', '01-01-2020'])
def test_default_validate_lastmod(default_map, lastmod):
    """Tests how lastmod validation works"""
    with pytest.raises(AssertionError):
        get_validated(lastmod=lastmod)


@pytest.mark.parametrize('changefreq', TRUE_INSTANCES)
def test_default_validate_changefreq(default_map, changefreq):
    """Tests how changefreq validation works"""
    with pytest.raises(AssertionError):
        get_validated(changefreq=changefreq)


@pytest.mark.parametrize('priority', [-1, 5, '1'])
def test_default_validate_priority(default_map, priority):
    """Tests how priority validation works"""
    with pytest.raises(AssertionError):
        get_validated(priority=priority)


@pytest.mark.parametrize('path, error', [
    pytest.param(None, AssertionError, id='No folder set'),
    pytest.param(WRONG_FOLDER, FileNotFoundError, id='Wrong folder in config'),
    pytest.param(None, FileNotFoundError, id='Wrong path in arguments'),
])
def test_default_build_static(default_map, path, error):
    """Tests raising exceptions with no or wrong path set"""
    default_map.filename = 'static.xml'
    default_map.config.IGNORED.update(DYNAMIC_URLS)
    with pytest.raises(error):
        default_map.write(path)
