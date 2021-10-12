from typing import Optional
from xml.etree import ElementTree

from .validators import ChangeFrequency, LastModified, Location, Priority


class SitemapItemBase:
    """Thr base class for sitemap and sitemap index items."""
    loc = Location()
    lastmod = LastModified()

    def __init__(self, loc: str, lastmod: Optional[str] = None):
        self.loc = loc
        self.lastmod = lastmod

    def __hash__(self):
        return hash(self.loc)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.loc == other.loc
        return False

    def __repr__(self):
        return f'<{self.__class__.__name__} loc="{self.loc}">'

    def as_xml(self):
        """Get an XML representation."""
        raise NotImplementedError


class SitemapIndexItem(SitemapItemBase):
    """The class representing an item of a sitemap index."""

    def as_xml(self):
        """Get an XML representation."""
        element = ElementTree.Element('sitemap')
        ElementTree.SubElement(element, 'loc').text = self.loc

        if self.lastmod:
            ElementTree.SubElement(element, 'lastmod').text = self.lastmod

        return element


class SitemapItem(SitemapItemBase):
    """The class representing an item of a sitemap."""
    changefreq = ChangeFrequency()
    priority = Priority()

    def __init__(self, loc: str,
                 lastmod: Optional[str] = None,
                 changefreq: Optional[str] = None,
                 priority: Optional[float] = None):
        super().__init__(loc, lastmod)
        self.changefreq = changefreq
        self.priority = priority

    def as_xml(self):
        """Get an XML representation."""
        element = ElementTree.Element('url')
        ElementTree.SubElement(element, 'loc').text = self.loc

        if self.lastmod:
            ElementTree.SubElement(element, 'lastmod').text = self.lastmod

        if self.changefreq:
            ElementTree.SubElement(element, 'changefreq').text = self.changefreq

        if self.priority:
            ElementTree.SubElement(element, 'priority').text = str(self.priority)

        return element
