import pytest
import sys
sys.path.append('./src')

from parse_logs.parse_base import LogDir
from parse_logs.parse_coordinator_logs import filter_log, get_flat_design, iter_coordinator_logs_in_scenario, read_design


def test_iterate_over_files():
    LogDir.base_data_path = './tests/data'
    codes = []
    for scenario_code, log_file in iter_coordinator_logs_in_scenario(exec_code='experiment_2021_04_01_16_20_00_run_1'):
        codes.append(scenario_code)
    assert len(codes) == 3

def test_read_design():
    LogDir.base_data_path = './tests/data'
    
    exp = read_design(exec_code='experiment_2021_04_01_16_20_00_run_1')
    assert exp.factors
    assert exp.trials

def test_get_flat_design():
    LogDir.base_data_path = './tests/data'
    
    exp = get_flat_design(exec_code='experiment_2021_04_01_16_20_00_run_1')
    assert exp

def test_filter_line_by_entity():
    LogDir.base_data_path = './tests/data'
    exec_code='experiment_2021_04_01_16_20_00_run_1'
    design_json_path = LogDir.get_path(exec_code, 
        'step1_experiment_generation', 'logs', 'aap', 'cf_request_0.log')

    incompatible_workers = filter_log(design_json_path, entity='incompatible_workers', content_as_json=True)
    assert len(incompatible_workers) == 4

