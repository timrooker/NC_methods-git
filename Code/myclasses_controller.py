import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import copy
import os
import numpy as np
# os.chdir(r'C:\Users\mep16tjr\Desktop\Python\02 NC Methods')

class process_results(object):

    def __init__(self, test_type):
        # initialise dict
        self.ttimes_init = {'dt_start' : [], 'dt_stop' : []}
        self.test_type = test_type
        self.test_time = {'G54.2' : copy.deepcopy(self.ttimes_init),
                'G43' : copy.deepcopy(self.ttimes_init),
                'G43.4' : copy.deepcopy(self.ttimes_init),
                'G68.2' : copy.deepcopy(self.ttimes_init)
                }
        self.functions = ['G43', 'G43.4', 'G54.2', 'G68.2']
        self.xyz_init = {'x' : {}, 'y' : {}, 'z' : {}}


        if test_type == 'machining':
            self.test_time['G54.2']['dt_start'] = ['23 15:20', '23 15:36', '24 08:19', '24 09:09', '25 09:30', '25 10:39']
            self.test_time['G54.2']['dt_stop'] = ['23 15:35', '23 15:50', '24 09:00', '24 09:25', '25 10:00', '25 10:51']

            self.test_time['G43']['dt_start'] = ['24 09:28', '24 10:34', '25 11:06'] 
            self.test_time['G43']['dt_stop'] = ['24 10:00', '24 11:15', '25 12:00']

            self.test_time['G43.4']['dt_start'] = ['24 12:55', '24 14:08', '24 15:32', '25 11:49', '25 12:36', '25 14:26']
            self.test_time['G43.4']['dt_stop'] = ['24 13:30', '24 14:45', '24 16:05', '25 12:00', '25 13:00', '25 15:00']

            self.test_time['G68.2']['dt_start'] = ['24 15:15', '25 15:06', '26 08:00', '26 08:52'] 
            self.test_time['G68.2']['dt_stop'] = ['24 15:30', '25 16:00', '26 08:40', '26 09:40']

            self.positions_dict = {'B0. C0.': copy.deepcopy(self.xyz_init),
            'B0. C90.': copy.deepcopy(self.xyz_init),
            'B0. C180.': copy.deepcopy(self.xyz_init),
            'B0. C270.': copy.deepcopy(self.xyz_init),
            'B0. C360.': copy.deepcopy(self.xyz_init), 
            'B90. C0.': copy.deepcopy(self.xyz_init),
            'B90. C90.': copy.deepcopy(self.xyz_init),
            'B90. C180.': copy.deepcopy(self.xyz_init),
            'B90. C270.': copy.deepcopy(self.xyz_init),
            'B-90. C0.': copy.deepcopy(self.xyz_init),
            'B-90. C90.': copy.deepcopy(self.xyz_init),
            'B-90. C180.': copy.deepcopy(self.xyz_init),
            'B-90. C270.': copy.deepcopy(self.xyz_init)
            }

        elif test_type == 'probing':
            self.test_time['G43']['dt_start'] = ['23 08:00']
            self.test_time['G43']['dt_stop'] = ['23 09:15']

            self.test_time['G54.2']['dt_start'] = ['23 09:20'] 
            self.test_time['G54.2']['dt_stop'] = ['23 10:30']

            self.test_time['G43.4']['dt_start'] = ['23 11:31']
            self.test_time['G43.4']['dt_stop'] = ['23 13:30']

            self.test_time['G68.2']['dt_start'] = ['23 10:45']
            self.test_time['G68.2']['dt_stop'] = ['23 11:30']

            positions = {620: {x :  copy.deepcopy(self.xyz_init) for x in ['B0. C0.', 'B0. C45.', 'B0. C90.', 'B0. C135.', 'B0. C180.', 'B0. C225.', 'B0. C270.', 'B0. C315.', 'B0. C360.']},
            621: {x : copy.deepcopy(self.xyz_init) for x in ['B-90. C0.', 'B-90. C45.', 'B-90. C90.', 'B-90. C135.', 'B-90. C180.', 'B-90. C225.', 'B-90. C270.', 'B-90. C315.', 'B-90. C360.']},
            622 : {x : copy.deepcopy(self.xyz_init) for x in ['B90. C0.', 'B90. C45.', 'B90. C90.', 'B90. C135.', 'B90. C180.', 'B90. C225.', 'B90. C270.', 'B90. C315.', 'B90. C360.']},
            623 : {x : copy.deepcopy(self.xyz_init) for x in ['B0. C0.', 'B15. C0.', 'B30. C0.', 'B45. C0.', 'B60. C0.', 'B75. C0.', 'B90. C0.']},
            624 : {x : copy.deepcopy(self.xyz_init) for x in ['B0. C0.', 'B-15. C0.', 'B-30. C0.', 'B-45. C0.', 'B-60. C0.', 'B-75. C0.', 'B-90. C0.']}
            }

            self.positions_dict = {'G43' : copy.deepcopy(positions),
                        'G43_4' : copy.deepcopy(positions),
                        'G54_2' : copy.deepcopy(positions),
                        'G68_2' : copy.deepcopy(positions)
                        }

    def return_dfs(self):
        return self.positions_dict, self.test_time, self.xyz_init

    def fpass_rot(self):
        # Block identifiers are the actual N(xxxx) block numbers, not lines in the nc file
        # Blocks are identified for the finishing pass and separated into XYZ as per the MCS orientation (and G54.2)
        # for eg, B90 C0 
            # the X fpass is the top of the step (if the block was upright) with X at a constant position
            # the Y fpass is the two sides of the step (vertical faces if the block was upright) with Y at a constant position
            # the Z fpass is the surface which connects to the B-90 feature (facing outwards if the block was upright), comprising 3 tool paths

        self.fpass_rot = copy.deepcopy(self.positions_dict)

        self.fpass_rot['B0. C0.']['x'], self.fpass_rot['B0. C0.']['y'], self.fpass_rot['B0. C0.']['z'] = [4169, 4251], [4087, 4128, 4210], [3958, 4014, 4042, 4098]
        self.fpass_rot['B0. C90.']['x'], self.fpass_rot['B0. C90.']['y'], self.fpass_rot['B0. C90.']['z'] = [7797, 7879, 7961], [7838, 7920], [7626, 7668, 7710, 7752]
        self.fpass_rot['B0. C180.']['x'], self.fpass_rot['B0. C180.']['y'], self.fpass_rot['B0. C180.']['z'] = [10788, 10870], [10747, 10829, 10911], [10576, 10618, 10660, 10702]
        self.fpass_rot['B0. C270.']['x'], self.fpass_rot['B0. C270.']['y'], self.fpass_rot['B0. C270.']['z'] = [13173, 13255, 13337], [13214, 13296], [13002, 13044, 13086, 13128]
        self.fpass_rot['B0. C360.']['x'], self.fpass_rot['B0. C360.']['y'], self.fpass_rot['B0. C360.']['z'] = [14854, 14936], [14813, 14895, 14977], [14684, 14726, 14768, 14810]

        self.fpass_rot['B90. C0.']['x'], self.fpass_rot['B90. C0.']['y'], self.fpass_rot['B90. C0.']['z'] = [15595], [15639, 15551], [16055, 16100, 16145]
        self.fpass_rot['B90. C90.']['x'], self.fpass_rot['B90. C90.']['y'], self.fpass_rot['B90. C90.']['z'] = [16794], [16750, 16838], [17254, 17299, 17344]
        self.fpass_rot['B90. C180.']['x'], self.fpass_rot['B90. C180.']['y'], self.fpass_rot['B90. C180.']['z'] = [17993], [17949, 18037], [18453, 18498, 18543]
        self.fpass_rot['B90. C270.']['x'], self.fpass_rot['B90. C270.']['y'], self.fpass_rot['B90. C270.']['z'] = [19192], [19148, 19236], [19652, 19697, 19742]

        self.fpass_rot['B-90. C0.']['x'], self.fpass_rot['B-90. C0.']['y'], self.fpass_rot['B-90. C0.']['z'] = [20382], [20338, 20426], [20834, 20879, 20924]
        self.fpass_rot['B-90. C90.']['x'], self.fpass_rot['B-90. C90.']['y'], self.fpass_rot['B-90. C90.']['z'] = [21561], [21517, 21605], [22013, 22058, 22103]
        self.fpass_rot['B-90. C180.']['x'], self.fpass_rot['B-90. C180.']['y'], self.fpass_rot['B-90. C180.']['z'] = [22740], [22696, 22784], [23192, 23237, 23282]
        self.fpass_rot['B-90. C270.']['x'], self.fpass_rot['B-90. C270.']['y'], self.fpass_rot['B-90. C270.']['z'] = [23919], [23875, 23963], [24371, 24416, 24461]

        return self.fpass_rot

