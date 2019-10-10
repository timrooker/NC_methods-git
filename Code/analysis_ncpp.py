#%%
import os
from xml.etree import ElementTree as ET
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import copy
plt.style.use('ggplot')
%matplotlib qt
matplotlib.rcParams['text.color'] = 'black'


#%%
# initialise
positions = {620: ['B0 C0', 'B0 C45', 'B0 C90', 'B0 C135', 'B0 C180', 'B0 C225', 'B0 C270', 'B0 C315', 'B0 C360'],
            621: ['B-90 C0', 'B-90 C45', 'B-90 C90', 'B-90 C135', 'B-90 C180', 'B-90 C225', 'B-90 C270', 'B-90 C315', 'B-90 C360'],
            622: ['B90 C0', 'B90 C45', 'B90 C90', 'B90 C135', 'B90 C180', 'B90 C225', 'B90 C270', 'B90 C315', 'B90 C360'],
            623: ['B0 C0', 'B15 C0', 'B30 C0', 'B45 C0', 'B60 C0', 'B75 C0', 'B90 C0'],
            624: ['B0 C0', 'B-15 C0', 'B-30 C0', 'B-45 C0', 'B-60 C0', 'B-75 C0', 'B-90 C0']
            }

program_dict = {620: pd.DataFrame(), 
                621: pd.DataFrame(), 
                622: pd.DataFrame(), 
                623: pd.DataFrame(), 
                624: pd.DataFrame()
                }

data_pp = {'G43' : copy.deepcopy(program_dict), 
            'G43_4' : copy.deepcopy(program_dict), 
            'G43_4-postop' : copy.deepcopy(program_dict), 
            'G54_2' : copy.deepcopy(program_dict), 
            'G68_2' : copy.deepcopy(program_dict)
            }
file_path = r'Data/NC_PP-results'

#%%
# pull data from benchmarks (pre-machining)

cases = ['G43', 'G43_4', 'G43_4-postop', 'G54_2', 'G68_2']
programs = [620, 621, 622, 623, 624]

def pull_data(case, program):
    if case == 'G43_4-postop':
        case = 'G43_4/post_machining'
    file_extract = r'{}/{}/{}.xml'.format(file_path, case, str(program))
    tree = ET.parse(file_extract)
    root = tree.getroot()

    root_xyz = root[2]
    rows = root_xyz[-1].find('Key').text[3:-8]

    d = []
    n_positions = int(float(rows)/3)
    for i in range(int(rows)):
        i = i + 1
        for child in root_xyz.findall("./Parameter/[Key='Row{}Value5']".format(i)):
            d.append(float(child.find('Value').text))

    d_xyz = []
    for n in range(n_positions):
        d_xyz.append((d[n*3], d[1 + n*3], d[2 + n*3])) 
    p = pd.DataFrame(d_xyz, columns=list('xyz'))

    return p

for case in cases:
    for program in programs:
        data_pp[case][program] = copy.deepcopy(pull_data(case, program))

#%%
# compare 2D error plots

plt.close('all')

alpha = 0.4

arc_rotation = 623
x_axis = 'x'
y_axis = 'z'
plt.plot(data_pp['G43_4'][arc_rotation]['x'], data_pp['G43_4'][arc_rotation]['z'], c = 'g', marker='o', label = 'G43.4', alpha = alpha)
plt.plot(data_pp['G43'][arc_rotation]['x'], data_pp['G43'][arc_rotation]['z'], marker='x', c = 'b', label = 'G43', alpha = alpha)
plt.plot(data_pp['G54_2'][arc_rotation][x_axis], data_pp['G54_2'][arc_rotation][y_axis], c = 'r', marker='*', label = 'G54.2', alpha = alpha)
plt.plot(data_pp['G68_2'][arc_rotation][x_axis], data_pp['G68_2'][arc_rotation][y_axis], c = 'c', marker='_', label = 'G68.2', alpha = alpha)
plt.legend()
plt.show()

#%%
# compare absolute vector magnitudes

plt.close('all')


# alpha = 1
markers = ['.', 'x', '+', 'v']
axs = []
fig = plt.figure(figsize=(10,10))

for x in range(len(programs)):
    axs.append(fig.add_subplot(5,1,x+1))

ax_title = fig.add_subplot(111, frameon = False)
ax_title.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
ax_title.grid(False)

for program in programs:
    for function, marker in zip(['G43', 'G43_4', 'G54_2', 'G68_2'], markers):
        magnitude = abs(( (data_pp[function][program]['x'] ** 2) + (data_pp[function][program]['y'] ** 2) + (data_pp[function][program]['y'] ** 2) ) ** 0.5)
        if function == 'G68_2' and program == 623:
            axs[programs.index(program)].plot(positions[program][1:], magnitude, marker = marker, label = function)
        else:
            axs[programs.index(program)].plot(positions[program], magnitude, marker = marker, label = function)

        # axs[programs.index(program)].set_title(program)

ax_title.set_xlabel('Probed position')
ax_title.set_ylabel('Absolute error vector magnitude /mm')
ax_title.set_title('Error vector magnitudes across various rotary axis positions')
# plt.tight_layout()
axs[0].legend(loc='upper left', bbox_to_anor=(1,1))
fig.show()
fig.savefig(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods\NC_methods-git\Results\NCPP_errorVectors.tiff', facecolor='white', format='tiff')
fig.savefig(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods\NC_methods-git\Results\NCPP_errorVectors.jpeg', facecolor='white', format='jpeg')

#%%
