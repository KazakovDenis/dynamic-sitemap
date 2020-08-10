from ..conf import *


# Config tests
@pytest.mark.parametrize('obj', TRUE_INSTANCES)
def test_config_from_obj(config, obj):
    """Tests configuration's from_object method exception"""
    with pytest.raises(NotImplementedError):
        config.from_object(obj)


# Base object tests
@pytest.mark.parametrize('priority', [5, -1, '0.5', 'high'])
def test_priority_01(flask_map, priority):
    """Assertion error should be raised when priority is not in range 0.0-1.0.
    TypeError should be raised when got non-numeric."""
    with pytest.raises((AssertionError, TypeError)):
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
