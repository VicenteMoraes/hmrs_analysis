import pytest
import sys
sys.path.append('./src')

from parse_logs.parse_base import LogDir
from verification.verify_task_execution import check_task_execution, task_execution_check

LogDir.base_data_path = './tests/data'
test_exec_code = 'experiment_2021_07_29_16_15_21_run_1'

def test_check_task_execution():
    result = check_task_execution(test_exec_code)
    assert len(result) == 4
    assert result['les-01']['aaaabp'][task_execution_check.assigned_robots_received_local_mission.name] is True
