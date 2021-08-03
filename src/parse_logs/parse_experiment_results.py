from parse_logs.extract_task_time import ExperimentParser, TrialEndStateExtractor


def parse_experiment_result(exec_code):    
    ep = ExperimentParser(TrialEndStateExtractor())
    for res in ep.extract(exec_code = exec_code):
        yield res[TrialEndStateExtractor.name]
    return