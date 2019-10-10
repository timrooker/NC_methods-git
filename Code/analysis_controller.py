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
        elif axis == 'z':
            data['position_z'] += offsets['z']

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
        elif axis == 'z':
            if 'C0.' in rotary_case:
                data['position_{}'.format('z')] -= offsets['x']          
            elif 'C90.' in rotary_case:
                data['position_{}'.format('z')] += offsets['y']  
            elif 'C180.' in rotary_case:
                data['position_{}'.format('z')] += offsets['x']  
            elif 'C270.' in rotary_case:
                data['position_{}'.format('z')] -= offsets['y'] 

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
        elif axis == 'z':
            if 'C0.' in rotary_case:
                data['position_{}'.format('z')] += offsets['x']          
            elif 'C90.' in rotary_case:
                data['position_{}'.format('z')] -= offsets['y']  
            elif 'C180.' in rotary_case:
                data['position_{}'.format('z')] -= offsets['x']  
            elif 'C270.' in rotary_case:
                data['position_{}'.format('z')] += offsets['y']                
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
                    # if function == 'G54.2' and rotary_case == 'B-90. C270.':
                    #     data = correct_682(data, rotary_case, axis)

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

def fpass_window(fpass_xyz, function, rotary_case, lbound, ubound, window_z=False, alt_run=None):
    # takes arguments to clip a window in the data collection and returns the new selection to i = 1
    i = 1
    if window_z == False:
        if alt_run == None:
            fpass_xyz[function][rotary_case]['x'][i] = fpass_xyz[function][rotary_case]['x'][i][lbound:ubound] 
            fpass_xyz[function][rotary_case]['y'][i] = fpass_xyz[function][rotary_case]['y'][i][lbound:ubound] 
        else:
            fpass_xyz[function][rotary_case]['x'][i] = fpass_xyz[function][rotary_case]['x'][alt_run][lbound:ubound] 
            fpass_xyz[function][rotary_case]['y'][i] = fpass_xyz[function][rotary_case]['y'][alt_run][lbound:ubound] 
    
    else:
        if alt_run == None:
            fpass_xyz[function][rotary_case]['z'][i] = fpass_xyz[function][rotary_case]['z'][i][lbound:ubound] 
        else:
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

    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 18, 34, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C90.', 11, 29, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C180.', 12, 29, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C270.', 15, 33, alt_run=2)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C0.', 14, 33, alt_run=3)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C90.', 11, 30, alt_run=3)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C180.', 15, 31, alt_run=3)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C270.', 2, 19)

    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C0.', 0, -1, window_z=True, alt_run=4)
    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C90.', 0, -1, window_z=True, alt_run=4)
    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C180.', 0, -1, window_z=True, alt_run=4)
    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C270.', 0, -1, window_z=True, alt_run=4)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 0, -1, window_z=True, alt_run=2)


    function = 'G43'
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C0.', 0, -1, alt_run=0)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C90.', 0, 46)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C180.', 0, -1, alt_run=0)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C270.', 0, -1, alt_run=0)    

    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 19, 35, alt_run=0)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C90.', 12, 29, alt_run=0)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C180.', 14, 32, alt_run=0)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C270.', 14, 31, alt_run=0)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C0.', 11, 29)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C90.', 11, 29)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C180.', 13, 31)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C270.', 15, 34)

    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C0.', 0, -1, window_z=True, alt_run=2)
    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C90.', 0, -1, window_z=True, alt_run=2)
    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C180.', 0, -1, window_z=True, alt_run=2)
    # fpass_xyz = fpass_window(fpass_xyz, function, 'B0. C270.', 0, -1, window_z=True, alt_run=2)

    function = 'G43.4'
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C0.', 20, 39) 
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C90.', 11, 24, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C180.', 14, 27, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B90. C270.', 14, 28, alt_run=2)

    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C0.', 13, 27, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C90.', 13, 27, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C180.', 14, 26, alt_run=2)
    fpass_xyz = fpass_window(fpass_xyz, function, 'B-90. C270.', 11, 26, alt_run=2)

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

error_values = {'G43' : pd.DataFrame(),
                'G43.4' : pd.DataFrame(),
                'G54.2' : pd.DataFrame(),
                'G68.2' : pd.DataFrame()
                }

# initialise a dataframe of zeros to hold the error vector magnitudes 
# error_euclidian = pd.DataFrame(np.zeros((4,len(fpass))), columns=fpass.keys())
# error_euclidian['function'] = ['G43', 'G43.4', 'G54.2', 'G68.2']
# error_euclidian = error_euclidian.set_index('function')

i = 1
for function in functions:
    for rotary_case in fpass:
        case_list = []
        
        for axis in ['x', 'y', 'z']:
            
            if 'B0.' in rotary_case:
                l_bound = min(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)])
                u_bound = max(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)])
                # error_values[function][rotary_case][axis] = G54[axis] - ((l_bound + u_bound) / 2)
                if axis != 'z':
                    case_list.append(G54[axis] - ((l_bound + u_bound) / 2))
                else:
                    case_list.append(min(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)]))

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
                    # error_values[function][rotary_case][axis] = ((G54[axis] - (512 + 0.25) + 30) + G54[axis]) / 2 - (l_bound + u_bound) /2
                    case_list.append(((G54[axis] - (512) + 30) + G54[axis]) / 2 - (l_bound + u_bound) /2)

                elif axis == 'y':
                    # error_values[function][rotary_case][axis] = G54[axis] - ((l_bound + u_bound) / 2)
                    case_list.append(G54[axis] - ((l_bound + u_bound) / 2))
                
                elif axis == 'z':
                    case_list.append(min(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)]))

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
                    # error_values[function][rotary_case][axis] = ((G54[axis] + (512 + 0.25) - 25) + G54[axis]) / 2 - (l_bound + u_bound) / 2
                    case_list.append(((G54[axis] + (512) - 25) + G54[axis]) / 2 - (l_bound + u_bound) / 2)
                elif axis == 'y':
                    # error_values[function][rotary_case][axis] = G54[axis] - ((l_bound + u_bound) / 2)
                    case_list.append(G54[axis] - ((l_bound + u_bound) / 2))

                elif axis == 'z':
                    case_list.append(min(fpass_xyz[function][rotary_case][axis][i]['position_{}'.format(axis)]))

        error_values[function][rotary_case] = case_list

#%%
# calculate the average value for each rotary case and log in a df
error_valuesAverage = pd.DataFrame()
# create a separate dataframe to hold the deviations from average
error_valuesDFA = copy.deepcopy(error_values)

for rotary_case in fpass:
    # omit G54.2 from B-90 C270
    #if rotary_case != 'B-90. C270.':
    average = (error_values['G54.2'][rotary_case] + error_values['G43'][rotary_case] + error_values['G43.4'][rotary_case] + error_values['G68.2'][rotary_case]) / 4
    #else:
     #   average = (error_values['G43'][rotary_case] + error_values['G43.4'][rotary_case] + error_values['G68.2'][rotary_case]) / 3
    error_valuesAverage[rotary_case] = average

for function in functions:
    for rotary_case in fpass:
        error_valuesDFA[function][rotary_case] = error_values[function][rotary_case] - error_valuesAverage[rotary_case]

for function in functions:
    error_valuesDFA[function]['axis'] = ['x', 'y', 'z']
    error_valuesDFA[function] = error_valuesDFA[function].set_index('axis')

print(error_valuesDFA)


        # error_euclidian[function][rotary_case] = ( (error_values[function][rotary_case]['x'] - error_valuesAverage[rotary_case][0]) ** 2 + (error_values[function][rotary_case]['y'] - error_valuesAverage[rotary_case][1]) ** 2) ** 0.5
    # error_vectors[rotary_case] = abs(error_vectors[rotary_case])


#%%
# plot the distances from average and save to file

B0_steps = ['B0. C0.', 'B0. C90.', 'B0. C180.', 'B0. C270.', 'B0. C360.']
Bp90_steps = ['B90. C0.', 'B90. C90.', 'B90. C180.', 'B90. C270.']
Bn90_steps = ['B-90. C0.', 'B-90. C90.', 'B-90. C180.', 'B-90. C270.'] 
markers = ['.--', 'x--', '+--', 'v--']
alpha = 0.7

def plot_distances():
    plt.close('all')
    fig = plt.figure(figsize=(15,10))
    ax_title = fig.add_subplot(111, frameon = False)
    ax_title.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    ax_title.grid(False)
    ax_title.axis('off')

    axs = {}
    axs[1] = fig.add_subplot(331)
    axs[2] = fig.add_subplot(332)
    axs[3] = fig.add_subplot(333)    
    axs[4] = fig.add_subplot(334)
    axs[5] = fig.add_subplot(335)
    axs[6] = fig.add_subplot(336)
    axs[7] = fig.add_subplot(337)
    axs[8] = fig.add_subplot(338)
    axs[9] = fig.add_subplot(339)

    i = 1
    for axis in xyz_init:
        legend_status = False
        for function, marker in zip(functions, markers):
            if axis == 'z':
                legend_status = True
            error_valuesDFA[function][B0_steps].loc[axis].T.plot(style=marker, ax=axs[i], label = function, legend=legend_status, alpha=alpha)
            error_valuesDFA[function][Bp90_steps].loc[axis].T.plot(style=marker, ax=axs[i+3], label = function, legend=False, alpha=alpha)
            # remove the last G54.2 point as the data is garbage
            #if function != 'G54.2':
            error_valuesDFA[function][Bn90_steps].loc[axis].T.plot(style=marker, ax=axs[i+6], label = function, legend=False, alpha=alpha)
            #else:
              #  error_valuesDFA[function][Bn90_steps[:-1]].loc[axis].T.plot(style=marker, ax=axs[i+6], label = function, legend=False, alpha=alpha)
        axs[i].set_title('Commanded position from average in {}'.format(axis))
        i += 1

    axs[3].legend(loc='upper left', bbox_to_anchor=(1,1))

   # ax_title.set_title('Euclidian distance from average feature centre point by method')
    fig.show()
    fig.savefig('NC_methods-git/Results/Controller/average_step_deviations.tiff', format='tiff', facecolor='white')

plot_distances()


#%%


 

