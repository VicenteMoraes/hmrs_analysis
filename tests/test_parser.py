import pytest

from src.parse_logs import parser

def test_parse_log_line():
    line = '0.0,[info],turtlebot5,skill-life-cycle,navigation,(status=RUNNING, parameters=[[-21.0, 16.0, 3.141592653589793, True], [-37.0, 16.0, 1.5707963267948966, True], [-37.0, 21.5, 3.141592653589793, True], [-38.0, 21.5, 0.0, False]])'
    time, log_level, entity, content = parser.parse_log_line(line)
    assert time == 0.0
    assert log_level == '[info]'
    assert entity == 'turtlebot5'

def test_parse_log_line_end_sim():
    log_entry = parser.parse_log_line('399.566666603,ENDSIM')
    assert pytest.approx(log_entry.time) == 399.5667
    assert pytest.approx(log_entry.content) == 'ENDSIM'

def test_parse_folder_of_log_files():
    parser.root_data_path = './tests/data'
    parser.exec_code = ''
    records = parser.parse_folder_of_log_files(parser.log_files_paths(
        exec_code='experiment_2021_04_01_16_20_00_run_1'))
    assert len(records) == 8
    records[0].trial_id = 1

