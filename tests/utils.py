from datetime import datetime
from unittest.mock import Mock

from dynamic_sitemap.core import DynamicSitemapBase


PY_TYPES = int, float, complex, tuple, list, set, dict, str, bytes, bytearray
FALSE_INSTANCES = (py_type() for py_type in PY_TYPES)
TRUE_INSTANCES = 1, 1.0, 1 + 1j, (1,), [1], {1}, {1: 1}, 'str', b'bytes', bytearray(b'array')

TEST_URL = 'http://site.com'
TEST_TIME = datetime.now()
TEST_DATE_STR = TEST_TIME.strftime('%Y-%m-%dT')
TEST_TIME_STR = TEST_TIME.strftime('%Y-%m-%dT%H:%M:%S')

QUERYSET = Mock(
    all=lambda: [
        Mock(slug='first-slug', updated=TEST_TIME),
        Mock(slug='second-slug', updated=TEST_TIME),
    ],
)

ORMModel = Mock(name='ORMModel', objects=QUERYSET, select=QUERYSET.all, query=QUERYSET)


class SitemapMock(DynamicSitemapBase):

    def _get_rules(self) -> list:
        return []

    def view(self):
        return 'response'
