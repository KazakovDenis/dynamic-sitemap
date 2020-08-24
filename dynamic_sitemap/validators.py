from abc import ABCMeta, abstractmethod
from pytz import timezone
from re import match, VERBOSE
from typing import Any, Union
from urllib.parse import urlparse


__all__ = ('CHANGE_FREQ', 'Location', 'LastModified', 'ChangeFrequency', 'Priority', 'Timezone', 'get_validated')

CHANGE_FREQ = 'always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never'


class Parameter(metaclass=ABCMeta):
    """A descriptor to check configuration parameters values"""

    __slots__ = ('storage', )

    assert_msg = None

    def __init__(self, default: Any = None):
        self.storage = default

    @classmethod
    @abstractmethod
    def validate(cls, value):
        pass

    def __get__(self, instance, owner):
        return self.storage

    def __set__(self, instance, value):
        self.storage = self.validate(value)


class Location(Parameter):
    """A descriptor to check loc parameter values"""

    __slots__ = ()

    assert_msg = 'A path is required in location parameter'

    @classmethod
    def validate(cls, value) -> str:
        if value is not None:
            assert isinstance(value, str), cls.assert_msg
            assert urlparse(value).path, cls.assert_msg
        return value


class LastModified(Parameter):
    """A descriptor to check lastmod parameter values according to https://www.w3.org/TR/NOTE-datetime"""

    __slots__ = ()

    assert_msg = 'Last modified should be of the format: YYYY-MM-DD[Thh:mm:ss[±hh:mm]]. Time and timezone is optional.'

    @classmethod
    def validate(cls, value) -> str:
        if value is not None:
            assert isinstance(value, str), cls.assert_msg
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
            assert match(pattern, value, VERBOSE), cls.assert_msg
        return value


class ChangeFrequency(Parameter):
    """A descriptor to check change frequency parameter values"""

    __slots__ = ()

    assert_msg = 'Change frequency should be one of the following: ' + ', '.join(CHANGE_FREQ)

    @classmethod
    def validate(cls, value) -> str:
        if value is not None:
            assert isinstance(value, str), cls.assert_msg
            assert value.casefold() in CHANGE_FREQ, cls.assert_msg
        return value


class Priority(Parameter):
    """A descriptor to check priority parameter values"""

    __slots__ = ()

    assert_msg = 'Priority should be a float between 0.0 and 1.0'

    @classmethod
    def validate(cls, value) -> Union[int, float]:
        if value is not None:
            assert isinstance(value, (int, float)), cls.assert_msg
            assert 0.0 < value <= 1.0, cls.assert_msg
        return value


class Timezone(Parameter):
    """A descriptor to check timezone parameter value"""

    __slots__ = ()

    assert_msg = 'Timezone should be one of pytz.all_timezones items'

    @classmethod
    def validate(cls, value) -> str:
        if value is not None:
            assert isinstance(value, str), cls.assert_msg
            timezone(value)
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
        result['priority'] = Priority.validate(priority)

    return result
