import os
from datetime import datetime
from operator import attrgetter
from urllib.parse import urljoin
from uuid import uuid4

import pytest

from dynamic_sitemap import SitemapConfig, ChangeFreq
from dynamic_sitemap.helpers import join_url_path
from tests.utils import TEST_DATE_STR, TEST_TIME_STR, TEST_URL, ORMModel, SitemapMock


@pytest.mark.parametrize('obj', [
    SitemapConfig(),
    type('Config', tuple(), {}),
])
def test_config_from_obj(config, obj):
    """Test configuration's setters and getters"""
    obj.TEST = True
    obj.ALTER_PRIORITY = 0.4
    config.from_object(obj)
    assert hasattr(config, 'TEST')
    assert config['ALTER_PRIORITY'] == 0.4


def test_queries_no_orm(local_model):
    sitemap = SitemapMock(TEST_URL, orm=None)
    sitemap._rules = ['/rule/<slug>/']
    sitemap.add_rule('/rule', local_model, loc_from='slug')
    sitemap.build()
    assert sitemap.initialized


@pytest.mark.parametrize('orm', ['sqlalchemy', 'SQLAlchemy', 'django', 'peewee'])
def test_queries_with_orm(orm):
    sitemap = SitemapMock(TEST_URL, orm=orm)
    sitemap._rules = ['/rule/<slug>/']
    sitemap.add_rule('/rule', ORMModel, loc_from='slug')
    sitemap.build()
    assert sitemap.initialized


def test_default_build(sitemap, monkeypatch):
    """Test building without problems only."""
    monkeypatch.setattr(sitemap, '_without_ignored', lambda: [])
    sitemap.build()
    assert sitemap.initialized


def test_default_add_items(sitemap, monkeypatch):
    """Test an item creation."""
    monkeypatch.setattr(sitemap, '_without_ignored', lambda: [])
    sitemap.add_items([
        '/page1',
        dict(loc='/', lastmod='2020-01-01', changefreq='weekly', priority=0.8),
    ])
    assert not sitemap.items

    sitemap.build()
    items = sorted(sitemap.items, key=attrgetter('loc'))
    assert len(items) == 2
    assert items[0].priority == 0.8
    assert items[1].priority is None
    assert items[1].loc == urljoin(TEST_URL, '/page1')


@pytest.mark.parametrize('priority', [0.5, 0.733, 1])
def test_default_add_rule(sitemap, priority):
    """Test a rule creation."""
    sitemap.add_rule('/app', ORMModel, loc_from='slug', lastmod_from='updated', priority=priority)
    obj = sitemap._models['/app/']
    assert obj.model == ORMModel
    assert isinstance(obj.attrs['loc_from'], str)
    assert isinstance(obj.attrs['lastmod_from'], str)
    assert isinstance(obj.attrs['priority'], (float, int))


def test_default_write(sitemap, request):
    """Test a static file is written."""
    filename = str(uuid4())

    def teardown():
        os.unlink(filename)
    request.addfinalizer(teardown)

    sitemap.write(filename)
    assert os.path.exists(filename)


def test_default_write_from_config(sitemap, request):
    """Tests a static file copying to source folder"""
    filename = str(uuid4())

    def teardown():
        os.unlink(filename)
    request.addfinalizer(teardown)

    sitemap.config.FILENAME = filename
    sitemap.write()
    assert os.path.exists(filename)


def test_default_without_ignored(sitemap):
    """Test that ignored urls was excluded."""
    pattern = '/rule'
    sitemap._rules = ['/rule/<slug>/']
    sitemap.config.IGNORED = {pattern}
    for url in sitemap._without_ignored():
        assert pattern not in url


@pytest.mark.parametrize('result, items, cache_period, timestamp', [
    pytest.param(False, [], None, datetime.now(), id='No data, cache disabled'),
    pytest.param(False, [], 1, datetime.now(), id='No data, cache enabled'),
    pytest.param(False, [1], None, datetime.now(), id='Data exists, cache disabled'),
    pytest.param(False, [1], 1, datetime(2020, 1, 1), id='Data exists, cache enabled, time not expired'),
    pytest.param(True, [1], 1, datetime(2050, 1, 1), id='Data exists, cache enabled, time expired')
])
def test_default_should_use_cache(sitemap, result, items, cache_period, timestamp):
    """Test conditions to use cache."""
    sitemap.config.CACHE_PERIOD = cache_period
    sitemap.items = items
    sitemap._cached_at = timestamp
    assert sitemap._should_use_cache() == result


def test_default_prepare_data_static(sitemap):
    """Test static data preparing."""
    assert not sitemap.items
    sitemap.config.INDEX_PRIORITY = 1.0
    sitemap.config.ALTER_PRIORITY = 0.3
    sitemap.config.ALTER_CHANGES = ChangeFreq.WEEKLY.value
    sitemap.add_items(['/test', '/page'])
    sitemap.build()
    items = sorted(sitemap.items, key=attrgetter('loc'))
    assert TEST_URL in items[-1].loc
    assert items[-1].changefreq == ChangeFreq.WEEKLY.value
    assert items[0].priority == 1.0
    assert items[-1].priority == 0.3


def test_default_prepare_data_dynamic(sitemap):
    """Test preparing data by patterns."""
    assert not sitemap.items
    sitemap.config.INDEX_PRIORITY = 1.0
    sitemap.config.ALTER_PRIORITY = 0.3
    sitemap._rules = ['/rule/<slug>/']
    sitemap.add_rule('/rule', ORMModel, loc_from='slug', lastmod_from='updated', priority=0.91)
    sitemap.build()
    items = sorted(sitemap.items, key=attrgetter('loc'))
    assert TEST_URL in items[-1].loc
    assert TEST_DATE_STR in items[-1].lastmod
    assert items[0].priority == 1.0
    assert items[-1].priority == 0.9


@pytest.mark.parametrize('prefix', ['', '/', '/prefix', '/pr_e/f1x/'])
@pytest.mark.parametrize('suffix', ['', '/', '/suffix'])
@pytest.mark.parametrize('model', [ORMModel, 'local_model'])
def test_default_replace_patterns(sitemap, prefix, suffix, model):
    """Test item data."""
    uri = prefix + '/<slug>'
    slug = '/' + ORMModel.query.all()[0].slug
    sitemap.add_rule(prefix, ORMModel, loc_from='slug', lastmod_from='updated', priority=0.7)
    prefix = prefix if prefix.endswith('/') else prefix + '/'
    rec = sitemap._replace_patterns(uri, [prefix, suffix])[0]
    assert rec.loc == join_url_path(sitemap.url, prefix, slug, suffix)
    assert rec.lastmod == TEST_TIME_STR
    assert rec.priority == 0.7


def test_helpers_model(local_model):
    """Test helpers.Model."""
    rows = tuple(local_model.all())
    assert rows[1].slug == 'slug2'
    assert rows[1].lastmod == datetime(2020, 2, 2)


def test_helpers_model_add_rule(sitemap, local_model):
    """Test add_rule with helpers.Model."""
    slug, lastmod = 'slug_attr', 'lastmod_attr'
    sitemap.add_rule('/path', local_model, loc_from=slug, lastmod_from=lastmod, priority=0.91)
    path_model = sitemap._models['/path/']
    assert path_model.attrs['loc_from'] == slug
    assert path_model.attrs['lastmod_from'] == lastmod
    assert path_model.attrs['priority'] == 0.9
