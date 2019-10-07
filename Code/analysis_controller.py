# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 15:04:30 2019

@author: mep16tjr
"""
#%%
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import copy
import os
import numpy as np
plt.style.use('ggplot')
import matplotlib
os.chdir(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods\NC_methods-git\Code')
from error_model_nmv8000 import HTM, error_model
from myclasses_controller import process_results
matplotlib.rcParams['text.color'] = 'black'
%matplotlib qt
os.chdir(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods')


#%%
# =============================================================================
# Connect to the database
# =============================================================================
conn = pyodbc.connect(
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=amrcsql\mspengd;'
    r'DATABASE=MSP_VIRTMET;'
    r'Trusted_Connection=yes;'
)
cursor = conn.cursor()
# ================================================================

functions = ['G43', 'G43.4', 'G54.2', 'G68.2']

#specify the time and day of each data collection interval
proc = process_results('machining')
fpass, test_time, xyz_init = proc.return_dfs()

fpass_rot = copy.deepcopy(fpass)

fpass_rot['B0. C0.']['x'], fpass_rot['B0. C0.']['y'], fpass_rot['B0. C0.']['z'] = [4169, 4251], [4087, 4128, 4210], [3958, 4014, 4042, 4098]
fpass_rot['B0. C90.']['x'], fpass_rot['B0. C90.']['y'], fpass_rot['B0. C90.']['z'] = [7797, 7879, 7961], [7838, 7920], [7626, 7668, 7710, 7752]
fpass_rot['B0. C180.']['x'], fpass_rot['B0. C180.']['y'], fpass_rot['B0. C180.']['z'] = [10788, 10870], [10747, 10829, 10911], [10576, 10618, 10660, 10702]
fpass_rot['B0. C270.']['x'], fpass_rot['B0. C270.']['y'], fpass_rot['B0. C270.']['z'] = [13173, 13255, 13337], [13214, 13296], [13002, 13044, 13086, 13128]
fpass_rot['B0. C360.']['x'], fpass_rot['B0. C360.']['y'], fpass_rot['B0. C360.']['z'] = [14854, 14936], [14813, 14895, 14977], [14684, 14726, 14768, 14810]

fpass_rot['B90. C0.']['x'], fpass_rot['B90. C0.']['y'], fpass_rot['B90. C0.']['z'] = [15595], [15639, 15551], [16055, 16100, 16145]
fpass_rot['B90. C90.']['x'], fpass_rot['B90. C90.']['y'], fpass_rot['B90. C90.']['z'] = [16794], [16750, 16838], [17254, 17299, 17344]
fpass_rot['B90. C180.']['x'], fpass_rot['B90. C180.']['y'], fpass_rot['B90. C180.']['z'] = [17993], [17949, 18037], [18453, 18498, 18543]
fpass_rot['B90. C270.']['x'], fpass_rot['B90. C270.']['y'], fpass_rot['B90. C270.']['z'] = [19192], [19148, 19236], [19652, 19697, 19742]

fpass_rot['B-90. C0.']['x'], fpass_rot['B-90. C0.']['y'], fpass_rot['B-90. C0.']['z'] = [20382], [20338, 20426], [20834, 20879, 20924]
fpass_rot['B-90. C90.']['x'], fpass_rot['B-90. C90.']['y'], fpass_rot['B-90. C90.']['z'] = [21561], [21517, 21605], [22013, 22058, 22103]
fpass_rot['B-90. C180.']['x'], fpass_rot['B-90. C180.']['y'], fpass_rot['B-90. C180.']['z'] = [22740], [22696, 22784], [23192, 23237, 23282]
fpass_rot['B-90. C270.']['x'], fpass_rot['B-90. C270.']['y'], fpass_rot['B-90. C270.']['z'] = [23919], [23875, 23963], [24371, 24416, 24461]

#%%
# =============================================================================
# Find the local timestamp which corresponds with the finishing pass
# =============================================================================
fpass_LocalTime = {'G54.2' : copy.deepcopy(fpass),
                   'G43' : copy.deepcopy(fpass),
                   'G43.4' : copy.deepcopy(fpass),
                   'G68.2' : copy.deepcopy(fpass)
                   }

for function in fpass_LocalTime:
    for rotary_case in fpass:
        for t in range(len(test_time[function]['dt_start'])):
            for axis in xyz_init:
                for j in range(len(fpass_rot[rotary_case][axis])):
                    block = fpass_rot[rotary_case][axis][j]
                    
                    test_month = '2019-07'
                    datetime_start = '{}-{}:00.000'.format(test_month, test_time[function]['dt_start'][t])
                    datetime_end = '{}-{}:00.000'.format(test_month, test_time[function]['dt_stop'][t])
                    
                    pass_time = ("""
                                 SELECT local_time, block 
                                 FROM datalake.block
                                 WHERE block LIKE '%N{}%' AND local_time BETWEEN '{}' AND '{}'
                                 """ .format(
                                 block, 
                                 datetime_start,
                                 datetime_end
                                 )
                                 )
                        
                    data = pd.read_sql(pass_time, conn)
                    fpass_LocalTime[function][rotary_case][axis][t] = data
#%%
# =============================================================================
#    Define a function to align the data from G68.2 to the rest
#    G68.2 was run in the actual machining program zero (X-2.43 Y-0.810 Z512.298) 
#    compared to the nominal X0 Y0 Z512 that the other three were collected in
# =============================================================================
def correct_682(data, rotary_case, axis):
    ### input offsets in XYZ from actual G55 to nominally run X0 Y0 Z512 to 
    ### calculate comparator 
    
    offsets = {}
    offsets['x'] = -2.43
    offsets['y'] = -0.819
    offsets['z'] = 0.298
    
    if axis == 'x':
        axis_1 = 'x'
        axis_2 = 'y'
        axis_3 = 'z'
    elif axis == 'y':
        axis_1 = 'y'
        axis_2 = 'x'
        axis_3 = 'z'
        
    if 'B0' in rotary_case:
        if axis == 'x':    
            if 'C0.' in rotary_case or 'C360.' in rotary_case:
                data['position_{}'.format('x')] -= offsets['x']
            elif 'C90.' in rotary_case:
                data['position_{}'.format('x')] -= offsets['y']
            elif 'C180.' in rotary_case:
                data['position_{}'.format('x')] += offsets['x']
            elif 'C270.' in rotary_case:
                data['position_{}'.format('x')] += offsets['y']
        elif axis == 'y':
            if 'C0.' in rotary_case or 'C360.' in rotary_case:
                data['position_{}'.format('y')] -= offsets['y']
            elif 'C90.' in rotary_case:
                data['position_{}'.format('y')] += offsets['x']
            elif 'C180.' in rotary_case:
                data['position_{}'.format('y')] += offsets['y']
            elif 'C270.' in rotary_case:
                data['position_{}'.format('y')] -= offsets['x'] 

    elif 'B90' in rotary_case:
        if axis == 'x':
            data['position_{}'.format(axis)] += offsets[axis_3]    
        elif axis == 'y':
            if 'C0.' in rotary_case:
                data['position_{}'.format(axis)] -= offsets[axis_1]          
            elif 'C90.' in rotary_case:
                data['position_{}'.format(axis)] += offsets[axis_2]  
            elif 'C180.' in rotary_case:
                data['position_{}'.format(axis)] += offsets[axis_1]  
            elif 'C270.' in rotary_case:
                data['position_{}'.format(axis)] -= offsets[axis_2] 

    elif 'B-90' in rotary_case:
        if axis == 'x':
            data['position_{}'.format(axis)] -= offsets[axis_3]    
        elif axis == 'y':
            if 'C0.' in rotary_case:
                data['position_{}'.format(axis)] -= offsets[axis_1]          
            elif 'C90.' in rotary_case:
                data['position_{}'.format(axis)] += offsets[axis_2]  
            elif 'C180.' in rotary_case:
                data['position_{}'.format(axis)] += offsets[axis_1]  
            elif 'C270.' in rotary_case:
                data['position_{}'.format(axis)] -= offsets[axis_2]                 
    return data
# =============================================================================
# Find the XYZ positions which relate to the found local_times
# ============================================================================
fpass_xyz = {'G54.2' : copy.deepcopy(fpass),
                   'G43' : copy.deepcopy(fpass),
                   'G43.4' : copy.deepcopy(fpass),
                   'G68.2' : copy.deepcopy(fpass)
                   }
timeshift = 3
def shift_fpassTime(fpass_start, fpass_stop, timeshift):
### shift the window a second either side to capture full finishing pass
### specify the shift in seconds
    fpass_start = datetime.strptime(str(fpass_start), '%Y-%m-%d %H:%M:%S') - timedelta(seconds=timeshift)
    fpass_stop = datetime.strptime(str(fpass_stop), '%Y-%m-%d %H:%M:%S') + timedelta(seconds=timeshift)
    return fpass_start, fpass_stop

for function in fpass_LocalTime:
    for rotary_case in fpass:
        for t in range(len(test_time[function]['dt_start'])):
            for axis in xyz_init:
                if axis == 'x' or axis == 'y':
                    if len(fpass_LocalTime[function][rotary_case]['x'][t]) != 0:
                        fpass_start = min(min(fpass_LocalTime[function][rotary_case]['x'][t]['local_time']), 
                                          min(fpass_LocalTime[function][rotary_case]['y'][t]['local_time'])
                                          )
                        fpass_stop = max(max(fpass_LocalTime[function][rotary_case]['x'][t]['local_time']), 
                                          max(fpass_LocalTime[function][rotary_case]['y'][t]['local_time'])
                                          )
                        fpass_start, fpass_stop = shift_fpassTime(fpass_start, fpass_stop, timeshift)
                            
                elif axis == 'z':
                    if len(fpass_LocalTime[function][rotary_case]['z'][t]) != 0:  
                        fpass_start = min(fpass_LocalTime[function][rotary_case]['z'][t]['local_time'])
                        fpass_stop = max(fpass_LocalTime[function][rotary_case]['z'][t]['local_time'])
                        fpass_start, fpass_stop = shift_fpassTime(fpass_start, fpass_stop, timeshift)
             
                try:
                    sql = ("""
                           SELECT local_time, position_{} FROM datalake.position_{}
                           WHERE local_time BETWEEN '{}' AND '{}' AND datasource_id = 3;
                           """.format(
                           axis,
                           axis,
                           fpass_start,
                           fpass_stop
                           )
                           )  
            
                    data = pd.read_sql(sql, conn)
                    if function == 'G68.2':
                        data = correct_682(data, rotary_case, axis)
                        
                    fpass_xyz[function][rotary_case][axis][t] = data
                    
                except IndexError as e1:
                    print('Index error on {} {} {}: {}'.format(
                            function,
                            rotary_case,
                            axis, 
                            e1
                            )
                          )
                except NameError as e2:
                    print('Name error on {} {} {}: {}'.format(
                            function,
                            rotary_case,
                            axis, 
                            e2
                            )
                          )

#%%
# manually correct the dataframes so they only include the finishing pass

def fpass_window(fpass_xyz, function, rotary_case, lbound, ubound, alt_run=None):
    # takes arguments to clip a window in the data collection and returns the new selection to i = 1
    i = 1

    if alt_run == None:
        fpass_xyz[function][rotary_case]['x'][i] = fpass_xyz[function][rotary_case]['x'][i][lbound:ubound] 
        fpass_xyz[function][rotary_case]['y'][i] = fpass_xyz[function][rotary_case]['y'][i][lbound:ubound] 
        fpass_xyz[function][rotary_case]['z'][i] = fpass_xyz[function][rotary_case]['z'][i][lbound:ubound] 
    else:
        fpass_xyz[function][rotary_case]['x'][i] = fpass_xyz[function][rotary_case]['x'][alt_run][lbound:ubound] 
        fpass_xyz[function][rotary_case]['y'][i] = fpass_xyz[function][rotary_case]['y'][alt_run][lbound:ubound] 
        fpass_xyz[function][rotary_case]['z'][i] = fpass_xyz[function][rotary_case]['z'][alt_run][lbound:ubound]         

    return fpass_xyz

def apply_fpass_window(fpass_xyz):
    # extract only the lines that define the finishing pass
    i = 1

    function = 'G54.2'
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C0.', 11, 35)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C90.', 7, 35)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C180.', 0, 35)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C270.', 0, 35)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 0, 30, alt_run=3)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C90.', 6, 25)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C180.', 12, 29, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C270.', 2, 19)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C0.', 14, 33, alt_run=3)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C90.', 5, 23)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C180.', 15, 31, alt_run=3)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C270.', 2, 21)

    function = 'G43'
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C0.', 0, -1)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C90.', 0, 46)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C180.', 0, -1, alt_run=0)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C270.', 0, -1, alt_run=0)    

    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 0, 22)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C90.', 0, 24)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C180.', 7, 27)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C270.', 0, 24)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C0.', 11, 29)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C90.', 11, 29)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C180.', 13, 31)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C270.', 15, 34)

    function = 'G43.4'
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 20, 39) 
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C90.', 10, 23)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C180.', 14, 27, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C270.', 9, 22)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C0.', 14, 27, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C90.', 0, 27)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C180.', 14, 26, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C270.', 6, 19)

    function = 'G68.2'
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 22, 38)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C90.', 11, 29)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C180.', 14, 30)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C270.', 13, 29)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C0.', 13, 33, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C90.', 12, 30, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C180.', 10, 25, alt_run =2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C270.', 13, 28, alt_run=2)

    return fpass_xyz

fpass_xyz = apply_fpass_window(fpass_xyz)  

#%%
i=1
def plot_step(rotary_case, functions=None):
    plt.close('all')
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    if functions == None:
        ax.plot(fpass_xyz['G54.2'][rotary_case]['x'][i]['position_x'], fpass_xyz['G54.2'][rotary_case]['y'][i]['position_y'], c='red', linestyle = '--', label = 'G54.2')
        ax.plot(fpass_xyz['G43'][rotary_case]['x'][i]['position_x'], fpass_xyz['G43'][rotary_case]['y'][i]['position_y'], c='blue', linestyle = '-', label = 'G43')
        ax.plot(fpass_xyz['G43.4'][rotary_case]['x'][i]['position_x'], fpass_xyz['G43.4'][rotary_case]['y'][i]['position_y'], c='green', linestyle = ':', label = 'G43.4')
        ax.plot(fpass_xyz['G68.2'][rotary_case]['x'][i]['position_x'], fpass_xyz['G68.2'][rotary_case]['y'][i]['position_y'], c='orange', linestyle = '-.', label = 'G68.2')
    elif functions != None:
        for f in functions:
            ax.plot(fpass_xyz[f][rotary_case]['x'][i]['position_x'], fpass_xyz[f][rotary_case]['y'][i]['position_y'], c='red', linestyle = '--', label = 'G54.2')

    if 'B0.' in rotary_case:
        ax.set_xlim(525, 670)
        ax.set_ylim(-535, -375)
    elif 'B90.' in rotary_case:
        ax.set_xlim(90, 240)
        ax.set_ylim(-535, -385)
    elif 'B-90.' in rotary_case:
        ax.set_xlim(965, 1105)
        ax.set_ylim(-535, -385)

    ax.legend(loc='upper right', bbox_to_anchor=(1.1,1))
    ax.set_xlabel('X-axis MCS position /mm')
    ax.set_ylabel('Y-axis MCS position /mm')
    ax.set_title('Commanded MCS position tool paths\nfor step geometry at {}'.format(rotary_case))
    fig.show()

#%%
plot_step('B-90. C180.')
#%%
# plot and save the step geometries
     


for rotary_case in fpass:
    plot_step(rotary_case)
    fig = plt.gcf()
    # fig.savefig(r'NC_methods-git/Results/Controller/{}_stepGeometry.jpeg'.format(rotary_case), facecolor='white', format='jpeg')
    fig.savefig(r'NC_methods-git/Results/Controller/{}_stepGeometry.tiff'.format(rotary_case), facecolor='white', format='tiff')

#%%

# calculate the error vector for each step as a comparator
G54 = {'x': 600.204,
        'y': -459.73,
        'z': -859.739
        }

error_values = {'G43' : copy.deepcopy(fpass),
                'G43.4' : copy.deepcopy(fpass),
                'G54.2' : copy.deepcopy(fpass),
                'G68.2' : copy.deepcopy(fpass)
                }

# initialise a dataframe of zeros to hold the error vector magnitudes 
error_vectors = pd.DataFrame(np.zeros((4,len(fpass))), columns=fpass.keys())
error_vectors['function'] = ['G43', 'G43.4', 'G54.2', 'G68.2']
error_vectors = error_vectors.set_index('function')

i = 1
for function in functions:
    for rotary_case in fpass:
        for axis in ['x', 'y']:
            if 'B0.' in rotary_case:
                l_bound = min(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)])
                u_bound = max(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)])
                error_values[function][rotary_case][axis] = G54[axis] - ((l_bound + u_bound) / 2)

            if 'B90.' in rotary_case:
                l_bound = min(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)])
                # create a standardised upper bound x position as the 90 deg feature is not close
                if axis == 'x':
                    u_bound = G54['x']
                else:
                    u_bound = max(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)]) 

                if axis == 'x':
                    # calculate the nominal centre point between top of step and G54 pivot point. MCS of step is G54 - (program zero
                    # offset in z + B-axis error in z) + 30mm for the already machined steps, this + G54 / 2 gives the centre point.
                    error_values[function][rotary_case][axis] = ((G54[axis] - (512 + 0.25) + 30) + G54[axis]) / 2 - (l_bound + u_bound) /2
                elif axis == 'y':
                    error_values[function][rotary_case][axis] = G54[axis] - ((l_bound + u_bound) / 2)

            if 'B-90.' in rotary_case:
                u_bound = max(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)])     
                # create a standardised upper bound x position as the 90 deg feature is not close
                if axis == 'x':
                    l_bound = G54['x']
                else:
                    l_bound = min(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)])

                if axis == 'x':
                    # calculate the nominal centre point between top of step and G54 pivot point. MCS of step is G54 + (program zero
                    # offset in z + B-axis error in z) - 25mm for the already machined steps, this + G54 / 2 gives the centre point.
                    error_values[function][rotary_case][axis] = ((G54[axis] + (512 + 0.25) - 25) + G54[axis]) / 2 - (l_bound + u_bound) / 2
                elif axis == 'y':
                    error_values[function][rotary_case][axis] = G54[axis] - ((l_bound + u_bound) / 2)

        try:
            error_vectors[rotary_case][function] = abs(error_values[function][rotary_case]['x'] ** 2 + error_values[function][rotary_case]['y'] ** 2) ** 0.5
            print('{} {} magnitude: {}'.format(function, rotary_case, np.around(error_vectors[rotary_case][function], 3)))
        except TypeError as e1:
            print('type error: {}'.format(e1))

# now process these results as deviations from average
for rotary_case in fpass:
    average = error_vectors[rotary_case].sum() / 4
    error_vectors[rotary_case] -= average
    error_vectors[rotary_case] = abs(error_vectors[rotary_case])
#%%
# plot the distances from average and save to file

B0_steps = ['B0. C0.', 'B0. C90.', 'B0. C180.', 'B0. C270.', 'B0. C360.']
Bp90_steps = ['B90. C180.', 'B90. C90.', 'B90. C180.', 'B90. C270.']
Bn90_steps = ['B-90. C90.', 'B-90. C90.', 'B-90. C180.', 'B-90. C270.'] 
markers = ['.-', 'x-', '+-', 'v-']

def plot_distances():
    plt.close('all')
    fig = plt.figure(figsize=(10,10))
    ax_title = fig.add_subplot(111, frameon = False)
    ax_title.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    ax_title.grid(False)
    ax_title.axis('off')

    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    error_vectors[B0_steps].T.plot(style=markers, ax=ax1, legend=True)
    error_vectors[Bp90_steps].T.plot(style=markers, ax=ax2, legend=False)
    error_vectors[Bn90_steps].T.plot(style=markers, ax=ax3, legend=False)

    ax1.legend(loc='upper left', bbox_to_anchor=(1,1))

    ax_title.set_title('Euclidian distance from average feature centre point by method')
    fig.show()
    fig.savefig('NC_methods-git/Results/Controller/average_step_deviations.tiff', format='tiff', facecolor='white')

plot_distances()


#%%


 

