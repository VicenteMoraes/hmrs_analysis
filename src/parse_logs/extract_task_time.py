import re
import json
from functools import reduce

from copy import deepcopy

from collections import namedtuple
from enum import Enum
from typing import List, Tuple

from parse_logs.parser import TrialRun
from .parse_base import get_exec_folder_path, iter_results_dir, parse_log_line, get_next_part, LogDir

class MissionData:
    def __init__(self):
        self.tasks_result = []
        self.navigation_segments = []

class TaskEndState(Enum):
    SUCCESS = True
    FAILURE = False
    UNKNOWN = None

class TaskResult:
    def __init__(self, exec_code, trial_run_code, exec_group, robot,
                start_time, skill, parameters):
        self.exec_code = exec_code
        self.trial_run_code = trial_run_code
        self.exec_group = exec_group
        self.robot = robot
        self.start_time = start_time
        self.skill = skill
        self.parameters = parameters
        self.expent_time = None
        self.end_time = None
        self.end_state: TaskEndState = None

class NavSegmentResult:
    def __init__(self, origin, destination, distance, robot, time):
        self.origin = origin
        self.destination = destination
        self.distance = distance
        self.robot = robot
        self.time = time


task_started = namedtuple('task_started', 'robot skill parameters')
task_ended = namedtuple('task_ended', 'robot skill end_state time')

def init_task_state_interpreter(exec_code, exec_group, trial_run_code):
    running_tasks: dict[str, TaskResult] = {}
    
    tasks_results = []
    failures = []

    def start_task(time, robot, skill, parameters, **_):
        if running_tasks.get(robot):
            print(f'{robot} started {skill} without logging end of {running_tasks[robot].skill}')
            end_task(time, robot, running_tasks[robot].skill, end_state='SUCCESS')
            
        task = TaskResult(
            exec_code=exec_code, trial_run_code=trial_run_code, exec_group=exec_group,
            robot=robot, skill=skill, parameters=parameters, start_time=time
        )
        tasks_results.append(task)
        running_tasks[robot] = task

    def end_task(time, robot, skill, end_state):
        curr_task = running_tasks[robot]
        if curr_task.skill != skill:
            failures.append(f'failure parsing "{robot}:{skill}" logs. {exec_code}:{exec_group}:{trial_run_code}')
        else:
            curr_task.end_time = time
            curr_task.end_state = end_state
            running_tasks[robot] = None
    
    def end_trial(tasks_result_to_extend):
        # TODO handle not detected end of tasks
        tasks_result_to_extend.extend(tasks_results)

    return start_task, end_task, end_trial


def parse_task_started(skill_log_info):
    return skill_log_info['status'] == 'STARTED', {}

def parse_task_ended(line):
    return False, None

def parse_nav_way_point(line):
    return False, None

def extract_status_and_parameters(text):
    try:
        content = re.sub(r"\((.*?)\)", r"\1", text) # remove parenteses
        p = re.compile(r"status=([\w\.]*),")
        status = p.findall(content).pop(-1)

        p2 = re.compile(r"parameters=(.*)")
        parameters = p2.findall(content).pop(-1)
        return status, eval(parameters)
    except Exception as e:
        print(e)
        return None, None

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
    


def parse_skill_line(log_line):
    try:
        content_json = json.loads(log_line.content)
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

def merge(obj1, obj2):
    robj = {}
    if obj1:
        if getattr(obj1, '_asdict', None):
            obj1 = obj1._asdict()
        robj.update(obj1)
    if obj2:
        if getattr(obj2, '_asdict', None):
            obj2 = obj2._asdict()
        robj.update(obj2)
    return robj

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


class Extractor():
    def __init__(self):
        pass
    
    def init_trial(self, exec_code, exec_group, scenario_id, trial_run_code) -> List[Tuple]:
        pass

    def end_trial(self):
        pass

    def result(self):
        pass


def asdic(obj) -> dict:
    if getattr(obj, '_asdict', None):
        return obj._asdict()
    return obj

def check_all_fields_on(origin, model):
    for key, value in model.items():
        if value != asdic(origin).get(key, None):
            return False
    return True
    
## 
def parse_sample_received(skill_log_info):
    print(skill_log_info['entity'])
    if skill_log_info['entity'] == 'lab_arm':
        return True, None
    return False, None

def parse_sample_received(skill_log_info):
    if skill_log_info['entity'] == 'lab_arm' and \
        skill_log_info.get('status', None) == 'sample-received':
        return True, {'end_state': 'success'} 
    else:
        return False, None

def parse_low_battery(skill_log_info):
    if skill_log_info.get('content', None) == 'ENDLOWBATT':
        return True, {'end_state': 'low-battery', 'has_failure': True}
    return False, None


def parse_no_skill_failure(skill_log_info):
    if skill_log_info.get('status', None) == 'UNAVAILABLE-SKILL':
        return True, {'end_state': 'no-skill', 'has_failure': True}
    else:
        return False, None

def parse_timeout_sim(skill_log_info):
    if skill_log_info.get('content', None) == 'ENDTIMEOUTSIM':
        return True, {'end_state': 'timeout-sim'}
    return False, None

def parse_timeout_wallclock(skill_log_info):
    if skill_log_info.get('entity') == 'trial-watcher' and \
        'False: wall-clock=' in skill_log_info.get('content', None):
        return True, {'end_state': 'timeout-wall'}
    return False, None

def parse_mission_end(skill_log_info):
    return False, None
    

def init_trial_state_interpreter(exec_group, scenario_id, trial_run_code):
    trial_run_result = TrialRun(exec_group=exec_group, scenario_id=scenario_id, code=trial_run_code)

    def handle_mission_end_success(end_state, time, **kargs):
        trial_run_result.end_state = end_state
        trial_run_result.ttc = time

    def handle_mission_end_failure(end_state, time, **kargs):
        trial_run_result.end_state = end_state
        trial_run_result.failure_time = time
        trial_run_result.has_failure = True

    return handle_mission_end_success, handle_mission_end_failure, trial_run_result

class TaskStateExtractor(Extractor):
    def __init__(self):
            self.tasks_results: list[TaskResult] = []
            self.handle_task_start, self.handle_task_end, self.ctx_end_trial = None, None, None
    

    def init_trial(self, exec_code, exec_group, scenario_id, trial_run_code):
        self.handle_task_start, self.handle_task_end, self.ctx_end_trial = \
            init_task_state_interpreter(exec_code, exec_group, trial_run_code)
        
        # pair fnc for parse/match and handle (in case of a match)            
        return  [(parse_task_started, self.handle_task_start),
                (parse_task_ended, self.handle_task_end),
                (parse_mission_end, self.handle_task_on_mission_end)]

    def end_trial(self):
        self.ctx_end_trial(self.tasks_results)
        self.handle_task_start, self.handle_task_end, self.ctx_end_trial = None, None, None


class TrialEndStateExtractor(Extractor):
    name = 'trial_end_state'
    def __init__(self):
        self.name = TrialEndStateExtractor.name
        self.trial_run: TrialRun = None

    def init_trial(self, exec_code, exec_group, scenario_id, trial_run_code):
        self.handle_mission_success_end, self.handle_mission_fail_end, curr_trial = \
            init_trial_state_interpreter(exec_group, scenario_id, trial_run_code)
        
        self.trial_run = curr_trial

        # each parser is called for each line, when a match is found, 
        #   the handle is called with the appropriate end_state
        return [(parse_sample_received, self.handle_mission_success_end, True),
                (parse_low_battery, self.handle_mission_fail_end, False),
                (parse_timeout_wallclock, self.handle_mission_fail_end, False),
                (parse_timeout_sim, self.handle_mission_fail_end, False),
                (parse_no_skill_failure, self.handle_mission_fail_end, False)]
    
    # def end_trial():
    #     pass

    def result(self):
        return self.trial_run

def flatten(t):
    return [item for sublist in t for item in sublist]


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
                self.parse_trial_run_logs(iter_lines, flatten(handle_tuples))
                # end the trials
                [ extractor.end_trial() for extractor in self.extractors]
                
                yield reduce(merge, map(lambda e: {e.name: e.result()}, self.extractors), {})

        return

    @staticmethod
    def parse_trial_run_logs(iter_lines, handle_pairs):
        for line in iter_lines:
            parse_line_and_call_handle(line, handle_pairs)