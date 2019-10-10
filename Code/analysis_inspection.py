#%%
import os
from xml.etree import ElementTree as ET
import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import copy
from scipy.spatial.distance import pdist, squareform
from matplotlib.collections import LineCollection
from scipy import stats
plt.style.use('ggplot')
%matplotlib qt
matplotlib.rcParams['text.color'] = 'black'
os.getcwd()

#%%
# load raw data from excel file

cmm_raw = {}
functions = ['G43', 'G43.4', 'G54.2', 'G68.2']
for function in functions:
    cmm_raw[function] = pd.read_excel(r'Data/Inspection/AE3436 - CMM Inspection Results.xlsx', sheet_name=function)
    cmm_raw[function] = cmm_raw[function].drop(columns=['Quindos Name', 'Feature Name2', 'Upper Tol', 'Lower Tol'])

cmm_nominal =  pd.read_excel(r'Data/Inspection/AE3436 - CMM Inspection Results.xlsx', sheet_name='Nominal Points')
cmm_nominal = cmm_nominal.drop(columns=['U', 'V', 'W', 'Base/Side', 'Index', 'Face', 'Feature Name2', 'Step'])
cmm_nominal = cmm_nominal.rename(columns={'Feature Name': 'reference'})

#%%
# sort data into xyz and isolate deviations from nominal
cmm_xyz = {}
for function in functions:
    cmm_xyz[function] = pd.DataFrame(columns=['reference', 'x', 'y', 'z'])

    for x in range(0, len(cmm_raw[function]), 3):
        entry = []
        entry += [cmm_raw[function]['Feature Name'][x]]
        for y in range(3):
            entry += [cmm_raw[function]['Deviation from Nominal'][x+y]] 
            # print(cmm_results[function]['Deviation from Nominal'][x+y])
        cmm_xyz[function].loc[x/3] = entry      

#%%
# sort data into a dict separating the rotary cases
rotary_cases = [
    'B0. C0.', 'B0. C90.', 'B0. C180.', 'B0. C270.', 'B0. C360.', 
    'B90. C0.', 'B90. C90.', 'B90. C180.', 'B90. C270.', 
    'B-90. C0.', 'B-90. C90.', 'B-90. C180.', 'B-90. C270.'
    ]

def sort_rcaseDict(in_df):
    # takes the raw xyz table from excel and converts it to a rotary-case specific dict
    out_dict = copy.deepcopy(rotary_cases_dict)

    if '-' in in_df['reference'][0]:
        A, B, C, D, E, F, G = 'A-', 'B-', 'C-', 'D-', 'E-', 'F-', 'G-'
    else:
        A, B, C, D, E, F, G = 'A_', 'B_', 'C_', 'D_', 'E_', 'F_', 'G_'
        
    for x, y in zip(rotary_cases[:5], [A, B, C, D, E]):
        out_dict[x] = in_df[in_df.reference.str.contains(y)]

    for x, y in zip(rotary_cases[5:9], ['East', 'North', 'West', 'South']):
        out_dict[x] = in_df[in_df.reference.str.contains(G) & in_df.reference.str.contains(y)]

    for x, y in zip(rotary_cases[9:13], ['West', 'South', 'East', 'North']):
        out_dict[x] = in_df[in_df.reference.str.contains(F) & in_df.reference.str.contains(y)]
    return out_dict

rotary_cases_dict = {}
rotary_cases_dict = {x: pd.DataFrame(columns=['reference', 'x', 'y', 'z']) for x in rotary_cases}

cmm_dict = {}
for function in functions:
    cmm_dict[function] = sort_rcaseDict(cmm_xyz[function])

cmm_nominal_dict = sort_rcaseDict(cmm_nominal)

#%%
# pull out the axis of interest, i.e. the only important measurement at the base of the step at B0. is in the Z direction

rotary_cases_dict_interest = {}
rotary_cases_dict_interest = {x: pd.DataFrame(columns=['reference', 'error']) for x in rotary_cases}

cmm_dict_interest = {}
for function in functions:
    cmm_dict_interest[function] = copy.deepcopy(rotary_cases_dict_interest)
    
    for rotary_case in rotary_cases:
        for i in range(len(cmm_dict[function][rotary_case])):
            entry = []
            ref = cmm_dict[function][rotary_case]['reference'].iloc[i]
            entry += [ref]

            if 'B0.' in rotary_case:
                if 'Base' in ref:
                    entry += [cmm_dict[function][rotary_case]['z'].iloc[i]]

                if 'Side' in ref:
                    if any(x in ref for x in (['East', 'West'])):
                        entry += [cmm_dict[function][rotary_case]['x'].iloc[i]]
                    elif any(x in ref for x in (['North', 'South'])):
                        entry += [cmm_dict[function][rotary_case]['y'].iloc[i]]

            elif 'B90.' or 'B-90.' in rotary_case:
                # B90/-90 side is as machined in the axis of the tool, base in radius of tool (same orientation as B0 inspection)
                # 12 points per run, goes from bottom of the feature up in z, along top and down other side
                # side measurements are simply the x/y directions
                # first and last 4 points are in x/y, middle 4 in z
                if 'Side' in ref:
                    if any(x in ref for x in (['East', 'West'])):
                        entry += [cmm_dict[function][rotary_case]['x'].iloc[i]]
                    elif any(x in ref for x in (['North', 'South'])):
                        entry += [cmm_dict[function][rotary_case]['y'].iloc[i]]

                if 'Base' in ref:
                    if any(x in ref for x in (['05', '06', '07', '08'])):
                        entry += [cmm_dict[function][rotary_case]['z'].iloc[i]]
                    else:
                        if any(x in ref for x in (['East', 'West'])):
                            entry += [cmm_dict[function][rotary_case]['y'].iloc[i]]
                        elif any(x in ref for x in (['North', 'South'])):
                            entry += [cmm_dict[function][rotary_case]['x'].iloc[i]]

            index = len(cmm_dict_interest[function][rotary_case])
            cmm_dict_interest[function][rotary_case].loc[index] = entry

#%%
# plot the results to compare
def plot_inspectionErrors(b_rotary_case, savefig=False):
    # simple line plots comparing the errors
    plt.close('all')
    fig = plt.figure(figsize=(10,10))
    vlineAlpha=0.5
    ax = {}
    ax_title = fig.add_subplot(111, frameon = False)
    ax_title.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    ax_title.grid(False)
    # ax_title.axis('off')

    if b_rotary_case == 'B0':
        # define the no of plots, ie no of C rotations at this B position
        n_plots = 5
        # define the cutoff points between the C rotations
        surface_index = [15, 19, 23, 27]
        # define the location of the xticks
        xticks_locs = [8, 17, 21, 25, 29]
        # and define what those labels are
        xticks_labels = ['Z', '+X', '+Y', '-Y', '-X']
        rotary_cases_subset = rotary_cases[:5]
    else:
        n_plots = 4
        surface_index = [3, 7, 11]
        xticks_locs = [1, 5, 9, 17]
        if b_rotary_case == 'B90':
            rotary_cases_subset = rotary_cases[5:9]
        if b_rotary_case == 'B-90':
            rotary_cases_subset = rotary_cases[9:13]

    for i in range(n_plots):
        ax[i] = fig.add_subplot(n_plots,1,i+1)

    for i, rotary_case in enumerate(rotary_cases_subset):
        for function in ['G43', 'G54.2', 'G68.2']:
            try:
                cmm_dict_interest[function][rotary_case] = cmm_dict_interest[function][rotary_case].sort_values('reference').reset_index()
            except ValueError:
                pass
            cmm_dict_interest[function][rotary_case].plot(y='error', ax=ax[i], label=function, legend=False)
            
            if b_rotary_case != 'B0':
                # xtick labels (on the base measurements) are dependent upon the NESW orentation of the face, alwasy in +ve direction 
                if 'C90.' in rotary_case:
                    xticks_labels = ['-X', 'Z', '+X', '+Y']
                if 'C270' in rotary_case:
                    xticks_labels = ['-X', 'Z', '+X', '-Y']
                if 'C0.' in rotary_case:
                    xticks_labels = ['-Y', 'Z', '+Y', '-X']
                if 'C180.' in rotary_case:
                    xticks_labels = ['-Y', 'Z', '+Y', '-Y']
                if 'B-90' in rotary_case:
                    if xticks_labels[-1][0] == '+':
                        xticks_labels[-1] == '-{}'.format(xticks_labels[1])  
                    else:
                        xticks_labels[-1] == '+{}'.format(xticks_labels[1])  
                plt.setp(ax[i], xticks=xticks_locs, xticklabels=xticks_labels)

            for j in range(n_plots-1):
                ax[i].axvline(x=[surface_index[j]], linestyle='--', color='grey', alpha=vlineAlpha)
            
            ax[i].set_title(rotary_case, loc='right', pad=0.5)
            ax[i]

    # cmm_results_dict
    ax[0].legend(loc='upper left', bbox_to_anchor=(1,1))
    
    if b_rotary_case == 'B0':
        for i in range(len(ax)-1):
            ax[i].axes.get_xaxis().set_visible(False)
        plt.setp(ax[n_plots-1], xticks=xticks_locs, xticklabels=xticks_labels)

    ax_title.set_xlabel('Major measurement axis')
    ax_title.set_ylabel('Measured error /mm')
    ax_title.set_title('Comparison of CMM inspection results')
    fig.show()
    if savefig == True:
        fig.savefig(r'NC_Methods-git/Results/Machining/error_values_{}.tiff'.format(b_rotary_case), format='tiff', facecolor='white')

for x in ['B0', 'B90', 'B-90']:
    plot_inspectionErrors(x, savefig=True)
#%%
# plot the inspection results in cartesian co-ordinates

def get_perimeter(function, rotary_case, plane, color, spread):
    # finds the coordinate space needed to plot perimeter lines from the datasets
    x = plane[0]
    y = plane[1]
    averageStepHeight = False

    if 'B0.' in rotary_case:
        if y == 'z':
            base_side = 'Base'
            averageStepHeight = True
        else:
            base_side = 'Side'
    else:
        if y == 'z':
            base_side = 'Base'
        else:
            base_side = 'Side'
            averageStepHeight = True

        if (plane=='xz') and any(x in rotary_case for x in (['C0.', 'C180.'])): 
            averageStepHeight = True   
        if (plane=='yz') and any(x in rotary_case for x in (['C90.', 'C270.'])): 
            averageStepHeight = True 

    data_nom = copy.deepcopy(cmm_nominal_dict[rotary_case][cmm_nominal_dict[rotary_case].reference.str.contains(base_side)])
    data_nom = data_nom.reset_index()

    if function == 'nominal':
        data = data_nom
    else:
        data_cmm = copy.deepcopy(cmm_dict[function][rotary_case][cmm_dict[function][rotary_case].reference.str.contains(base_side)])    
        data_cmm = data_cmm.reset_index()

        data = copy.deepcopy(data_nom)
        data[x] += data_cmm[x] * spread
        if averageStepHeight == True:
            data[y] += data_cmm[y] * spread
            m, c, _, _, _ = stats.linregress(data[x], data[y])
            data[y] = m * data[x] + c
        else:
            data[y] += data_cmm[y] * spread

    X = np.array([data[x], data[y]]).T
    k = 3
    N = len(X)  

    # matrix of pairwise Euclidean distances
    distmat = squareform(pdist(X, 'euclidean'))

    # select the kNN for each datapoint
    neighbors = np.sort(np.argsort(distmat, axis=1)[:, 0:k])

    # get edge coordinates
    coordinates = np.zeros((N, k, 2, 2))
    for i in np.arange(N):  
        for j in np.arange(k):
            coordinates[i, j, :, 0] = np.array([X[i,:][0], X[neighbors[i, j], :][0]])
            coordinates[i, j, :, 1] = np.array([X[i,:][1], X[neighbors[i, j], :][1]])

    # create line artists
    lines = LineCollection(coordinates.reshape((N*k, 2, 2)), color=color)
    return X, lines

def plot_inspectionXYZ(rotary_case, spread, spacing, savefig=False):
    # plot the inspected errors as they appear on the part in cartesian space

    plt.close('all')
    fig = plt.figure(figsize=(22,7))
    vlineAlpha=0.5
    ax = {}
    ax_title = fig.add_subplot(111, frameon = False)
    ax_title.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    ax_title.grid(False)
    # ax_title.axis('off')

    n_plots = 3
    for i in range(n_plots):
        ax[i] = fig.add_subplot(1,n_plots,i+1)
        
    planes = ['xy', 'xz', 'yz']

    for i, plane in zip(ax, planes):
        color='black'
        X, lines = get_perimeter('nominal', rotary_case, plane, color, spread)
        ax[i].scatter(X[:,0], X[:,1], c = color, marker='+', alpha=1)
        ax[i].add_artist(lines)

        # define suitable limits for the axes
        if (plane[1] == 'z') and ('B0.' in rotary_case):
            ax[i].set_ylim([X[0,1]-spacing, X[0,1]+spacing])

        if (plane[1] != 'z') and any(x in rotary_case for x in (['B90.', 'B-90.'])):
            if any(x in rotary_case for x in (['C0.', 'C180.'])):
                ax[i].set_xlim([X[0,0]-8, X[0,0]+8])
            else:
                ax[i].set_ylim([X[0,1]-8, X[0,1]+8])

        if 'B0.' not in rotary_case:
            if (plane=='xz') and any(x in rotary_case for x in (['C0.', 'C180.'])): 
                ax[i].set_xlim([X[0,0]-spacing, X[0,0]+spacing])
            if (plane=='yz') and any(x in rotary_case for x in (['C90.', 'C270.'])): 
                ax[i].set_xlim([X[0,0]-spacing, X[0,0]+spacing])
                # ax[i].set_ylim([X[0,1]-spacing, X[0,1]+spacing])


        for function, color in zip(['G43', 'G54.2', 'G68.2'], ['red', 'blue', 'mediumpurple']):
            X, lines = get_perimeter(function, rotary_case, plane, color, spread)
            ax[i].scatter(X[:,0], X[:,1], c = color, marker='o', alpha=1, label=function)
            ax[i].add_artist(lines)

        ax[i].set_xlabel('Error in {} /mm (scale {}:1)'.format(plane[0], spread))
        ax[i].set_ylabel('Error in {} /mm (scale {}:1)'.format(plane[1], spread))
        ax[i].set_title('{} plane'.format(plane))

    ax[2].legend(loc='upper left', bbox_to_anchor=(1,1))

    ax_title.set_title('Actual vs nominal step positions at {}'.format(rotary_case), y = 1.05)

    fig.show()
    if savefig == True:
        fig.savefig(r'NC_Methods-git/Results/Machining/errors_XYZ_{}.tiff'.format(rotary_case), facecolor='white')

spread = 10
spacing = 2

for rotary_case in rotary_cases:
    plot_inspectionXYZ(rotary_case, spread, spacing, savefig=True)

#%%



















