import pytest

from dynamic_sitemap import SitemapConfig
from dynamic_sitemap.exceptions import SitemapIOError, SitemapValidationError
from dynamic_sitemap.validators import get_validated
from tests.utils import TEST_URL, TRUE_INSTANCES, ORMModel


@pytest.mark.parametrize('obj', TRUE_INSTANCES)
def test_config_from_obj(config, obj):
    """Tests configuration's from_object method exception"""
    with pytest.raises(SitemapValidationError):
        config.from_object(obj)


def test_config_set(sitemap):
    """Tests impossibility of another config object setting"""
    another = SitemapConfig()
    with pytest.raises(SitemapValidationError):
        sitemap.config = another


# Base object tests
@pytest.mark.parametrize('url, config, orm', [
    pytest.param(b'Wrong URL type', None, None, id='Wrong URL argument type'),
    pytest.param('Wrong URL', None, None, id='Wrong URL'),
    pytest.param(TEST_URL, 'Wrong config type', None, id='Wrong config type'),
    pytest.param(TEST_URL, None, b'Wrong ORM type', id='Wrong ORM argument type'),
    pytest.param(TEST_URL, None, 'Unknown ORM', id='Unknown ORM'),
])
def test_default_create_map(sitemap_cls, url, orm, config):
    """Test exceptions while init"""
    with pytest.raises(SitemapValidationError):
        sitemap_cls(url, config=config, orm=orm)


@pytest.mark.parametrize('priority', [
    pytest.param(5, id='Greater priority'),
    pytest.param(-1, id='Negative priority'),
    pytest.param('0.5', id='String priority'),
    pytest.param('high', id='Wrong type priority')
])
def test_default_add_rule_priority(sitemap, priority):
    """Assertion error should be raised when priority is not in range 0.0-1.0.
    TypeError should be raised when got non-numeric."""
    with pytest.raises(SitemapValidationError):
        sitemap.add_rule('/app', ORMModel, loc_from='slug', priority=priority)


@pytest.mark.parametrize('bad_attr', [
    pytest.param('slug', id='Wrong "loc" attribute'),
    pytest.param('lastmod', id='Wrong "lastmod" attribute'),
])
def test_default_add_rule_no_attr(sitemap, monkeypatch, bad_attr):
    monkeypatch.delattr(ORMModel, bad_attr)
    with pytest.raises(SitemapValidationError):
        sitemap.add_rule('/blog/', ORMModel, loc_from='slug', lastmod_from='lastmod')


@pytest.mark.parametrize('loc', ['/index', '/index/page?arg=50'])
@pytest.mark.parametrize('lastmod', ['2020-01-01T01:01:01', '2020-02-02'])
@pytest.mark.parametrize('changefreq', ['daily', 'weekly'])
@pytest.mark.parametrize('priority', [0.5, 0.733, 1])
def test_default_validate_tags(loc, lastmod, changefreq, priority):
    """Test validation is ok."""
    get_validated(loc=loc, lastmod=lastmod, changefreq=changefreq, priority=priority)


@pytest.mark.parametrize('loc', [1, {1: 1}, '?arg1=50', TEST_URL])
def test_default_validate_loc(loc):
    """Test how loc validation works."""
    with pytest.raises(SitemapValidationError):
        get_validated(loc=loc)


@pytest.mark.parametrize('lastmod', [*TRUE_INSTANCES, '01:23', '01-01-2020'])
def test_default_validate_lastmod(lastmod):
    """Test how lastmod validation works."""
    with pytest.raises(SitemapValidationError):
        get_validated(lastmod=lastmod)


@pytest.mark.parametrize('changefreq', TRUE_INSTANCES)
def test_default_validate_changefreq(changefreq):
    """Test how changefreq validation works."""
    with pytest.raises(SitemapValidationError):
        get_validated(changefreq=changefreq)


@pytest.mark.parametrize('priority', [-1, 5, '1'])
def test_default_validate_priority(priority):
    """Test how priority validation works."""
    with pytest.raises(SitemapValidationError):
        get_validated(priority=priority)


@pytest.mark.parametrize('fn1, fn2, error', [
    pytest.param('/access/denied.xml', None, SitemapIOError, id='Wrong filename in config'),
    pytest.param(None, '/access/denied.xml', SitemapIOError, id='Wrong filename in arguments'),
    pytest.param(None, None, SitemapValidationError, id='No filename provided.'),
])
def test_default_build_static(sitemap, fn1, fn2, error):
    """Test raising exceptions with no or wrong path set."""
    sitemap.config.FILENAME = fn1
    sitemap.build()
    with pytest.raises(error):
        sitemap.write(fn2)
