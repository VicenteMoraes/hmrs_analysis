
import sys
sys.path.append('./src')

import pandas as pd
from parse_logs.parse_base import LogDir

from parse_logs.extract_experiment_result import parse_experiment_result


def test_parse_experiment_result():
    LogDir.base_data_path = './tests/data'
    trial_run_objects = parse_experiment_result(exec_code='experiment_2021_07_29_16_15_21_run_1')
    no_state = []
    no_executor= []
    trial_runs = []
    for trial_run in trial_run_objects:
        if not trial_run.end_state:
            no_state.append(trial_run)
        if not trial_run.executor:
            no_executor.append(trial_run)
        trial_runs.append(trial_run)
    # load trials run to dict (it can take a while)
    trial_run_dicts = [trial_run.to_dict() for trial_run in trial_runs]
    trial_run_dicts.sort(key=lambda tr: tr['scenario_id'])
    print(trial_run_dicts)

    trial_run_df = pd.DataFrame.from_records(trial_run_dicts)
    print(trial_run_df.to_csv())

def test_extract_experimen():
    LogDir.base_data_path = './tests/data'
    trial_run_objects = parse_experiment_result(exec_code='experiment_2021_07_29_16_15_21_run_1')
    a = next(tr for tr in trial_run_objects if tr.end_state == 'success')
    assert a
    
def test_parse_battery_level():
    LogDir.base_data_path = './tests/data'
    trial_run_objects = parse_experiment_result(exec_code='experiment_2021_07_29_16_15_21_run_1')
    first = next(trial_run_objects).to_dict()
    assert first['end_battery_level']


def test_extract_experiment_success():
    LogDir.base_data_path = './tests/data'
    trial_run_objects = parse_experiment_result(exec_code='experiment_2021_07_29_16_15_21_run_1')
    successses = [tr for tr in trial_run_objects if tr.end_state == 'success']
    for succ in successses:
        assert succ.to_dict()['ttc']


def test_extract_all_have_end_state():
    #LogDir.base_data_path, exec_code = './data', 'experiment_2021_07_29_15_33_17_run_1'
    LogDir.base_data_path, exec_code = './tests/data', 'experiment_2021_07_29_16_15_21_run_1'
    trial_run_objects = parse_experiment_result(exec_code=exec_code)
    no_end_state = [tr for tr in trial_run_objects if not tr.end_state]
    assert not no_end_state
