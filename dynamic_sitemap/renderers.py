from io import BytesIO
from typing import Collection
from xml.etree import ElementTree

from .items import SitemapIndexItem, SitemapItem, SitemapItemBase


class RendererBase:
    """The base class for all renderers."""

    def __init__(self, items: Collection[SitemapItemBase]):
        self._items = items

    def render(self) -> str:
        """Get a string representation."""
        raise NotImplementedError

    def write(self, filename: str):
        """Write to a file."""
        raise NotImplementedError

    @property
    def items(self) -> Collection[SitemapItemBase]:
        return self._items


class XMLRendererBase(RendererBase):
    """The base class for XML renderers."""
    set_name: str
    set_attrs: dict

    def render(self) -> str:
        """Render a sitemap."""
        file = BytesIO()
        tree = self.get_tree()
        tree.write(file, xml_declaration=True, encoding='UTF-8')
        return file.getvalue().decode()

    def write(self, filename: str):
        """Write a sitemap to a file."""
        tree = self.get_tree()
        tree.write(filename, xml_declaration=True, encoding='UTF-8')

    def get_tree(self) -> ElementTree.ElementTree:
        url_set = self.get_set()

        for item in self.items:
            url_set.append(item.as_xml())

        return ElementTree.ElementTree(url_set)

    def get_set(self) -> ElementTree.Element:
        return ElementTree.Element(self.set_name, self.set_attrs)


class SitemapIndexXMLRenderer(XMLRendererBase):
    set_name: str = 'sitemapindex'
    set_attrs: dict = {
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    }

    def __init__(self, items: Collection[SitemapIndexItem]):
        super().__init__(items)


class SitemapXMLRenderer(XMLRendererBase):
    set_name: str = 'urlset'
    set_attrs: dict = {
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation':
            'http://www.sitemaps.org/schemas/sitemap/0.9 '
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd',
    }

    def __init__(self, items: Collection[SitemapItem]):
        super().__init__(items)
