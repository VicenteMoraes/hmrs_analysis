

import json
from collections import namedtuple
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

def log_entry_content_as_json(log_entry):
    log_entry_type = namedtuple('log_entry', 'time log_level entity content')
    time, log_level, entity, content = log_entry
    content = json.loads(content)
    return log_entry_type(time=time, log_level=log_level, entity=entity, content=content)

def filter_log(file_path, entity = None, content_as_json=False):
    def filter_fnc(entry):
        if entity:
            if entry.entity != entity:
                return False
        return True

    if content_as_json:
        parse_func = log_entry_content_as_json
    else:
        parse_func = lambda x: x # noop

    iter_log_entries =  map(parse_log_line, iter_lines(file_path))
    return [ parse_func(log_entry) for log_entry in iter_log_entries if filter_fnc(log_entry)]
