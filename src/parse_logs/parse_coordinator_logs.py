

import json
from collections import namedtuple
from typing import List

from flatten_json import flatten
from parse_logs.parse_base import LogDir, iter_folders_on_a_folder, iter_log_files_on_a_folder, iter_lines, parse_log_line

exp_design = namedtuple('exp_design', 'factors scenarios trials')

def iter_coordinator_logs_in_scenario(exec_code):
    data_path = LogDir.get_path(exec_code, 'step1_experiment_generation', 'logs')
    
    for scenario_code, run_folder_path in iter_folders_on_a_folder(data_path):
        for log_file_name, file_path in iter_log_files_on_a_folder(run_folder_path):
            yield scenario_code, file_path
    return

def read_design(exec_code) -> exp_design:
    design_json_path = LogDir.get_path(exec_code, 'step1_experiment_generation', 'design.json')
    trials_json_path = LogDir.get_path(exec_code, 'step1_experiment_generation', 'trials.json')
    scenarios_json_path = LogDir.get_path(exec_code, 'step1_experiment_generation', 'scenarios.json')
    with open(design_json_path) as design_json_file:
        factors = json.load(design_json_file)
    with open(trials_json_path) as trials_json_file:
        trials = json.load(trials_json_file)
    with open(scenarios_json_path) as scenarios_json_file:
        scenarios = json.load(scenarios_json_file)

    return exp_design(factors, scenarios, trials)

def get_flat_design(exec_code) -> List[dict]:
    exp_design = read_design(exec_code)
    trials_designs = [flatten({'code': trial['code'],
                                'scenario_id': trial['id'], 
                                'factors': trial['factors'],
                                'treatment': 'planned' if 'p' in trial['code'] else 'baseline'
                                    }) for trial in exp_design.trials]
    return trials_designs
    

def filter_log(file_path, entity = None):
    def filter_fnc(entry):
        if entity:
            if entry.entity != entity:
                return False
        return True


    iter_log_entries =  map(parse_log_line, iter_lines(file_path))
    return [ log_entry for log_entry in iter_log_entries if filter_fnc(log_entry)]
