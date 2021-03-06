import pytest
import sys
sys.path.append('./src')

from parse_logs import parse_base
from parse_logs.parse_base import LogDir


def test_parse_log_line():
    line = '0.0,[info],turtlebot5,skill-life-cycle,navigation,(status=RUNNING, parameters=[[-21.0, 16.0, 3.141592653589793, True], [-37.0, 16.0, 1.5707963267948966, True], [-37.0, 21.5, 3.141592653589793, True], [-38.0, 21.5, 0.0, False]])'
    time, log_level, entity, content = parse_base.parse_log_line(line)
    assert time == 0.0
    assert log_level == '[info]'
    assert entity == 'turtlebot5'

def test_parse_log_line_end_sim():
    log_entry = parse_base.parse_log_line('399.566666603,ENDSIM')
    assert pytest.approx(log_entry.time) == 399.5667
    assert pytest.approx(log_entry.content) == 'ENDSIM'

def test_parse_battery_level():
    log_entry = parse_base.parse_log_line('75.60, [INFO], turtlebot1, {"battery-level": "22.92%"}')
    assert pytest.approx(log_entry.time) == 75.60
    getattr(log_entry.content, 'battery-level', None) == '22.92%'


# def test_get_trial_runs_records():
#     LogDir.base_data_path = './tests/data'
#     trial_runs = parser.get_trial_runs('experiment_2021_04_01_16_20_00_run_1')
#     trial_runs = list(trial_runs)
#     assert len(trial_runs) == 8
#     assert trial_runs[0].code == 'aab'
#     assert trial_runs[0].treatment == 'baseline'
#     assert trial_runs[0].factors['avg_speed'] == 'a'


