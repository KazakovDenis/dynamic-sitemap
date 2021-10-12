import logging
from io import BytesIO
from typing import BinaryIO, Collection, Optional
from xml.etree import ElementTree

from .main import Page
from .validators import validate_io


logger = logging.getLogger(__name__)


class RendererBase:
    """The base class for all renderers."""

    def __init__(self, items: Collection):
        self._items = items

    def render(self, *args, **kwargs) -> str:
        """Get a string representation."""

    @property
    def items(self) -> Collection:
        return self._items


class XMLRendererBase(RendererBase):
    """The base class for XML renderers."""
    set_name: str
    set_attrs: dict

    def get_tree(self):
        raise NotImplementedError

    def get_set(self):
        return ElementTree.Element(self.set_name, self.set_attrs)


class SitemapIndexXMLRenderer(XMLRendererBase):
    set_name: str = 'sitemapindex'
    set_attrs: dict = {
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    }

    def get_tree(self):
        raise NotImplementedError


class SitemapXMLRenderer(XMLRendererBase):
    set_name: str = 'url_set'
    set_attrs: dict = {
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation':
            'http://www.sitemaps.org/schemas/sitemap/0.9 '
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd',
    }

    def __init__(self, pages: Collection[Page]):
        super().__init__(pages)

    def render(self, file: Optional[BinaryIO] = None) -> str:
        """Render a sitemap."""
        if file is not None:
            validate_io(file)
        else:
            file = BytesIO()
        tree = self.get_tree()

        try:
            tree.write(file, xml_declaration=True, encoding='UTF-8')
            file.seek(0)
            xml = file.read().decode()
        finally:
            file.close()

        return xml

    def get_tree(self) -> ElementTree.ElementTree:
        url_set = self.get_set()

        for page in self.items:
            url_set.append(page.as_xml())

        return ElementTree.ElementTree(url_set)
