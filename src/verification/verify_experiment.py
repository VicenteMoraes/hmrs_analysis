from utils import iter_map
from .verify_lab_samples_trials import check_mission_coordination
from .verify_task_execution import check_task_execution

def check_experiment(exec_code):
    mc_verification = check_mission_coordination(exec_code)
    mc_verification_list = []
    te_verification_list = []
    
    for trial, (property, value) in iter_map(mc_verification, 2):
        trial_verification = { "trial": trial, "property": property, "result": value }
        mc_verification_list.append(trial_verification)

    te_verification = check_task_execution(exec_code)
    for exec_group, (trial, (property, value)) in iter_map(te_verification, 3):
        trial_exec_verification = { "exec_group": exec_group, "trial": trial, "property": property, "result": value }
        te_verification_list.append(trial_exec_verification)


    return mc_verification_list, te_verification_list