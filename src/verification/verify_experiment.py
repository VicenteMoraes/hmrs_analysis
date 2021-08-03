from .verify_lab_samples_trials import check_mission_coordination
from .verify_task_execution import check_task_execution


def check_experiment(exec_code):
    mc_verification = check_mission_coordination(exec_code)
    te_verification = check_task_execution

    return mc_verification.update(te_verification)
