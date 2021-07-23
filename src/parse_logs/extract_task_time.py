import re

from collections import namedtuple
from enum import Enum
from .parse_base import iter_results_dir, parse_log_line, get_next_part, LogDir

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
    navigation_segments = []
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

    def reach_way_point():
        pass

    def end_task(time, robot, skill, end_state):
        curr_task = running_tasks[robot]
        if curr_task.skill != skill:
            failures.append(f'failure parsing "{robot}:{skill}" logs. {exec_code}:{exec_group}:{trial_run_code}')
        else:
            curr_task.end_time = time
            curr_task.end_state = end_state
            running_tasks[robot] = None
    
    def end_mission(tasks_result_to_extend, navigation_segments_to_extend):
        tasks_result_to_extend.extend(tasks_results)
        navigation_segments_to_extend.extend(navigation_segments)
    
    return start_task, reach_way_point, end_task, end_mission

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
    
def parse_skill_life_cycle(content):
    log_line = parse_log_line(content)
    if not log_line.time: # not following 
        return False, None
    
    next_token, rest = get_next_part(log_line.content)
    is_skill = (next_token == 'skill-life-cycle')
    if not is_skill:
        return False, None

    skill, parameters_content = get_next_part(rest)
    status, parameters = extract_status_and_parameters(parameters_content)
    
    skill_line_info = { 'time': log_line.time, 
                        'robot': log_line.entity,
                        'skill': skill,
                        'status': status,
                        'parameters': parameters }

    return True, skill_line_info

# def parse_line(line, time, log_level, entity, content, skill):
#     task_ended, task_started, nav_way_point = None, None, None
#     log_entry = parse_log_line(line)
#         # if is end:
#         #     pass
#     is_skill, skill, params = parse_skill_life_cycle(log_entry)
#     if not is_skill:
#         return task_ended, task_started, nav_way_point
#     if is_skill:
#         task_ended = parse_task_ended(line)
#         task_started = parse_task_started(line)
#         nav_way_point = parse_nav_way_point(line)
#     return task_ended, task_started, nav_way_point

def parse_line_and_call_handle(line, *parse_handle_pairs):
    is_skill, skill_line_info = parse_skill_life_cycle(line)
    if not is_skill:
        return

    for parser, handler in parse_handle_pairs:
        is_match, aditional_info = parser(skill_line_info)
        if is_match:
            handler(**skill_line_info, **aditional_info)
            
def parse_trial_run_logs(exec_code, exec_group, trial_run_code, iter_lines, 
    out_tasks_results, out_nav_segments_results):
    handle_task_start, handle_task_end, reach_way_point, handle_mission_end = \
    init_task_state_interpreter(exec_code, exec_group, trial_run_code)
    
    for line in iter_lines:
        parse_line_and_call_handle(line, 
            # pair fnc for parse/match and handle (in case of a match)
            (parse_task_started, handle_task_start),
            (parse_task_ended, handle_task_end), 
            (parse_nav_way_point, reach_way_point)
        )
    handle_mission_end(out_tasks_results, out_nav_segments_results)


def task_results_parser(exec_code):
    tasks_results: list[TaskResult] = []
    nav_segments_results: list[NavSegmentResult] = []
    folder_patrh = LogDir.get_path(exec_code, 'step2_execution')

    for exec_group, iter_exec_group in iter_results_dir(folder_patrh):
        for trial_run_code, iter_lines in iter_exec_group:
            parse_trial_run_logs(
                exec_code, exec_group, trial_run_code,
                iter_lines, tasks_results, nav_segments_results)

    return tasks_results, nav_segments_results

