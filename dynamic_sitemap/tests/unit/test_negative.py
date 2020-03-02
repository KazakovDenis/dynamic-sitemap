from ..conf import *


@pytest.mark.parametrize('priority', [5, -1, '0.5', 'high'])
def test_priority_01(flask_map, priority):
    with pytest.raises((AssertionError, TypeError)):
        flask_map.add_rule('/app', Model, priority=priority)


def test_default_copy_exception(default_map, request):
    def test_default_copy_exception_teardown():
        default_map.config.DEBUG = True
    request.addfinalizer(test_default_copy_exception_teardown)
    default_map.config.DEBUG = False
    with pytest.raises(FileExistsError):
        default_map._copy_template(template_folder)
