from parse_logs.parse_base import LogDir

from verification.verify_experiment import check_experiment


LogDir.base_data_path = './tests/data'
exec_code = 'experiment_2021_07_29_16_15_21_run_1'

# LogDir.base_data_path = './data'
# exec_code = 'experiment_2021_07_29_15_33_17_run_1'

def main():
    a, b = check_experiment(exec_code)
    print(a)
    print(b)


if __name__ == '__main__':
    main()
