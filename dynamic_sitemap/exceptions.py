class SitemapError(Exception):
    pass


class SitemapValidationError(SitemapError):
    pass


class SitemapItemError(SitemapError):
    pass


class SitemapIOError(SitemapError):
    pass
