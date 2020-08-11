from ..conf import *


# Config tests
@pytest.mark.parametrize('obj', TRUE_INSTANCES)
def test_config_from_obj(config, obj):
    """Tests configuration's from_object method exception"""
    with pytest.raises(NotImplementedError):
        config.from_object(obj)


def test_config_set(default_map):
    """Tests impossibility of another config object setting"""
    another = SitemapConfig()
    with pytest.raises(PermissionError):
        default_map.config = another


# Base object tests
@pytest.mark.parametrize('priority,error', [
    (5, AssertionError),
    (-1, AssertionError),
    ('0.5', TypeError),
    ('high', TypeError)
])
def test_priority_01(flask_map, priority, error):
    """Assertion error should be raised when priority is not in range 0.0-1.0.
    TypeError should be raised when got non-numeric."""
    with pytest.raises(error):
        flask_map.add_rule('/app', Model, priority=priority)


@pytest.mark.parametrize('folder,error,create', [
        (TEMPLATE_FOLDER, FileExistsError, True),
        ('no_such_dir', PermissionError, False),
    ]
)
def test_default_copy_exceptions(default_map, folder, error, create):
    """Tests exception which should be raised when sitemap.xml already exists"""
    if create:
        with open(TEMPLATE_FILE, 'w') as f:
            f.write('Another sitemap file')

    with pytest.raises(error):
        default_map._copy_template(folder)
