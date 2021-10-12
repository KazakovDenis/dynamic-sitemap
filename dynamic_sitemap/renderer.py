import logging
from abc import ABC, abstractmethod
from io import BytesIO
from typing import BinaryIO, Collection, Optional
from xml.etree import ElementTree

from .main import Record
from .validators import validate_io


logger = logging.getLogger(__name__)

XML_ATTRS = {
    'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'xsi:schemaLocation':
        'http://www.sitemaps.org/schemas/sitemap/0.9 '
        'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd',
}


class RendererBase(ABC):

    def __init__(self, records: Collection[Record]):
        self._records = records

    @abstractmethod
    def render(self, *args, **kwargs) -> str:
        """Render a sitemap."""
        pass

    def get_tree(self) -> ElementTree.ElementTree:
        url_set = self.get_url_set()

        for record in self.records:
            url_set.append(record.as_xml())

        return ElementTree.ElementTree(url_set)

    @staticmethod
    def get_url_set() -> ElementTree.Element:
        return ElementTree.Element('urlset', XML_ATTRS)

    @property
    def records(self):
        return self._records


class XMLRenderer(RendererBase):

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
