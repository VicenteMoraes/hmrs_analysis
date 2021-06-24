import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import re


for num in range(81):
    with open(f'results/planned/log/experiment1_trial{num:02d}.log', 'r') as rf:
        text = rf.readlines()
        nurse = [line for line in text if "NURSES_CONFIG" in line][0][:-1]
        lines = [line for line in text if "robot-pose" in line]

    lines = [line.split(',') for line in lines]
    dic = {}
    for log in lines:
        try:
            x = float(log[-1].split(';')[0].split('=')[1])
            y = float(log[-1].split(';')[1].split('=')[1])
            position = [x, y]
            turtlebot = log[2]
            dic[turtlebot].append(position)
        except KeyError:
            dic[turtlebot] = [position]


    positions = list(dic.values())
    robots = list(dic.keys())
    colors = {'turtlebot1': 'r',
             'turtlebot2': 'b',
             'turtlebot3': 'g',
             'turtlebot4': 'm',
             'turtlebot5': 'c'}
    cmaps = {'turtlebot1': 'afmhot_r',
             'turtlebot2': 'hot_r',
             'turtlebot3': 'plasma_r',
             'turtlebot4': 'jet',
             'turtlebot5': 'gist_heat_r'}


    lab_position = [-26.00, 13.00]


    nurse = nurse[:-1].replace('[', '', 1)
    nurse_position = re.findall(r'\[.*?\]', nurse)[0]
    nurse_position = eval(nurse_position)[:-1]
    nurse_position


    def animate(i):
        c = np.linspace(0, 1, i)
        for j in range(len(positions)):
            ax.plot([x[0] for x in positions[j][:i]], [x[1] for x in positions[j][:i]], 
                    f'{colors[robots[j]]}-', zorder=j)
            try:
                ax.scatter([x[0] for x in positions[j][:i]], [x[1] for x in positions[j][:i]],
                        c=c, cmap=cmaps[robots[j]], zorder=j+100)
            except:
                ax.scatter([x[0] for x in positions[j][:i]], [x[1] for x in positions[j][:i]],
                        c=c[:len([x[0] for x in positions[j][:i]])], cmap=cmaps[robots[j]], zorder=j+100)
            ax.annotate(robots[j], positions[j][0])
        ax.scatter(lab_position[0], lab_position[1], color="cyan")
        ax.annotate("Lab", (lab_position[0], lab_position[1]))
        ax.scatter(nurse_position[0], nurse_position[1], color="magenta")
        ax.annotate("Nurse", (nurse_position[0], nurse_position[1]))

    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, animate, frames=29)

    ani.save(f'animations/{num:02d}.mp4', fps=2)
    print(f"FINISHED:{num}")
