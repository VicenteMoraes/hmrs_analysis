import os
import json 
from copy import deepcopy
from functools import reduce
from collections import namedtuple

import pathlib
from typing import List, Tuple

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

### Util functions 

def arr_to_map(arr, by):
    def set_value(map, obj):
        key = obj[by]
        map[key] = obj
        return map
    return reduce(set_value, arr, {})

def asdic(obj) -> dict:
    if getattr(obj, '_asdict', None):
        return obj._asdict()
    return obj

def merge(obj1, obj2):
    robj = {}
    if obj1:
        robj.update(asdic(obj1))
    if obj2:
        robj.update(asdic(obj2))
    return robj


def unpack(content, ntype, parameters):
    new_type = namedtuple(ntype, parameters)
    params = []
    ncontent = deepcopy(content)
    for param_key in parameters.split(' '):
        try:
            params.append(content.get(param_key, None))
            del ncontent[param_key]
        except Exception as e:
            pass
    return new_type(*params), ncontent
    

def is_float(potential_float):
    try:
        float(potential_float)
        return True
    except Exception as e:
        return False

def flatten(t):
    return [item for sublist in t for item in sublist]

def get_exec_folder_path(exec_code):
    return LogDir.get_path(exec_code, 'step2_execution')

def get_next_part(content, separator=','):
    if not separator in content:
        return [None, content]
    else:
        return content.split(separator, 1)


# iterate over log folders and files

def iter_folders_on_a_folder(folder_path):
    with os.scandir(LogDir.get_path(folder_path)) as entries:
        for entry in entries:
            if entry.is_dir():
                yield entry.name, entry
        return

def iter_log_files_on_a_folder(folder_path):
    entries = os.listdir(folder_path)
    entries.sort()
    for entry_name in entries:
        if not entry_name.endswith('.log'):
            continue
        entry = pathlib.Path(os.path.join(folder_path, entry_name))
        yield entry.name.removesuffix('.log'), entry
            
    return


# def log_files_paths(exec_code):
#     data_path = LogDir.get_path(exec_code, 'step2_execution')
    
#     for machine, run_folder_path in iter_folders_on_a_folder(data_path):
#         for log_file_name, file_path in iter_log_files_on_a_folder(run_folder_path):
#             yield machine, log_file_name, file_path
#     return

def parse_log_line(line):
    '''
    Parse a log line form a log file, interpreting it as 4 parts: time, log_evel, entity, content
    Return content as a tuple
    '''
    log_entry = namedtuple('log_entry', 'time log_level entity content')
    def strip_if_str(pstr):
        if isinstance(pstr, str):
            return pstr.strip()
        else:
            return pstr

    def loads_if_json(content):
        try:
            return json.loads(content)
        except Exception as err:
            return content
    try:
        rest = line
        [first_part, rest] = get_next_part(rest, ',')
        if not is_float(first_part):
            # not standard log
            return log_entry(None, None, None, line) 
        time = float(first_part)
        [log_level, rest] = get_next_part(rest, ',')
        [entity, log_content] = get_next_part(rest, ',')
        return log_entry(time, 
            strip_if_str(log_level),
            strip_if_str(entity),
            loads_if_json(strip_if_str(log_content)))
    except Exception as e:
        print(f'cannot parse line {line}')
        raise e

def get_done_file(log_file: pathlib.Path):
    done_file_name = log_file.name.removesuffix('.log') + '.done'
    done_folder = str(log_file.parent)
    done_file_name = pathlib.Path(os.path.join(done_folder, done_file_name))
    if done_file_name.is_file():
        return done_file_name
    else:
        return None

def sort_line(line):
    [time, _] = get_next_part(line, ',')
    time = float(time)
    return time

def iter_lines(log_file_path):
    try:
        # iterate over .log file
        with open(log_file_path, 'r') as rf:
            try:
                lines = []
                for line in rf.readlines():
                    lines.append(line)
                lines.sort(key=sort_line)
                for line in lines:
                    yield line
                # parse log
            except Exception as err:
                print(f'failure parsing {log_file_path} for ')
                print(err)
        # iterate over .done file
        done_log_file = get_done_file(log_file_path)
        if not done_log_file:
            return
        with open(done_log_file, 'r') as rf:
            try:
                for line in rf.readlines():
                    yield line
                return
            except Exception as err:
                print(f'failure parsing {log_file_path} for ')
                print(err)

    except Exception as e:
        print(f'error reading {log_file_path}:')
        print(e)
        raise e

def iter_results_dir(folder_path):
    def log_files_folder_wrapper(exec_group_folder):
        if '.ignore' in exec_group_folder.path:
            return
        for log_file_name, file in iter_log_files_on_a_folder(exec_group_folder):
            yield log_file_name, iter_lines(file)
    
    for exec_group_name, exec_group_folder in iter_folders_on_a_folder(folder_path):
        yield exec_group_name, log_files_folder_wrapper(exec_group_folder)
    return

def map_field(field, iter):
    return map(lambda obj: getattr(obj.content, field), iter)

def map_value(key, iter):
    return map(lambda r: r[key], iter)

def map_named(name, iter):
    return map(lambda r: r._asdict()[name], iter)


def parse_skill_line(log_line):
    try:
        content_json = log_line.content #json.loads(log_line.content)
        is_skill = not not content_json.get('skill')
        skill = content_json.get('skill', None)
        if skill:
            del content_json['skill']
        skill_life_cycle_field = content_json.get('skill-life-cycle', None)
        status_field = content_json.get('status', None)
        report_status_field = content_json.get('report-status', None)

        if skill_life_cycle_field:
            del content_json['skill-life-cycle']
        if status_field:
            del content_json['status']
        if report_status_field:
            del content_json['report-status']
        status = skill_life_cycle_field or status_field or report_status_field
        return is_skill, skill, status, content_json
    except Exception as e:
        return False, None, None, None


def parse_skill_life_cycle(content):
    log_line = parse_log_line(content)
    if type(log_line.time) != float:
        return False, None
    
    is_skill, skill, status, content = parse_skill_line(log_line)
    if not is_skill:
        return False, asdic(log_line)
    
    skill_line_info = { 'time': log_line.time, 
                        'entity': log_line.entity,
                        'skill': skill,
                        'status': status,
                        'parameters': content }

    return True, skill_line_info


def parse_line_and_call_handle(line, parse_handle_pairs):
    is_skill, content = parse_skill_life_cycle(line)
    for parser, handler, skill_only in parse_handle_pairs:
        if not is_skill:
            if skill_only:
                continue
        try:
            is_match, aditional_info = parser(content)
            if is_match:
                params = merge(content, aditional_info)
                handler(**params)
                #handler(content=content, **aditional_info)
        except Exception as e:
            print(f'failure on parsing the line "{line}"')
            print(e)
    return content.get('time', None)

class Extractor():
    def __init__(self):
        pass
    
    def init_trial(self, exec_code, exec_group, scenario_id, trial_run_code) -> List[Tuple]:
        pass

    def end_trial(self, end_time):
        pass

    def result(self):
        pass

def parse_trial_run_logs(iter_lines, handle_pairs):
    last_time = None
    for line in iter_lines:
        last_time = parse_line_and_call_handle(line, handle_pairs) or last_time
    return last_time

class ExperimentParser():
    def __init__(self, *extractors):
        self.extractors: List[Extractor] = extractors

    def extract(self, exec_code):    
        folder_patrh = get_exec_folder_path(exec_code)
        for exec_group, iter_exec_group in iter_results_dir(folder_patrh):
            for file_name, iter_lines in iter_exec_group:
                scenario_id = None
                try:
                    [scenario_id, trial_run_code] = file_name.split('_')
                except Exception as e:
                    print(f'ignoring "{file_name}.log, wrong name format"')
                    continue
                # init trial parse
                handle_tuples = [ extractor.init_trial(exec_code, exec_group, scenario_id, trial_run_code) for extractor in self.extractors]
                # parse each line
                last_time = parse_trial_run_logs(iter_lines, flatten(handle_tuples))
                # end the trials
                [ extractor.end_trial(last_time) for extractor in self.extractors]
                
                yield reduce(merge, ([{e.name: e.result()} for e in self.extractors ]), {}), \
                      (exec_group, int(scenario_id), trial_run_code)

        return
