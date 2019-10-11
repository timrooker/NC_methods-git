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
os.chdir(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods\NC_methods-git\Code')
from error_model_nmv8000 import HTM
os.chdir(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods')

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

data_pp_measured = copy.deepcopy(data_pp)
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
    d_measured = []
    n_positions = int(float(rows)/3)
    for i in range(int(rows)):
        i = i + 1
        for child in root_xyz.findall("./Parameter/[Key='Row{}Value5']".format(i)):
            d.append(float(child.find('Value').text))

    for i in range(int(rows)):
        i = i + 1
        for child in root_xyz.findall("./Parameter/[Key='Row{}Value2']".format(i)):
            d_measured.append(float(child.find('Value').text))

    d_xyz = []
    d_measured_xyz = []
    for n in range(n_positions):
        d_xyz.append((d[n*3], d[1 + n*3], d[2 + n*3])) 
        d_measured_xyz.append((d_measured[n*3], d_measured[1 + n*3], d_measured[2 + n*3])) 
    p = pd.DataFrame(d_xyz, columns=list('xyz'))
    p_measured = pd.DataFrame(d_measured_xyz, columns=list('xyz'))

    return p, p_measured

for case in cases:
    for program in programs:
        data_pp[case][program], data_pp_measured[case][program] = copy.deepcopy(pull_data(case, program))

# missing data point for G68.2 in program 623 (B90 C0), replace with value from B-90 C0 at same position
data_0 = []
data_0.insert(0, data_pp_measured['G68_2'][624].iloc[0])
data_pp_measured['G68_2'][623] = pd.concat( [ pd.DataFrame(data_0), data_pp_measured['G68_2'][623] ], ignore_index=True)
data_pp['G68_2'][623] = data_pp_measured['G68_2'][623] - data_pp_measured['G68_2'][623].mean()

#%%
# compare 2D error plots

def align_data(data, arc_rotation):
    # executes a rotation on G54.2 and G68.2 to align all methods in XYZ orientation
    if arc_rotation == 620:
        B = 0
        C = 180
    elif arc_rotation == 621:
        B = -90
        C = 180
    elif arc_rotation == 622:
        B = 90
        C = 180
    elif arc_rotation == 623:
        B = 90
        C = 0
    elif arc_rotation == 624:
        B = -90
        C = 0

    data_aligned = pd.DataFrame()
    for j in range(len(data['x'])):
        entry = pd.DataFrame(HTM(data['x'][j], data['y'][j], data['z'][j], B, C, [0,0,0])[:-1].T, columns = list('xyz'))
        data_aligned = data_aligned.append(entry)
    return data_aligned

def plot_xyzPP(arc_rotation, savefig = False):
    # plot the results in XYZ

    plt.close('all')
    fig = plt.figure(figsize=(22,7))
    ax_title = fig.add_subplot(111, frameon = False)
    ax_title.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    ax_title.grid(False)
    
    alpha = 1
    functions = ['G43', 'G43_4', 'G54_2', 'G68_2']
    planes = ['xy', 'xz', 'yz']
    ax = {}

    for i in range(3):
        ax[i] = fig.add_subplot(1,3,i+1)

    for i, plane in enumerate(planes):
        lim = [0,0]
        for function in functions:
            data = data_pp[function][arc_rotation]
            if any(x == function for x in (['G54_2', 'G68_2'])):
                data = align_data(data, arc_rotation)                

            ax[i].plot(data[plane[0]], data[plane[1]], marker='o', label = function, alpha = alpha)
            ax[i].set_xlabel(plane[0])
            ax[i].set_ylabel(plane[1])

            l_lim = data.min().min()
            h_lim = data.max().max()
            if l_lim < lim[0] or h_lim > lim[1]:
                lim = [l_lim, h_lim]
        
        ax[i].set_xlim([lim[0] - 0.05, lim[1] + 0.05])
        ax[i].set_ylim([lim[0] - 0.05, lim[1] + 0.05])    

    ax[2].legend(loc='upper left', bbox_to_anchor=(1,1))
    ax_title.set_title('XYZ plots for rotary case: {} to {}'.format(positions[arc_rotation][0], positions[arc_rotation][-1]))
    fig.show()
    if savefig == True:
        fig.savefig(r'NC_methods-git\Results\Probing\NCPP_errorXYZ_{}.tiff'.format(arc_rotation), format='tiff', facecolor='white')

for x in list(positions.keys()):
    plot_xyzPP(x, savefig=True)

#%%
plot_xyzPP(620)

#%%
# compare absolute vector magnitudes

def plot_trendPP(dataset, savefig=False):
    plt.close('all')
    print('plotting {}...'.format(dataset))
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
            data = dataset[function][program]
            if any(x == function for x in (['G54_2', 'G68_2'])):
                data = align_data(data, arc_rotation) 
                # data = data.reset_index()

            magnitude = abs(( (data['x'] ** 2) + (data['y'] ** 2) + (data['z'] ** 2) ) ** 0.5)
            axs[programs.index(program)].plot(positions[program], magnitude, marker = marker, label = function)

            # axs[programs.index(program)].set_title(program)

    ax_title.set_xlabel('Probed position')
    ax_title.set_ylabel('Absolute error vector magnitude /mm')
    ax_title.set_title('Error vector magnitudes across various rotary axis positions')
    # plt.tight_layout()
    axs[0].legend(loc='upper left', bbox_to_anchor=(1,1))
    fig.show()
    if savefig == True:
        fig.savefig(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods\NC_methods-git\Results\Probing\NCPP_errorVectors.tiff', facecolor='white', format='tiff')

plot_trendPP(data_pp)

#%%

