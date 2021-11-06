import enum
from re import VERBOSE, match
from typing import Generic, List, Optional, TypeVar, Union
from urllib.parse import urlparse

from pytz import UnknownTimeZoneError, timezone

from .exceptions import SitemapValidationError


class ChangeFreq(enum.Enum):
    ALWAYS = 'always'
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    NEVER = 'never'

    @classmethod
    def values(cls) -> List[str]:
        return [i.value for i in cls]


Value = TypeVar('Value')


class Parameter(Generic[Value]):
    """A descriptor to check configuration parameters values"""
    __slots__ = ('default', 'storage')

    def __init__(self, default: Optional[Value] = None):
        self.default = default
        self.storage: dict = {}

    def __get__(self, instance, owner) -> Value:
        return self.storage.get(id(instance), self.default)

    def __set__(self, instance, value: Value):
        self.storage[id(instance)] = self.validate(value)

    @classmethod
    def validate(cls, value: Value) -> Value:
        return value


class Location(Parameter):
    """A descriptor to check loc parameter values"""
    __slots__ = ()

    @classmethod
    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        if not (
            isinstance(value, str) and urlparse(value).path
        ):
            raise SitemapValidationError('A path is required in location parameter')
        return value


class LastModified(Parameter):
    """A descriptor to check lastmod parameter values according to https://www.w3.org/TR/NOTE-datetime"""
    __slots__ = ()

    @classmethod
    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        pattern = r"""
        (?P<date>
            (?P<year>20[0-9]{2})-
            (?P<month>0[0-9]|1[0-2])-
            (?P<day>[0-2][0-9]|3[0-1])
        )
        (T
            (?P<time>
                (?P<hours>[0-1][0-9]|2[0-3]):
                (?P<minutes>[0-5][0-9]):
                (?P<seconds>[0-5][0-9])
            )
            (?P<timezone>[+-][0-5][0-9]:[0-5][0-9])?
        )?
        """

        if not (
            isinstance(value, str) and match(pattern, value, VERBOSE)
        ):
            raise SitemapValidationError(
                'Last modified should be of the format: YYYY-MM-DD[Thh:mm:ss[±hh:mm]]. Time and timezone is optional.',
            )
        return value


class ChangeFrequency(Parameter):
    """A descriptor to check change frequency parameter values"""
    __slots__ = ()

    @classmethod
    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        if not (
            isinstance(value, str)
            and (value.casefold() in ChangeFreq.values())
        ):
            raise SitemapValidationError(
                'Change frequency should be one of the following: ' + ', '.join(ChangeFreq.values()),
            )
        return value


class Priority(Parameter):
    """A descriptor to check priority parameter values"""
    __slots__ = ()

    @classmethod
    def validate(cls, value: Optional[Union[int, float]]) -> Optional[Union[int, float]]:
        if value is None:
            return None

        if not (
            isinstance(value, (int, float))
            and (0.0 < value <= 1.0)
        ):
            raise SitemapValidationError('Priority should be a float between 0.0 and 1.0')
        return value


class Timezone(Parameter):
    """A descriptor to check timezone parameter value"""
    __slots__ = ()

    @classmethod
    def validate(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        msg = 'Timezone should be one of pytz.all_timezones items'

        if not isinstance(value, str):
            raise SitemapValidationError(msg)

        try:
            timezone(value)
        except UnknownTimeZoneError:
            raise SitemapValidationError(msg)
        return value


def get_validated(loc=None, lastmod=None, changefreq=None, priority=None) -> dict:
    """Validates sitemap's XML tags values"""
    result = {}

    if loc:
        result['loc'] = Location.validate(loc)

    if lastmod:
        result['lastmod'] = LastModified.validate(lastmod)

    if changefreq:
        result['changefreq'] = ChangeFrequency.validate(changefreq)

    if priority:
        result['priority'] = Priority.validate(priority)    # type: ignore

    return result
