from enum import Enum
from functools import reduce
from parse_logs.parse_base import arr_to_map
from parse_logs.parse_coordinator_logs import iter_coordinator_logs_in_scenario, read_design
from parse_logs.parse_coordinator_logs import filter_log


lab_samples_required_skills = set(['navigation',
                                'approach_person' , 
                                'authenticate_person' , 
                                'operate_drawer' , 
                                'approach_robot' ])

# Mission Coordination Checks
class mc_checks(Enum):
    available_robots_was_part_of_the_ensemble = 0 # the right robots entered the ensemble
    all_robots_with_the_skills_were_evaluated = 1 # the robots with the set of skill to execute a local mission were evaluated
    the_best_ranked_robots_were_assigned = 2 # the selection chosed the best robot


# Task Execution checks
class task_execution_check(Enum):
    assigned_robots_received_local_mission = 0
    tasks_were_executed_in_order = 1 # the plan was followed
    completed_plans_leaded_to_mission_success = 2 # tasks are executed, 


# property and function that verify this property
def get_verification_pairs():
    verification_pairs = [
        (mc_checks.available_robots_was_part_of_the_ensemble, check_available_robots_were_part_of_the_coalition_formation_process ),
        (mc_checks.all_robots_with_the_skills_were_evaluated, check_all_robots_with_the_skills_were_evaluated)
        ]
    return verification_pairs


def check_mission_coordination(exec_code):
    
    design = read_design(exec_code)
    factors_map = design.factors
    scenario_map = arr_to_map(design.scenarios, by='code')
    
    verification  =  {}
    for scenario_code, coordinator_request_log in iter_coordinator_logs_in_scenario(exec_code):
        verification[scenario_code]  =  {}
        # check scenarios
        for property, check_fnc in get_verification_pairs():
            trial = next(filter(lambda trial: trial['code'] == scenario_code, design.trials), None)
            verification[scenario_code][property.name] = check_fnc(factors_map, scenario_map[scenario_code], trial, coordinator_request_log)

    # TODO check all scenarios where checked
    return verification


def map_field(field, iter):
    return map(lambda obj: getattr(obj.content, field), iter)

def map_value(key, iter):
    return map(lambda r: r[key], iter)

def map_named(name, iter):
    return map(lambda r: r._asdict()[name], iter)

def check_available_robots_were_part_of_the_coalition_formation_process(factors_map, scenario, trial, coordinator_request_log):
    robots_in_the_design = scenario['robots']
    robots_in_the_design_names = set(map(lambda r:r['name'], robots_in_the_design))

    inconpatible_workers = list(map_named('content', filter_log(coordinator_request_log, entity='incompatible_workers')))
    evaluated_workers = list(map_named('content', filter_log(coordinator_request_log, entity='bid')))
    
    robots_in_the_ensemble = set(map_value('worker', inconpatible_workers + evaluated_workers))

    return not (robots_in_the_design_names - robots_in_the_ensemble) # no robot in the design is out of the ensemble



def check_all_robots_with_the_skills_were_evaluated(factors_map, scenario, trial, coordinator_request_log):
    def filter_robots_with_required_skills(robots, required_skills):
        return filter(lambda r: not required_skills - set(r['skills'] ), robots)

    scenario_robots_with_required_skills = filter_robots_with_required_skills(
        scenario['robots'], lab_samples_required_skills)

    set_of_names_of_scenario_robots_with_required_skills = set(map_value('name', scenario_robots_with_required_skills))
    
    evaluated_robots_logs = filter_log(coordinator_request_log, entity='bid')
    evaluated_robots_content = map_named('content', evaluated_robots_logs)
    sef_of_name_of_evaluated_robots = set(map_value('worker', evaluated_robots_content))

    return not (set_of_names_of_scenario_robots_with_required_skills - sef_of_name_of_evaluated_robots) # no robot in the design is out of the ensemble

def check_assigned_robots_received_local_mission(factors_map, scenario, trial, coordinator_request_log):
    pass



# def check_mission_context_was_created(coordinator_request_log):
#     """ Cfp receives a local mission for the managed roles 
#     of the requested mission """
#     filter_log(entity=)
#     get_log(scenario, 'request'
    
#     verification['log_exits'], request_log_exists is not None)

#     local_mission = lfp.get_entity('local_mission')

#     assert(verification, local_mission)


# def check_mission_was_estimated_for_robots_with_all_skills(exp_design, exp_coordinator_log):
#     set(exp_coordinator_log['incompatible'][]) = exp_design
