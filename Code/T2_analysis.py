# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 15:04:30 2019

@author: mep16tjr
"""

import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import copy
plt.style.use('ggplot')
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
#%%
# =============================================================================
# Define the G-code blocks which contain finish pass moves
# =============================================================================
xyz_init = {'x' : {}, 'y' : {}, 'z' : {}}
fpass = {'B0. C0.': copy.deepcopy(xyz_init),
            'B0. C90.': copy.deepcopy(xyz_init),
            'B0. C180.': copy.deepcopy(xyz_init),
            'B0. C270.': copy.deepcopy(xyz_init),
            'B0. C360.': copy.deepcopy(xyz_init), 
            'B90. C0.': copy.deepcopy(xyz_init),
            'B90. C90.': copy.deepcopy(xyz_init),
            'B90. C180.': copy.deepcopy(xyz_init),
            'B90. C270.': copy.deepcopy(xyz_init),
            'B-90. C0.': copy.deepcopy(xyz_init),
            'B-90. C90.': copy.deepcopy(xyz_init),
            'B-90. C180.': copy.deepcopy(xyz_init),
            'B-90. C270.': copy.deepcopy(xyz_init)
            }

# Block identifiers are the actual N(xxxx) block numbers, not lines in the nc file
# Blocks are identified for the finishing pass and separated into XYZ as per the MCS orientation (and G54.2)
# for eg, B90 C0 
    # the X fpass is the top of the step (if the block was upright) with X at a constant position
    # the Y fpass is the two sides of the step (vertical faces if the block was upright) with Y at a constant position
    # the Z fpass is the surface which connects to the B-90 feature (facing outwards if the block was upright), comprising 3 tool paths

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

# =============================================================================
# Define the times which test started/ended
# =============================================================================
ttimes_init = {'dt_start' : [], 'dt_stop' : []}
test_time = {'G54.2' : copy.deepcopy(ttimes_init),
             'G43' : copy.deepcopy(ttimes_init),
             'G43.4' : copy.deepcopy(ttimes_init),
             'G68.2' : copy.deepcopy(ttimes_init)
             }
#specify the time and day of each data collection interval
test_time['G54.2']['dt_start'] = ['23 15:20', '23 15:36', '24 08:19', '24 09:09', '25 09:30', '25 10:39']
test_time['G54.2']['dt_stop'] = ['23 15:35', '23 15:50', '24 09:00', '24 09:25', '25 10:00', '25 10:51']

test_time['G43']['dt_start'] = ['24 09:28', '24 10:34', '25 11:06'] 
test_time['G43']['dt_stop'] = ['24 10:00', '24 11:15', '25 12:00']

test_time['G43.4']['dt_start'] = ['24 12:55', '24 14:08', '24 15:32', '25 11:49', '25 12:36', '25 14:26']
test_time['G43.4']['dt_stop'] = ['24 13:30', '24 14:45', '24 16:05', '25 12:00', '25 13:00', '25 15:00']

test_time['G68.2']['dt_start'] = ['24 15:15', '25 15:06', '26 08:00', '26 08:52'] 
test_time['G68.2']['dt_stop'] = ['24 15:30', '25 16:00', '26 08:40', '26 09:40']

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
        if axis == 'x' or axis == 'y':    
            if 'C0.' in rotary_case or 'C360.'  in rotary_case:
                data['position_{}'.format(axis)] -= offsets[axis_1]
            elif 'C90.' in rotary_case:
                data['position_{}'.format(axis)] -= offsets[axis_2] 
            elif 'C180.' in rotary_case:
                data['position_{}'.format(axis)] += offsets[axis_1]                   
            elif 'C270.' in rotary_case:
                data['position_{}'.format(axis)] += offsets[axis_2]
    
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

#%%
B0_steps = ['B0. C0.', 'B0. C90.', 'B0. C180.', 'B0. C270.', 'B0. C360.']
Bp90_steps = ['B90. C180.']#, 'B90. C90.', 'B90. C180.', 'B90. C270.']
Bn90_steps = ['B-90. C90.']#, 'B-90. C90.', 'B-90. C180.', 'B-90. C270.']        
i=1
fig = plt.figure(figsize=(8,8))
plt.close('all')
ax = fig.add_subplot(111)
for rotary_case in Bp90_steps:
    ax.plot(fpass_xyz['G54.2'][rotary_case]['x'][i]['position_x'], fpass_xyz['G54.2'][rotary_case]['y'][i]['position_y'], c='red', linestyle = '--', label = 'G54.2')
    ax.plot(fpass_xyz['G43'][rotary_case]['x'][i]['position_x'], fpass_xyz['G43'][rotary_case]['y'][i]['position_y'], c='blue', linestyle = '-', label = 'G43')
    ax.plot(fpass_xyz['G43.4'][rotary_case]['x'][i]['position_x'], fpass_xyz['G43.4'][rotary_case]['y'][i]['position_y'], c='green', linestyle = ':', label = 'G43.4')
    ax.plot(fpass_xyz['G68.2'][rotary_case]['x'][i]['position_x'], fpass_xyz['G68.2'][rotary_case]['y'][i]['position_y'], c='orange', linestyle = '-.', label = 'G68.2')
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
ax.set_title('Commanded MCS position tool paths\nfor step machinined at {}'.format(rotary_case))
fig.show()





#%%
fpass_xyz['G43']['B0. C270.']['y'][1]
#fpass_xyz['G43'][rotary_case]['x'][i]['position_y']















#%%
# =============================================================================
# Find the XYZ positions which relate to the found local_times
# ============================================================================
fpass_xyz = {'G54.2' : copy.deepcopy(fpass),
                   'G43' : copy.deepcopy(fpass),
                   'G43.4' : copy.deepcopy(fpass),
                   'G68.2' : copy.deepcopy(fpass)
                   }

log = False

for function in fpass_LocalTime:
    for rotary_case in fpass:
        for axis in xyz_init:
            for t in range(len(test_time[function]['dt_start'])):
                local_time = fpass_LocalTime[function][rotary_case][axis][t]['local_time']
    #                if i != 0:
    #                    if local_time[i] != local_time[i-1]:
    #                        log = True
    #                    else:
    #                        log = False
    #                else:
    #                    log = True
    #                if log == True:

                try:
                    sql = ("""
                           SELECT local_time, position_{} FROM datalake.position_{}
                           WHERE local_time BETWEEN '{}' AND '{}' AND datasource_id = 3;
                           """.format(
                           axis,
                           axis,
                           local_time.iloc[0],
                           local_time.iloc[-1]
                           )
                           )  
            
                    data = pd.read_sql(sql, conn)
        #                    for j in range(len(data)):
        #                        if i == 0:
                            
                    fpass_xyz[function][rotary_case][axis][t] = data
                    
                except IndexError as e1:
                    print('Index error on {} {} {}: {}'.format(
                            function,
                            rotary_case,
                            axis, 
                            e1
                            )
                          )

#def plot_vm_axisloads(measurement_name, datetime_start=None, datetime_end=None, plot_infunction=False):
#    #plots controller stream for individual measurements, takes datetime with format YYYY-MM-DD HH-MM-SS
#    plt.close('all')
#    global data
#    if datetime_end == 'latest':
#        now = datetime.datetime.now()
#        datetime_end = ('%02d-%02d-%02d %02d:%02d:%02d'%(now.year, now.month, now.day, now.hour, now.minute, now.second))
#    if datetime_start == 'oldest':
#        datetime_start = '2019-02-25 09:00:00'
#        
#    custom_dict = {
#            'measurement_name' : measurement_name,
#            'dt_start' : '{}.000'.format(datet/ime_start),            
#            'dt_end' : '{}.000'.format(datetime_end)
#            }
#
#    sql = ("""
#           SELECT datasource_id, local_time, %(measurement_name)s FROM datalake.%(measurement_name)s
#           WHERE local_time BETWEEN '%(dt_start)s' AND '%(dt_end)s';
#           """ % custom_dict
#           )          
#    
#    data = pd.read_sql(sql, conn)  
#    if plot_infunction == True:
#        plt.plot(data.local_time, data[measurement_name], markersize=1)
#    return data.local_time, data[measurement_name]