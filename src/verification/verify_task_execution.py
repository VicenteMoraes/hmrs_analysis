from enum import Enum
from functools import reduce
from parse_logs.parse_base import arr_to_map
from parse_logs.parse_coordinator_logs import read_design

from parse_logs.parse_trial_run import iter_exec_logs_in_experiment

# Task Execution checks
class task_execution_check(Enum):
    assigned_robots_received_local_mission = 0
    tasks_were_executed_in_order = 1 # the plan was followed
    completed_plans_leaded_to_mission_success = 2 # tasks are executed, 


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
    for exec_group, trial_code, iter_log_lines in iter_exec_logs_in_experiment(exec_code):
        init_verification(exec_group, trial_code, verification)


        trial_design = trial_design_map[trial_code]
        
        # parse log
        trial_tasks_exec_results = None# parse_trial_log(exec_code, exec_group, trial_code, iter_log_lines)
        trial_end_result = None # TODO
        # check trial execution
        for property, check_fnc in get_verification_pairs():
            verification[exec_group][trial_code][property.name] = \
                check_fnc(trial_design, trial_tasks_exec_results, trial_end_result)
            
            # TODO compare estimates

    # TODO check all scenarios where checked
    return verification

def init_verification(exec_group, scenario_code, verification:dict ):
    if not verification.get(exec_group, None):
        verification[exec_group] = {}

    if not verification[exec_group].get(scenario_code, None):
        verification[exec_group][scenario_code] = {}


def filter_task(tasks, robot):
    task_filter = filter(lambda t: t.robot == robot , tasks)
    return task_filter


def iter_assigend_in_design_and_task_exec_list(trial_design, trial_exec_result):
    for td_r in trial_design['robots']:
        if td_r['local_plan']:
            robot = td_r['name']
            task_execs = list(filter_task(trial_exec_result, robot))
            yield td_r, task_execs
    return

def check_assigned_robots_received_local_mission(trial_design, trial_exec_result, trial_end_result):
    for td_r, task_execs in iter_assigend_in_design_and_task_exec_list(trial_design, trial_exec_result):
        if not task_execs:
            print(f'in {trial_design["code"]} { td_r["name"] } should be assigeds')
            # an assigned robot in the trial design without task execs
            return False
    return True


def check_tasks_were_executed_in_order(trial_design, trial_exec_result):
    for td_r, task_execs in iter_assigend_in_design_and_task_exec_list(trial_design, trial_exec_result):
        if not task_execs:
            # an assigned robot in the trial design without task execs
            return False
        
        index = 0
        for lp_task in td_r['local_plan']:
            [lp_skill, _, _] = lp_task
            if index >= len(task_execs) or not lp_skill == task_execs[index].skill:
                print(f'in {trial_design["code"]} task number {index +1 } of { td_r["name"] } should be a {lp_skill}')
                return False
            index += 1

        print(td_r)


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

def check_tasks_were_executed_in_order(trial_design, trial_tasks_exec_result, trial_end_result):
    td_r, lp_task = next(find_task_that_were_executed(trial_design, trial_tasks_exec_result), (None, None) )
    if td_r:
        print(f'in {trial_design["code"]} task {lp_task} of robot { td_r["name"] } not executed')
        return False # todo check trial_end_result
    else:
        return not td_r
