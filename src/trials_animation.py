import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import re
import glob


experiment_dir = "experiment_2021_07_29_15_33_17_run_1"
computers = [f"les-{i:02d}" for i in range(1, 9)]
failures = []

for computer in computers:
    for num in range(1, 82):
        for b_or_p in ['b', 'p']:
            filename = glob.glob(f'../data/{experiment_dir}/step2_execution/{computer}/{num:02d}*{b_or_p}.log')[0]
            with open(filename, 'r') as rf:
                try:
                    text = rf.readlines()
                    nurse = text[1][:-1]
                    lines = [line for line in text if '{"y":' in line]
                except Exception as e:
                    print(e)
                    print(f"BROKEN {filename}")
                    failures.append(filename)
                    continue

            dic = {}
            for log in lines:
                try:
                    robot_pos = re.findall(r'\{.*?\}', log)[0]
                    robot_pos = eval(robot_pos)
                    x = float(robot_pos['x'])
                    y = float(robot_pos['y'])
                    position = [x, y]
                    turtlebot = log.split(",")[2][1:]
                    dic[turtlebot].append(position)
                except KeyError:
                    dic[turtlebot] = [position]


            positions = list(dic.values())
            robots = list(dic.keys())
            colors = {'turtlebot1': 'r',
                     'turtlebot2': 'b',
                     'turtlebot3': 'g',
                     'turtlebot4': 'm',
                     'turtlebot5': 'c',
                     'turtlebot6': 'y'}
            cmaps = {'turtlebot1': 'jet',
                     'turtlebot2': 'jet',
                     'turtlebot3': 'jet',
                     'turtlebot4': 'jet',
                     'turtlebot5': 'jet',
                     'turtlebot6': 'jet'}


            lab_position = [-26.00, 13.00]
            nurse = nurse[:-1].replace('[DEBUG]', '').replace('[', '', 1)
            nurse_position = re.findall(r'\[.*?\]', nurse)[0]
            nurse_position = eval(nurse_position)[:-1]


            def animate(i):
                for j in range(len(positions)):
                    c = np.linspace(0, 1, i)
                    ax.plot([x[0] for x in positions[j][:i]], [x[1] for x in positions[j][:i]], 
                            f'{colors[robots[j]]}-', zorder=j)
                    try:
                        ax.scatter([x[0] for x in positions[j][:i]], [x[1] for x in positions[j][:i]],
                                c=c, cmap=cmaps[robots[j]], zorder=j+100)
                    except:
                        ax.scatter([x[0] for x in positions[j][:i]], [x[1] for x in positions[j][:i]],
                                c=c[:len(positions[j][:i])], cmap=cmaps[robots[j]], zorder=j+100)
                    ax.annotate(robots[j], positions[j][0])
                ax.scatter(lab_position[0], lab_position[1], color="cyan")
                ax.annotate("Lab", (lab_position[0], lab_position[1]))
                ax.scatter(nurse_position[0], nurse_position[1], color="magenta")
                ax.annotate("Nurse", (nurse_position[0], nurse_position[1]))

            m = 0
            for j in positions:
                m = max(m, len(j))
            fig, ax = plt.subplots()
            ani = animation.FuncAnimation(fig, animate, frames=m+1)

            ani.save(f'../animations/{computer}/{num:02d}{b_or_p}.mp4', fps=2)
            print(f"FINISHED:../animations/{computer}/{num:02d}{b_or_p}.mp4")
            plt.close(fig)
