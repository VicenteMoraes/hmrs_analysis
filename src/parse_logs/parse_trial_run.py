from parse_logs.extract_task_time import NavSegmentResult, TaskResult
from .parse_base import get_exec_folder_path, iter_results_dir

def iter_exec_logs_in_experiment(exec_code):
    folder_path = get_exec_folder_path(exec_code)
    
    for exec_group, iter_exec_group in iter_results_dir(folder_path):
        for trial_run_code, iter_lines in iter_exec_group:
            try:
                [_, trial_code] = trial_run_code.split('_')
                yield exec_group, trial_code, iter_lines
            except:
                print(f'ignoring {trial_run_code} file on {str(folder_path)}')
                continue
    return

# def parse_trial_log(exec_code, exec_group, trial_code, iter_lines) -> list[TaskResult]:
#     tasks_results: list[TaskResult] = []
#     nav_segments_results: list[NavSegmentResult] = []
#     mission_result = False
#     parse_trial_run_logs(
#                 exec_code, exec_group, trial_code,
#                 iter_lines, tasks_results, nav_segments_results)

#     return tasks_results, mission_result