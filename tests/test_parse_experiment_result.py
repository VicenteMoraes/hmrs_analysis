
import sys
sys.path.append('./src')

import pandas as pd
from parse_logs.parse_base import LogDir

from parse_logs.parse_experiment_results import parse_experiment_result


def test_parse_experiment_result():
    LogDir.base_data_path = './data'
    trial_run_objects = parse_experiment_result(exec_code='experiment_2021_07_29_15_33_17_run_1')
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