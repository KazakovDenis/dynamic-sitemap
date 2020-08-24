from logging import Logger
from os.path import join
from pathlib import Path
from typing import Union

from .validators import *


__all__ = ('SitemapConfig', 'ConfType', 'DirPathType', 'EXTENSION_ROOT')

ConfType = Union[type, 'SitemapConfig']
DirPathType = Union[str, tuple, list]
EXTENSION_ROOT = Path(__file__).parent.absolute()


class SitemapConfig(dict):
    """A class to set configurations

    DEBUG - if True sets up logging to DEBUG level
    LOGGER - an instance of logging.Logger, creates child of app.logger if not set
    IGNORED - a set of strings which ignored URLs contain
    SOURCE_FILE - str, a path to the template to be copied into templates directory
    CACHE_PERIOD - float, hours; if set, will use already generated data
    TIMEZONE - str, the site's local time zone, one of pytz.all_timezones

    INDEX_CHANGES - str, a change frequency of the index page
    CONTENT_CHANGES - str, a change frequency of pages generated by models
    ALTER_CHANGES - str, a change frequency of other pages with attributes not defined by add_elem

    INDEX_PRIORITY - float, a priority of the index page
    CONTENT_PRIORITY - float, a priority of pages generated by models
    ALTER_PRIORITY - float, a priority of other pages

    APP_ROOT - a str or a collection of folders to application root directory
    STATIC_FOLDER - a str or a collection of folders to make path where to put a STATIC sitemap.xml
    TEMPLATE_FOLDER - where to put a template for a dynamic sitemap
        folders examples:
            STATIC_FOLDER = os.path.join('app', 'static')
            TEMPLATE_FOLDER = ['app', 'templates']
    """
    # Sitemap object attributes
    DEBUG: bool = False
    LOGGER: Logger = None
    IGNORED: set = {'/sitemap.xml', '/admin', '/static', }
    SOURCE_FILE: str = join(EXTENSION_ROOT, 'templates', 'jinja2.xml')
    CACHE_PERIOD: Union[int, float] = None
    TIMEZONE: str = Timezone(default=None)

    INDEX_CHANGES: str = ChangeFrequency(default=None)
    CONTENT_CHANGES: str = ChangeFrequency(default=None)
    ALTER_CHANGES: str = ChangeFrequency(default=None)

    INDEX_PRIORITY: float = Priority(default=1.0)
    CONTENT_PRIORITY: float = Priority(default=None)
    ALTER_PRIORITY: float = Priority(default=None)

    # Application object attributes
    APP_ROOT: DirPathType = ''
    STATIC_FOLDER: DirPathType = None
    TEMPLATE_FOLDER: DirPathType = None

    def from_object(self, obj: ConfType):
        """Updates values from the given object

        :param obj: a class with the same attributes as this one or it's instance
        """
        if isinstance(obj, type) or isinstance(obj, type(self)):
            for key in dir(obj):
                if key.isupper():
                    self[key] = getattr(obj, key)
        else:
            raise NotImplementedError('This type of object is not supported yet')

    def __set__(self, instance, value):
        raise PermissionError(
            'You could not change configuration this way. Use "from_object" method or set specific attribute'
        )

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, item):
        return getattr(self, item)

    def __repr__(self):
        return f'<Sitemap configurations object at {id(self)}>'
