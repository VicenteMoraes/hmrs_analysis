from typing import List
from parse_logs.extract_experiment_result import ExperimentParser, TrialEndStateExtractor, TrialRun
from parse_logs.extract_tasks_exec_result import TaskResult, TaskStateExtractor
from parse_logs.parse_base import arr_to_map, map_named, merge

from parse_logs.parse_coordinator_logs import filter_log, iter_coordinator_logs_in_scenario


def init_bid_store(exec_code):
    design_map = {}

    for scenario_code, coordinator_request_log in iter_coordinator_logs_in_scenario(exec_code):
        print(scenario_code)
        selected_bid = list(map_named('content', filter_log(coordinator_request_log, entity='selected_bid')))
        design_map[scenario_code] = arr_to_map(selected_bid[0]['plan'], by='label')

    def get_task_bid(task):
        trial_winning_bid = design_map.get(task.code, {})
        plan = trial_winning_bid.get(task.label, {})
        return { 'time': plan.get('time'), 'energy': plan.get('energy')}
    
    return get_task_bid

class TrialResultEvaluator:

    def evaluate_trial_result(self, exec_code):
        task_bid = init_bid_store(exec_code)
        ep = ExperimentParser(TrialEndStateExtractor(), TaskStateExtractor())
        for res, meta in ep.extract(exec_code = exec_code):
            # each trial
            trial: TrialRun = res[TrialEndStateExtractor.name]
            trial_tasks_states: List[TaskResult] = res[TaskStateExtractor.name]
            yield trial, trial_tasks_states
        return
    
    def task_results(self, exec_code):
        task_bid = init_bid_store(exec_code)
        ep = ExperimentParser(TrialEndStateExtractor(), TaskStateExtractor())
        for res, meta in ep.extract(exec_code = exec_code):
            # each trial
            trial: TrialRun = res[TrialEndStateExtractor.name]
            trial_tasks_states: List[TaskResult] = res[TaskStateExtractor.name]
            # check runtime exception
            for task in trial_tasks_states:
                planned_time = task_bid(task)['time']
                yield merge(task.to_dict(), {"planned_time": planned_time,  "trial_end_state": trial.end_state })

        return
