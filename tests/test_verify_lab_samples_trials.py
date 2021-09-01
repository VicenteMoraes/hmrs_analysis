import sys
sys.path.append('./src')

from parse_logs.parse_base import LogDir
from verification.verify_lab_samples_trials import check_mission_coordination, mc_checks


def test_check_mission_coordination():
    LogDir.base_data_path = './tests/data'
    test_exec_code = 'experiment_2021_07_29_16_15_21_run_1'

    result = check_mission_coordination(test_exec_code)
    assert len(result) == 4
    assert result['aaabbp'][mc_checks.all_robots_with_the_skills_were_evaluated.name] is True
    assert result['aaabbp'][mc_checks.available_robots_was_part_of_the_ensemble.name] is True
