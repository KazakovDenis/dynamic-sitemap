import pytest

from dynamic_sitemap.items import SitemapIndexItem, SitemapItem


def test_sitemap_item():
    """Test SitemapItem returns a correct XML object"""
    item = SitemapItem(loc='/path', lastmod='2020-01-01', changefreq='daily', priority=0.7).as_xml()
    children = item.getchildren()
    assert children[0].text == '/path'
    assert children[1].text == '2020-01-01'
    assert children[2].text == 'daily'
    assert children[3].text == '0.7'


def test_sitemap_index_item():
    """Test SitemapIndexItem returns a correct XML object"""
    item = SitemapIndexItem(loc='/path', lastmod='2020-01-01').as_xml()
    children = item.getchildren()
    assert children[0].text == '/path'
    assert children[1].text == '2020-01-01'


@pytest.mark.parametrize('item, result', [
    (SitemapItem('/loc'), True),
    (SitemapItem('/loc', '2020-01-01'), True),
    (SitemapItem('/location'), False),
    ('/loc', False),
])
def test_items_equal(item, result):
    assert (SitemapItem('/loc') == item) is result
