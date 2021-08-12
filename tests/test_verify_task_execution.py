import sys
sys.path.append('./src')

from parse_logs.parse_base import LogDir
from verification.verify_task_execution import check_task_execution, task_execution_check

# LogDir.base_data_path = './data'
# test_exec_code = 'experiment_2021_07_29_15_33_17_run_1'

LogDir.base_data_path = './tests/data'
test_exec_code = 'experiment_2021_04_01_16_20_00_run_1'

# def test_check_task_execution():
#     result = check_task_execution(test_exec_code)
#     assert len(result['les-01']) == 162
#     assert result['les-01']['aaaabp'][task_execution_check.assigned_robots_received_local_mission.name] is True
#     assert result['les-01']['aaaabp'][task_execution_check.tasks_were_executed_in_order.name] is True
