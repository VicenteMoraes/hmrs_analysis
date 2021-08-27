import sys
sys.path.append('./src')

from parse_logs.parse_base import LogDir
from verification.verify_experiment import check_experiment


def test_check_experiment():
    LogDir.base_data_path = './data'
    check_mc, check_te = check_experiment('experiment_2021_07_29_15_33_17_run_1')
    assert check_mc


