from conftest import *


@pytest.mark.parametrize('priority', [5, -1, '0.5', 'high'])
def test_priority_01(flask_map, priority):
    with pytest.raises((AssertionError, TypeError)):
        flask_map.add_rule('/app', Model, priority=priority)
