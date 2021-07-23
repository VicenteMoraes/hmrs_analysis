import os

from functools import reduce
from collections import namedtuple

import pathlib

class LogDir:
    base_data_path = './data'
    def get_path(*dirs):
        base_path = pathlib.Path().resolve()

        path_args = [ LogDir.base_data_path ]
        dirs = [ _dir for _dir in dirs if _dir] # remove None
        if dirs:
            path_args.extend(dirs)
        path = os.path.join(base_path, *path_args)
        return path

def is_float(potential_float):
    try:
        float(potential_float)
        return True
    except Exception as e:
        return False

def get_next_part(content, separator=','):
    if not separator in content:
        return [None, content]
    else:
        return content.split(separator, 1)

def iter_folders_on_a_folder(folder_path):
    with os.scandir(LogDir.get_path(folder_path)) as entries:
        for entry in entries:
            if entry.is_dir():
                yield entry.name, entry
        return

def iter_log_files_on_a_folder(folder_path):
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith('.log'):
                yield entry.name.removesuffix('.log'), entry
        return

def log_files_paths(exec_code):
    data_path = LogDir.get_path(exec_code, 'step2_execution')
    
    for machine, run_folder_path in iter_folders_on_a_folder(data_path):
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
        [first_part, rest] = get_next_part(rest, ',')
        if not is_float(first_part):
            # not standard log
            return log_entry(None, None, None, line) 
        time = float(first_part)
        [log_level, rest] = get_next_part(rest, ',')
        [entity, log_content] = get_next_part(rest, ',')
        return log_entry(time, log_level, entity, log_content)    
    except Exception as e:
        print(f'cannot parse line {line}')
        raise e

def iter_lines(log_file_path):
    try:
        with open(log_file_path, 'r') as rf:
            try:
                for line in rf.readlines():
                    yield line
                # parse log
            except Exception as err:
                print(f'failure parsing {log_file_path} for ')
                print(err)
        return
    except Exception as e:
        print(f'error reading {log_file_path}:')
        print(e)
        raise e

def iter_results_dir(folder_path):
    def log_files_folder_wrapper(exec_group_folder):
        for log_file_name, file in iter_log_files_on_a_folder(exec_group_folder):
            yield log_file_name, iter_lines(file)
    
    for exec_group_name, exec_group_folder in iter_folders_on_a_folder(folder_path):
        yield exec_group_name, log_files_folder_wrapper(exec_group_folder)
    return