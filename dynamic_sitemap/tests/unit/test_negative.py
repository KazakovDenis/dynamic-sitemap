from ..conftest import *


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
def test_priority(default_map, priority, error):
    """Assertion error should be raised when priority is not in range 0.0-1.0.
    TypeError should be raised when got non-numeric."""
    with pytest.raises(error):
        default_map.add_rule('/app', Model, priority=priority)


def test_default_copy_file_exists(request, default_map):
    """Tests exception which should be raised when sitemap.xml already exists"""
    def teardown():
        os.remove(TEST_FILE)
    request.addfinalizer(teardown)
    
    with open(TEST_FILE, 'w') as f:
        f.write('Another sitemap file')

    with pytest.raises(FileExistsError):
        default_map._copy_template()


def test_default_copy_permission(request, default_map):
    """Tests exception which should be raised when putting into not existing directory"""
    def teardown():
        default_map.config.TEMPLATE_FOLDER = TEST_FOLDER
    request.addfinalizer(teardown)

    default_map.config.TEMPLATE_FOLDER = 'no_such_dir'
    with pytest.raises(PermissionError):
        default_map._copy_template()
