import os
from datetime import datetime
from unittest.mock import Mock

from dynamic_sitemap.config import EXTENSION_ROOT


PY_TYPES = int, float, complex, tuple, list, set, dict, str, bytes, bytearray
FALSE_INSTANCES = (py_type() for py_type in PY_TYPES)
TRUE_INSTANCES = 1, 1.0, 1+1j, (1,), [1], {1}, {1: 1}, 'str', b'bytes', bytearray(b'array')

TEST_URL = 'http://site.com'
TEST_TIME = datetime.now()
TEST_DATE_STR = TEST_TIME.strftime('%Y-%m-%dT')
TEST_TIME_STR = TEST_TIME.strftime('%Y-%m-%dT%H:%M:%S')
TEST_FOLDER = os.path.join(EXTENSION_ROOT, 'tmp')
TEST_FILE = os.path.join(TEST_FOLDER, 'sitemap.xml')
WRONG_FOLDER = os.path.join(TEST_FOLDER, 'no_such_dir')
os.makedirs(TEST_FOLDER, exist_ok=True)

STATIC_URLS = '/', '/url', '/ign'
DYNAMIC_URLS = '/ign/<slug>', '/api/<int:page>', '/blog/<str:title>'
DEFAULT_URLS = STATIC_URLS + DYNAMIC_URLS

record = Mock('slug', 'updated', 'priority')
rule = Mock(methods=['GET'], rule='/url')


class ORMModel:
    slug = updated = created = True
    # for SQLAlchemy, DjangoORM
    query = objects = Mock(
        all=lambda: [
            record(slug='first-slug', updated=TEST_TIME),
            record(slug='second-slug', updated=TEST_TIME),
        ]
    )

    # for Peewee
    @classmethod
    def select(cls):
        return getattr(cls.query, 'all')()
