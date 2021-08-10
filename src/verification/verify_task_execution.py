from enum import Enum
from functools import reduce
from parse_logs.extract_experiment_result import TrialEndStateExtractor
from parse_logs.extract_tasks_exec_result import TaskResult, TaskStateExtractor
from parse_logs.parse_base import ExperimentParser, arr_to_map, parse_line_and_call_handle
from parse_logs.parse_coordinator_logs import read_design

# from parse_logs.parse_trial_run import iter_exec_logs_in_experiment

# Task Execution checks
class task_execution_check(Enum):
    assigned_robots_received_local_mission = 0
    tasks_were_executed_in_order = 1 # the plan was followed
    completed_plans_leaded_to_mission_success = 2 # tasks are executed, 

robot_aliases = {
    'r1': ['turtlebot1'],
    'r2': ['turtlebot2'],
    'r3': ['turtlebot3'],
    'r4': ['turtlebot4'],
    'r5': ['turtlebot5'],
    'r6': ['turtlebot6']
}

# property and function that verify this property
def get_verification_pairs():
    verification_pairs = [
        (task_execution_check.assigned_robots_received_local_mission, check_assigned_robots_received_local_mission),
        (task_execution_check.tasks_were_executed_in_order, check_tasks_were_executed_in_order)
        ]
    return verification_pairs

def check_task_execution(exec_code):    

    design = read_design(exec_code)
    trial_design_map = arr_to_map(design.trials, by='code')
    
    verification  =  {}
    tsx = TaskStateExtractor()
    ep = ExperimentParser(tsx)
    # for each parsed log
    for extracted, meta in ep.extract(exec_code = exec_code):        
        exec_group, scenario_id, code = meta
        trial_run_results: list[TaskResult] = extracted[tsx.name]
        
        trial_design = trial_design_map[code] # design of this trial
        init_verification(verification=verification, exec_group=exec_group, code=code)
        # check trial execution
        for property, check_fnc in get_verification_pairs():
            verification[exec_group][code][property.name] = \
                check_fnc(trial_design, trial_run_results)
            
            # TODO compare estimates

    # TODO check all scenarios where checked
    return verification

def init_verification(exec_group, code, verification:dict ):
    if not verification.get(exec_group, None):
        verification[exec_group] = {}

    if not verification[exec_group].get(code, None):
        verification[exec_group][code] = {}


def filter_task(tasks, robot):
    aliases = robot_aliases[robot] if robot_aliases.get(robot, None) else []
    target_names = set([robot] + aliases )
    task_filter = filter(lambda t: getattr(t, 'robot', None) in target_names , tasks)
    return task_filter


def iter_assigend_in_design_and_task_exec_list(trial_design, trial_exec_result):
    for td_r in trial_design['robots']:
        if td_r['local_plan']:
            robot = td_r['name']
            task_execs = list(filter_task(trial_exec_result, robot))
            yield td_r, task_execs
    return

def check_assigned_robots_received_local_mission(trial_design, trial_exec_result):
    """ Check if the assigned robots executed a set of tasks """
    for td_r, task_execs in iter_assigend_in_design_and_task_exec_list(trial_design, trial_exec_result):
        if not task_execs:
            print(f'in {trial_design["code"]} { td_r["name"] } should be assigeds')
            # an assigned robot in the trial design without task execs
            return False
    return True


def check_tasks_were_executed_in_order(trial_design, trial_exec_result):
    """ Check if any task was executed out of order. Do not check if it was executed until the end """
    for td_r, task_execs in iter_assigend_in_design_and_task_exec_list(trial_design, trial_exec_result):
        if not task_execs:
            # an assigned robot in the trial design without task execs
            return False
        
        exec_group = None
        if trial_exec_result[0]:
            exec_group = getattr(trial_exec_result[0], 'exec_group', None)
        index = 0
        for lp_task in td_r['local_plan']:
            [_, _, lp_label] = lp_task
            if index >= len(task_execs):
                print(f'{exec_group}/{trial_design["code"]}> last task executed was "{lp_label}".')
                break
            if lp_label != task_execs[index].label:
                print(f'{exec_group}/{trial_design["id"]}_{trial_design["code"]}.log> task #{index } of { td_r["name"] } should be a "{lp_label}" but it was "{task_execs[index].label}".')
                return False
            index += 1
    return True


def find_task_that_were_executed(trial_design, trial_exec_result):
    for td_r, task_execs in iter_assigend_in_design_and_task_exec_list(trial_design, trial_exec_result):
        if not task_execs:
            # an assigned robot in the trial design without task execs
            yield td_r, td_r['local_plan'][0]
        
        # check if all tasks were executed
        index = 0
        for lp_task in td_r['local_plan']:
            [lp_skill, _, _] = lp_task
            if index >= len(task_execs) or not lp_skill == task_execs[index].skill:
                yield td_r, lp_task
            index += 1
    return

