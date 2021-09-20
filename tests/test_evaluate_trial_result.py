
import sys
sys.path.append('./src')

from parse_logs.parse_base import LogDir
# from parse_logs.parse_base import arr_to_map
# from parse_logs.parse_coordinator_logs import read_design
# from parse_logs.extract_tasks_exec_result import parse_task_state
from parse_logs.extract_tasks_exec_result import TaskResult

from evaluate.trial_result import TrialResultEvaluator
from evaluate.trial_result import init_bid_store


def test_bid_store():
    LogDir.base_data_path = './tests/data'
    test_exec_code = 'experiment_2021_07_29_16_15_21_run_1'
    get_task_bid = init_bid_store('experiment_2021_07_29_16_15_21_run_1')
    task = TaskResult(exec_code=test_exec_code, code='aaabap', scenario_id='01', exec_group='les-01',
                      robot='r1', start_time=100, skill='', label='navto_room', parameters=None)

    bid = get_task_bid(task)
    assert bid['time'] == 68.2

def test_bid_store_not_planned_task():
    LogDir.base_data_path = './tests/data'
    test_exec_code = 'experiment_2021_07_29_16_15_21_run_1'
    get_task_bid = init_bid_store('experiment_2021_07_29_16_15_21_run_1')
    task = TaskResult(exec_code=test_exec_code, code='xxxx', scenario_id='01', exec_group='les-01',
                      robot='r1', start_time=100, skill='', label='navto_room', parameters=None)

    bid = get_task_bid(task)
    assert bid['time'] == None

def test_trial_result():
    LogDir.base_data_path = './tests/data'
    test_exec_code = 'experiment_2021_07_29_16_15_21_run_1'
    tre = TrialResultEvaluator()
    trial_result = next(tre.evaluate_trial_result(exec_code=test_exec_code))
    assert trial_result


def test_trial_result_real_experiment():
    LogDir.base_data_path = './data'
    test_exec_code = 'experiment_2021_07_29_15_33_17_run_1'
    tre = TrialResultEvaluator()
    trial_result = next(tre.evaluate_trial_result(exec_code=test_exec_code))
    assert True

def test_task_result():
    LogDir.base_data_path = './data'
    test_exec_code = 'experiment_2021_07_29_15_33_17_run_1'
    tre = TrialResultEvaluator()
    tre_task_results_iter = tre.task_results(exec_code=test_exec_code)
    first_planned = [task_result for task_result in tre_task_results_iter if task_result['planned_time']]
    assert True