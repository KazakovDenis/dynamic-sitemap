from pathlib import Path
from typing import Optional, Union

from . import helpers
from .exceptions import SitemapValidationError
from .validators import ChangeFrequency, Priority, Timezone


ConfType = Optional[Union[type, 'SitemapConfig']]
EXTENSION_ROOT = Path(__file__).parent.absolute()


class SitemapConfig(dict):
    """The class to set configurations."""
    #: str, a path to write sitemap
    FILENAME: str = ''
    #: str, a base URL such as 'http://site.com'
    BASE_URL: str = ''
    #: set, a set of strings which ignored URLs start with
    IGNORED: set = {'/sitemap.xml', '/admin', '/static'}
    #: int or float, hours; if set, will use already generated data
    CACHE_PERIOD: Union[int, float] = 0
    #: str, str, the site's local time zone, one of pytz.all_timezones
    TIMEZONE = Timezone(default=None)
    #: str, a change frequency of the index page
    INDEX_CHANGES = ChangeFrequency(default=None)
    #: str, a change frequency of pages generated by models
    CONTENT_CHANGES = ChangeFrequency(default=None)
    #: str, a change frequency of other pages with attributes not defined by add_items
    ALTER_CHANGES = ChangeFrequency(default=None)
    #: int or float, a priority of the index page
    INDEX_PRIORITY = Priority(default=1.0)
    #: int or float, a priority of pages generated by models
    CONTENT_PRIORITY = Priority(default=None)
    #: int or float, a priority of other pages
    ALTER_PRIORITY = Priority(default=None)

    def from_object(self, obj: ConfType):
        """Updates values from the given object.

        :param obj: a class with the same attributes as this one or it's instance
        """
        if obj is None:
            return

        self._validate(obj)

        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def _validate(self, obj: ConfType):
        if not isinstance(obj, (type, type(self))):
            raise SitemapValidationError('This type of object is not supported yet')

        filename = getattr(obj, 'FILENAME', None)
        if filename and not Path(filename).parent.exists():
            raise SitemapValidationError(f'Bad filename: {filename}')

        base_url = getattr(obj, 'BASE_URL', None)
        if base_url and not helpers.check_url(base_url):
            raise SitemapValidationError(f'Bad URL: {base_url}')

        cache_period = getattr(obj, 'CACHE_PERIOD', None)
        if cache_period and not (
            isinstance(cache_period, (int, float))
            and cache_period > 0.0
        ):
            raise SitemapValidationError('CACHE_PERIOD should be a float greater than 0.0')

    def __set__(self, instance, value):
        raise SitemapValidationError(
            'You could not change configuration this way. Use "from_object" method or set specific attribute',
        )

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return f'<Sitemap configuration of "{self.BASE_URL}">'
