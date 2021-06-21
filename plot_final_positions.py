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

    # In[26]:


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


    # In[35]:


    lab_position = [-26.00, 13.00]


    # In[57]:


    nurse = nurse[:-1].replace('[', '', 1)
    nurse_position = re.findall(r'\[.*?\]', nurse)[0]
    nurse_position = eval(nurse_position)[:-1]

    m = 0
    for j in positions:
        m = max(m, len(j))
    c = np.linspace(0, 1, m)
    for j in range(len(positions)):
        plt.plot([x[0] for x in positions[j]], [x[1] for x in positions[j]], 
                            f'{colors[robots[j]]}-', zorder=j)
        plt.scatter([x[0] for x in positions[j]], [x[1] for x in positions[j]],
                c=c[:len([x[0] for x in positions[j]])], cmap=cmaps[robots[j]], zorder=j+100)
        plt.annotate(robots[j], positions[j][0])
    plt.scatter(lab_position[0], lab_position[1], color="cyan")
    plt.annotate("Lab", (lab_position[0], lab_position[1]))
    plt.scatter(nurse_position[0], nurse_position[1], color="magenta")
    plt.annotate("Nurse", (nurse_position[0], nurse_position[1]))
    plt.savefig(f"plots/{num:02d}")
    plt.clf()

