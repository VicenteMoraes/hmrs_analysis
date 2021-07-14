import os
import fnmatch
import datetime

def get_path():
    return os.getcwd()+'/log'


def get_log_files(basepath, ftype):
    files_in_basepath = None
    with os.scandir(basepath) as entries:
        files_in_basepath = (entry for entry in entries if entry.is_file() and entry.name.endswith('.log'))
        # for file in files_in_basepath:
        #     print(file.name)
    for file in files_in_basepath:
        print(file.name)
    return files_in_basepath

def count_many_sims(basepath):
    timeout = 0
    success = 0
    low_bat = 0
    bt_fail = 0
    total = 0

    succeded= []
    faileds = []
    lows    = [] 
    timeouts= []   
    # print("Opening file: "+str(files))
    # for file in files:
    #         print(file.name)
    with os.scandir(basepath) as entries:
        files_in_basepath = (entry for entry in entries if entry.is_file() and entry.name.endswith('.log'))
        for file in files_in_basepath:
            print("Opening file: "+file.name)
            with open(file, 'r') as opened_file:
                lines = opened_file.readlines()
                last_line = ''
                # print("Opening file: "+str(lines[-1]))
                try:
                    last_line = lines[-1]
                except Exception as e:
                    pass
                
                print("with last line: "+last_line)
                if "reach-target" in last_line:
                    success = success + 1
                    succeded.append(file.name)
                elif "failure-bt" in last_line:
                    bt_fail = bt_fail + 1
                    faileds.append(file.name)
                elif "low-battery" in last_line:
                    low_bat = low_bat + 1
                    lows.append(file.name)
                else:
                    if "timeout" in last_line:
                        timeout = timeout + 1
                        timeouts.append(file.name)
            total = success+low_bat+timeout+bt_fail
    print("lows: "+str(len(lows)/total)+" : "+str(lows))
    print("timeouts: "+str(len(timeouts)/total)+" : "+str(timeouts))
    print("faileds: "+str(len(faileds)/total)+" : "+str(faileds))
    print("succeded: "+str(len(succeded)/total))
    print("total: "+str(total))

    current_date = datetime.datetime.today().strftime('%H-%M-%S-%d-%b-%Y')
    with open('results-'+current_date+'.csv', 'w') as file:
        file.write('Type,Quantity,Percentage\n')
        file.write('BT Failure,'+str(len(faileds))+','+("%.2f"%(100*len(faileds)/total))+'\n')
        file.write('Timeout,'+str(len(timeouts))+','+("%.2f"%(100*len(timeouts)/total))+'\n')
        file.write('Low Battery,'+str(len(lows))+','+("%.2f"%(100*len(lows)/total))+'\n')
        file.write('Success,'+str(len(succeded))+','+("%.2f"%(100*len(succeded)/total))+'\n')
        file.write('Total,'+str(total)+','+("%.2f"%(100*total/total))+'\n')

def get_times(lines):
    sim_line = lines[0]
    wall_line = lines[1]
    sim_time = float(sim_line[0:sim_line.find(',')])
    wall_time = float(wall_line[wall_line.find('execution-wall-clock=')+len('execution-wall-clock='):])
    return sim_time, wall_time

def get_close(last_line):
    if "reach-target" in last_line:
        return "reach-target"
    elif "failure-bt" in last_line:
        return "failure-bt"
    elif "low-battery" in last_line:
        return "low-battery"
    else:
        if "timeout" in last_line:
            return "timeout"

def results_table(path):
    results = {}
    with os.scandir(path) as entries:
        files_in_basepath = (entry for entry in entries if entry.is_file() and entry.name.endswith('.log'))
        for file in files_in_basepath:
            print("Opening file: "+file.name)
            with open(file, 'r') as opened_file:
                # get trial id
                trial_idx = file.name.find("trial")
                trial = file.name[trial_idx+5:trial_idx+5+2]
                print("trial #"+file.name[trial_idx+5:trial_idx+5+2])
                # get trial runtime
                lines = opened_file.readlines()
                last_lines = ''
                # print("Opening file: "+str(lines[-1]))
                try:
                    last_lines = [lines[-2], lines[-1]]
                except Exception as e:
                    continue

                sim_ttc, wall_ttc = get_times(last_lines)
                result = {
                    "id": trial,
                    "sim_ttc": sim_ttc,
                    "wall_ttc": wall_ttc,
                    "close": get_close(last_lines[-1]),
                }
                results[trial] = result
    metrics_dict = {
        "reach-target": "0,0,0,1",
        "failure-bt":   "1,0,0,0",
        "low-battery":  "0,1,0,0",
        "timeout":      "0,0,1,0",
    }
    with open('results.csv', 'w') as file:
        file.write('id,Sim TTC,Wall TTC,Failure,Low Battery,Tiemout,Success\n')
        for key in sorted(results.keys()):
            print(key, '->', results[key])
            # line = str(results[key]["id"]) +','+ str(results[key]["sim_ttc"]) +','+ \
            #        str(results[key]["wall_ttc"]) +','+ metrics_dict[results[key]["close"]] \
            #        + '\n'
            line = f"{results[key]['id']},{results[key]['sim_ttc']:.2f}," + \
                   f"{results[key]['wall_ttc']:.2f},{metrics_dict[results[key]['close']]}\n"
            file.write(line)

def main():
    path = get_path()
    print(path)
    list_of_files = get_log_files(path, '.log')
    print(list_of_files)
    # count_many_sims(path)
    results_table(path)

if __name__ == '__main__':
    main()
