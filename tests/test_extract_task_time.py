import sys
import os
cwd = os.getcwd()
sys.path.append(f'{cwd}/src')
print(sys.path)

from collections import namedtuple
from parse_logs.parse_base import LogDir, parse_line_and_call_handle, parse_trial_run_logs
from parse_logs.extract_tasks_exec_result import extract_status_and_parameters, task_started, task_ended, TaskResult, init_task_state_interpreter

line_start_1 = \
    '9.33333325386,[info],turtlebot5,skill-life-cycle,navigation,(status=STARTED, parameters=[[-37.0, 33.98, -1.5707963267948966, True], [-37.0, 18.93, 0.0, True], [-33.9, 18.93, 3.14, False]])'
line_start_2 = \
    "218.799999952,[info],turtlebot5,skill-life-cycle,approach_person,(status=STARTED, parameters=['nurse'])"

def test_init_task_state_interpreter():
    start_task, end_task, end_trial = init_task_state_interpreter('2021-04-01', 'aaaa', 'les-01')
    start_task(100, entity='r1', skill='navigate', parameters={'from': 'A'})

    tasks_results: list[TaskResult] = []
    end_trial(tasks_result_to_extend=tasks_results)

    assert tasks_results[0].skill == 'navigate'
    assert tasks_results[0].parameters == {'from': 'A'}

def test_task_parser_end_task():
    start_task, end_task, end_trial = init_task_state_interpreter('2021-04-01', 'aaaa', 'les-01')
    start_task(100, 'r1', 'navigate', {'from': 'A'})
    end_task(200, 'r1', 'navigate', 'succ')

    tasks_results: list[TaskResult] = []
    end_trial(tasks_result_to_extend=tasks_results)

    assert tasks_results[0].end_state == 'succ'
    assert tasks_results[0].end_time == 200

def test_get_parametesr():
    params = '(status=STARTED, parameters=[[-37.0, 33.98, -1.5707963267948966, True], [-37.0, 18.93, 0.0, True], [-33.9, 18.93, 3.14, False]])'
    status, parameters = extract_status_and_parameters(params)

    assert status == 'STARTED'
    assert isinstance(parameters, list)


# def test_parse_line_start_task():
#     handler_called, parser_called = False, False
#     def parser_match(skill_log):
#         nonlocal parser_called
#         parser_called = True
#         return True, { 'x': 3}
    
#     def handler(x, **other_params):
#         nonlocal handler_called
#         handler_called = True

#     parse_line_and_call_handle(line_start_1,
#         (parser_match, handler, False)
#         )
#     assert parser_called
#     assert handler_called

# def test_parse_task_start_and_end():
#     lines = [line_start_1, line_start_2]
#     task_results, b = [], []
#     parse_trial_run_logs('2021-04-01', 'les-01', 'aaaa', 
#         lines, task_results, b)

#     assert task_results[0].skill == 'navigation'
#     assert task_results[0].end_time == 218.799999952
#     assert task_results[1].skill == 'approach_person'

# def test_parse_task_reach_way_point():
#     lines = [line_start_1, line_start_2]
#     task_results, b = [], []
#     parse_trial_run_logs('2021-04-01', 'les-01', 'aaaa', 
#         lines, task_results, b)

#     assert task_results[0].skill == 'navigation'
#     assert task_results[0].end_time == 218.799999952
#     assert task_results[1].skill == 'approach_person'

# def test_task_results_parser():
#     LogDir.base_data_path = './tests/data'
#     task_results_objs, _ = task_results_parser(exec_code='experiment_2021_04_01_16_20_00_run_1')
#     assert len(task_results_objs) == 44
