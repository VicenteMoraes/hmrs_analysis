import pandas as pd
from functools import reduce
import pathlib
import os
from collections import namedtuple

#global root_data_path
root_data_path = '../data'
exec_code = '!!set_experimennt_run_foleder!!' # refer to the date of generation and number of execution

class TrialRunResult():
    def __init__(self, trial_id, code, machine):
        # identification
        self.trial_id, self.code, self.machine = int(trial_id), code, machine
        # results
        self.ttc = None
        self.failure_time = None
        self.end_state = None
        self.total_time_wall_clock = None
        self.has_failure = False

    def to_dict(self):
        return {
            'trial_id': self.trial_id,
            'code': self.code,
            'machine': self.machine,
            'ttc': self.ttc,
            'failure_time': self.failure_time,
            'end_state': self.end_state,
            'total_time_wall_clock': self.total_time_wall_clock,
            'has_failure': self.has_failure,
        }

def check_float(potential_float):
    try:
        float(potential_float)
        return True
    except ValueError:
        return False

def get_next_part(content, separator):
    if not separator in content:
        return [None, content]
    else:
        return content.split(separator, 1)

def iter_log_files_on_a_folder(folder_path):
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith('.log'):
                yield entry.name.removesuffix('.log'), entry
        return

def iter_folders_on_a_folder(folder_path):
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_dir():
                yield entry.name, entry
        return

def log_files_paths(exec_code):
    exp_data_path = f'{root_data_path}/{exec_code}/step2_execution/'
    
    for machine, run_folder_path in iter_folders_on_a_folder(exp_data_path):
        for log_file_name, file_path in iter_log_files_on_a_folder(run_folder_path):
            yield machine, log_file_name, file_path
    return

def parse_log_line(line):
    '''
    Parse a log line form a log file, interpreting it as 4 parts: time, log_evel, entity, content
    Return content as a tuple
    '''
    log_entry = namedtuple('log_entry', 'time log_level entity content')
    try:
        rest = line
        [first_part, rest] = rest.split(',', 1)
        if not check_float(first_part):
            # not standard log
            return log_entry(None, None, None, line) 
        time = float(first_part)
        [log_level, rest] = get_next_part(rest, ',')
        [entity, log_content] = get_next_part(rest, ',')
        return log_entry(time, log_level, entity, log_content)    
    except Exception as e:
        print(f'cannot parse line {line}')
        print(e)
        raise e

def parse_end_line(trial_run_result, log_entry):
    '''
    Get end_state and total_time_wall_clock
    '''
    if log_entry.entity != "simulation closed":
        # not of interest here
        return
    else:
        content_parts = log_entry.content.split(',')
        run_data_end_state = content_parts[0] # either reach-target, timeout, failure-bt
        run_total_time_wall_clock = float(content_parts[1].split('=')[1])
        trial_run_result.end_state = run_data_end_state
        if run_data_end_state == 'timeout':
            trial_run_result.has_failure = True
        trial_run_result.total_time_wall_clock = run_total_time_wall_clock
    

def parse_inventory_log(trial_run_result, log_entry):
    '''
    Get total_time from 'sample-received' log
    '''

    if log_entry.entity != 'Inventory' or \
        '(status=sample-received)' not in log_entry.content:
        # not of interest here
        return
    else:
        time_on_sample_received = float(log_entry.time)
        trial_run_result.ttc = time_on_sample_received
    
def parse_first_failure(trial_run_result, log_entry):
    '''
    Get time of the first failure
    '''
    if 'status=Status.FAILURE' in log_entry.content:
        # TODO should differentiate a low battery in case of not assigned robot?
        trial_run_result.has_failure = True
        if not trial_run_result.failure_time or \
            log_entry.time < trial_run_result.failure_time:
            trial_run_result.failure_time = log_entry.time

def parse_line(trial_run_result, line):
    log_entry = parse_log_line(line)
    
    parse_first_failure(trial_run_result, log_entry)
    parse_inventory_log(trial_run_result, log_entry)
    parse_end_line(trial_run_result, log_entry)
    return trial_run_result


def parse_folder_of_log_files(log_files_path):
    ''' 
    Read a logs from a folder to a dataframe
    '''
    trial_runs = []
    for machine, log_file_name, log_file_path in log_files_path:
        [trial_id, code] = log_file_name.split('_')
        trial_run_result = TrialRunResult(trial_id=trial_id, code=code, machine=machine)
        
        with open(log_file_path, 'r') as rf:    
            # parse log
            print(trial_id, code, machine, trial_run_result)
            # exit_line = [line for line in rf.readlines() if "simulation closed" in line]
            trial_result = reduce(parse_line, rf, trial_run_result)
            trial_runs.append(trial_result)
    return trial_runs


# baseline_results_df = read_log_files_to_dataframe(log_files_paths('baseline'))
# planned_results_df = read_log_files_to_dataframe(log_files_paths('planned'))
# dataframe = pd.DataFrame.from_records([tr.to_dict() for tr in trial_runs])
