# -*- coding: utf-8 -*-
"""
Created on Tue May 21 16:40:48 2019

@author: mep16tjr
"""

import numpy as np
import os
os.chdir('C:/Users/mep16tjr/Desktop/Python/NC Methods/year_3/NMV_trials/NC_methods-git/Code')
from error_model_nmv8000 import HTM
#import shutil
os.chdir('C:/Users/mep16tjr/Desktop/CATIA/Programs')

#%% ===========================================================================
# Initialise
# =============================================================================

print('\n ######################################################### \n\nGenerate alternative NC-Codes for volumetric compensation trial\n \n ######################################################### \n')

tool_num = input('What is the tool number?                ')
w_offset = [float(input('What is the program zero offset from G54 in X?   ')), 
            float(input('What is the program zero offset from G54 in Y?   ')),
        float(input('What is the program zero offset in from G54 Z?   '))
        ]
program_zero = 'X{}. Y{}. Z{}.'.format(w_offset[0], w_offset[1], w_offset[2])

rot = ['B0. C0.',
            'B0. C90.',
            'B0. C180.',
            'B0. C270.',
            'B0. C360.', 
            'B90. C0.',
            'B90. C90.',
            'B90. C180.',
            'B90. C270.',
            'B-90. C0.',
            'B-90. C90.',
            'B-90. C180.',
            'B-90. C270.'
            ]
#%% ===========================================================================
# G54.2 preprocessing
# =============================================================================
#initialise
test = 0
edit = False
convert_neg90 = False

def find_lin_pos(line):
    X_start = line.find('X')
    Z_end = line.find('F')
    return X_start, Z_end

def G54_2_Bneg90_convert(line):    
    X_start = line.find('X') + 1
    if line[X_start] == '-':
        line_converted = '{}{}'.format(line[:X_start], line[X_start+1:])        #flip safety position also
    else:
        line_converted = '{}-{}'.format(line[:X_start], line[X_start:])
    return line_converted

with open('NC1661T_01_010_A (O0001).nc', 'r') as g54_2_read:
    with open('NC1661T_01_010_A.nc', 'w') as g54_2:
    
        for line in g54_2_read:
            #Correct rotation cases for trial
            if edit == True:
                X_start, Z_end = find_lin_pos(line)
                
                if 'B0' in rot[test]: 
                    #go to safety clearance, set rotation axes to home then rotate independently
                    g54_2.write("""N00 G1 G54.2 P0
N00 G1 G58 Z-300. F7480. ( SAFETY MOVE )
N00 G1 X0. Y0.
N00 G1 G54
N00 G1 G54.2 P1
N00 M11
N00 M69
N00 G1 {} {}  ( ROTATE )\n""".format(line[Z_end:-1], rot[test])) 
                    #reapproach part for machining
                    g54_2.write('N00 G1 G54 {} F7480. ( START )\n'.format(line[X_start:-6]))                         
                    
                elif 'B-90' in rot[test]:
                    g54_2.write("""N00 G1 G54.2 P0
N00 G1 G59 Z-300. F7480. ( SAFETY MOVE )
N00 G1 X0. Y0.
N00 G1 G54
N00 G1 G54.2 P1
N00 M11
N00 M69
N00 G1 {} {}  ( ROTATE )\n""".format(line[Z_end:-1], rot[test])) 
                    line_converted = G54_2_Bneg90_convert(line)
                    g54_2.write('N00 G1 G54 {} F7480. ( START )\n'.format(line_converted[X_start:line_converted.find('C')])) #line_converted.find('C')]                        #reapproach part for machining
                    convert_neg90 = True
                             
                else:
                    g54_2.write("""N00 G1 G54.2 P0
N00 G1 G58 Z-300. F7480. ( SAFETY MOVE )
N00 G1 X0. Y0.
N00 G1 G54
N00 G1 G54.2 P1
N00 M11
N00 M69
N00 G1 {} {}  ( ROTATE )\n""".format(line[Z_end:-1], rot[test])) 
                    g54_2.write('N00 G1 G54 {} F7480. ( START )\n'.format(line[X_start:-6]))                         #reapproach part for machining                test = test + 1
                
                test = test + 1
                edit = False
            
            #Insert placeholders with M1 stops for each test condition, activate edit mode for above boolean 
            elif 'M3' in line:
                g54_2.write('{} ( STOP )\n\nN00 ( TEST CONDITION {}: {} )\n\n'.format(line[:-1], test, rot[test]))
                edit = True
                convert_neg90 = False
            
            elif 'M5' in line:
               convert_neg90 = False
               g54_2.write('{} ( PROGRAM END )\n'.format(line[:-1]))
               
            elif 'M6' in line:
                line = 'N00 T{} M6\nN00 M11\nN00 M69\n'.format(tool_num)
                g54_2.write(line)
            
            elif 'G43' in line:
                line = 'N00 G43 H{} \n'.format(tool_num)
                g54_2.write(line)   
               
            elif convert_neg90 == True:
                line_converted = G54_2_Bneg90_convert(line)
                g54_2.write(line_converted)
                convert_neg90 == True
                
            else:
                g54_2.write(line)  

print('\n ######################################################### \n\nProgram NC1661T_01_010_A (G54.2) Posted')
#%% ===========================================================================
# G43.4 RTCP
# =============================================================================
 #initialise
test = -1
edit_tlpath = False
rtcp_activated = False
safety_clearance = 50
safe_position = False
safe_position_plus90 = False
safe_position_neg90 = False

safety_clearance_xy = {
        'B0. C0.': 'X0. Y0.',
        'B0. C90.': 'X0. Y0.',
        'B0. C180.': 'X0. Y0.',
        'B0. C270.': 'X0. Y0.',
        'B0. C360.': 'X0. Y0.', 
        'B90. C0.': 'X200. Y0.',
        'B90. C90.': 'X200. Y200.',
        'B90. C180.': 'X-200. Y200.',
        'B90. C270.': 'X-200. Y-200.',
        'B-90. C0.': 'X-100. Y0.',
        'B-90. C90.': 'X-100. Y-100.',
        'B-90. C180.': 'X200. Y-200.',
        'B-90. C270.': 'X200. Y200.'
        }

def conversion_commit(line, X, Y, Z, rot_func):  
    positions = [line.find('X'), line.find('Y'), line.find('Z')]
    conversions = [X, Y, Z]
    
    # skip controls the conversion of -ve positions when the conversion strategy itself is -ve
    # 1 for standard skip to next character, 2 to skip the position's sign and remove the strategy's sign (making a positive value)    
    def handle_negatives(positions, conversions):
        skip = np.zeros(3)   
        for i, j, k in zip(positions, conversions, [0, 1, 2]):
            if '-' in j:
                if line[i+1] == '-':
                    conversions[k] = j[0]
                    skip[k] = 2
                else:
                    skip[k] = 1
            else:
                skip[k] = 1
        return conversions, skip
    conversions, skip = handle_negatives(positions, conversions)
        
    commit = '{}{}{}{}{}{}{}'.format(                         
        line[:positions[0]],
        conversions[0],
        line[positions[0]+int(skip[0]):positions[1]],
        conversions[1],
        line[positions[1]+int(skip[1]):positions[2]],
        conversions[2],
        line[positions[2]+int(skip[2]):]
        )
    
    rot_func.write(commit)
  
with open('NC1661T_01_010_A.nc', 'r') as g54_2:
    with open('NC1661T_01_030_A.nc', 'w') as g43_4:
    
        for line in g54_2:
            #top level housekeeping
            if '( STOP )' in line:
                line = line
                edit_tlpath = False
            
            elif safe_position == True:
                if safe_position_plus90 == True:
                    line = 'N00 G1 X100. Y-100.\n'
                    safe_position_plus90 = False
                    safe_position_neg90 = True
                    
#                elif 'B90' in rot[test]:
#                    line = 'N00 G1 {}\n'.format(safety_clearance_xy[rot[test]])
#                elif 'B-90' in rot[test]:
#                    line = 'N00 G1 {}\n'.format(safety_clearance_xy[rot[test]])
                else:
                    line = ''
                safe_position=False
                
#            elif 'B0' in rot[test] and rot[test] != 'B0. C0.' and '( ROTATE )' in line:
#                    #kick the b-axis by -1 deg to rotate
#                    C = rot[test].find('C')
#                    B = rot[test].find('B')
#                    line = """N00 G1 B-1. F300. ( KICK TO B-1 TO ROTATE ) \nN00 G1 {}. ( ROTATE ) \nN00 G1 {}. \n""".format(
#                            rot[test][C:C + rot[test][C:].find('.')], 
#                            rot[test][B:B + rot[test][B:].find('.')]
#                            )
            
            elif safe_position_neg90 == True and '( ROTATE )' in line:    
                line = 'N00 N00 G1 F300. B0. X150. Y0. ( ROTATE )\nN00 G1 F300. B-90. X200. Y100. ( ROTATE )\nN00 G1 F300. C0. X-200. Y200. ( ROTATE )\n'
                safe_position_neg90 = False
                
            elif '( ROTATE )' in line:
                line = '{}{} {}'.format(line[:line.find('(')], safety_clearance_xy[rot[test]], line[line.find('('):])
                safe_position = False
#            elif '( ROTATE )' in line:
#                line = '{} 100. {}'.format(line[:line.find('(')], line[line.find('('):])
#                
            elif 'TEST CONDITION' in line:
                line = line
                test = test + 1
#                print(line)
            
            elif '( PROGRAM END )' in line:
                line = 'N00 M5 ( END )\n'
                edit_tlpath = False
                
            elif 'G54.2 P0' in line:
                line = ''
 
            elif 'G54.2 P1' in line:
               line = ''
            
#            elif 'M68' in line or 'M10' in line:
#                line = 'N00 ( NO CLAMP FOR RTCP )\n'
                    
            elif 'O0001 (01_010_A)' in line:
                line = ('O0001 (NC1661T_01_030_A)\n')
            
            elif 'G94 G97' in line:
                line = ''
                            
            elif 'G43' in line:
                line = ('N00 G94 G97 \nN00 G55\n{} G43.4 H{}\nN00 G01 F300.\n'.format(line[:3], tool_num))
                rtcp_activated = True
                
            elif 'G54' in line:
                G54_loc = line.find('G54')
                line = '{}{}'.format(line[:G54_loc], line[G54_loc+3:])  
                
            elif '( SAFETY MOVE )' in line:
                if rot[test] == 'B-90. C0.':    
                    line = 'N00 G1 Z0. ( SAFETY MOVE )\n'
                    safe_position_plus90 = True
                else:
                    line = 'N00 G1 Z{}. ( SAFETY MOVE )\n'.format(safety_clearance)
                safe_position = True
                
            if edit_tlpath == True: 
                if 'M68' in line or 'M10' in line:
                    line = 'N00 ( NO CLAMP FOR RTCP )\n'
                    g43_4.write(line)
                    
                elif test == 0:                                                   #B0C0, no conversion
                    g43_4.write(line)
                    
                elif 'M10' in line or 'M68' in line:
                    g43_4.write(line)
                
            #convert tool path from 54.2 to 43.4
                elif rot[test] == 'B0. C90.':                                                 #B0C90 CONDITION 1
                    X_rtcp = 'Y'                                                #conversion strategy for rtdfo to rtcp
                    Y_rtcp = 'X-'
                    Z_rtcp = 'Z'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)
                    
                elif rot[test] == 'B0. C180.':                                                 #B0C180 CONDITION 2
                    X_rtcp = 'X-'                                                
                    Y_rtcp = 'Y-'
                    Z_rtcp = 'Z'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)
                    
                elif rot[test] == 'B0. C270.':                                                 #B0C270 CONDITION 3
                    X_rtcp = 'Y-'                                                
                    Y_rtcp = 'X'
                    Z_rtcp = 'Z'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)
                    
                elif rot[test] == 'B0. C360.':                                                 #B0C360  CONDITION 4
                    X_rtcp = 'X'                                                
                    Y_rtcp = 'Y'
                    Z_rtcp = 'Z'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)

                elif rot[test] == 'B90. C0.':                                                 #B90C0  CONDITION 5
                    X_rtcp = 'Z-'                                                
                    Y_rtcp = 'Y'
                    Z_rtcp = 'X'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)

                elif rot[test] == 'B90. C90.':                                                 #B90C90  CONDITION 6
                    X_rtcp = 'Z-'                                                
                    Y_rtcp = 'X-'
                    Z_rtcp = 'Y'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)

                elif rot[test] == 'B90. C180.':                                                 #B90C180  CONDITION 7
                    X_rtcp = 'Z-'                                                
                    Y_rtcp = 'Y-'
                    Z_rtcp = 'X-'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)

                elif rot[test] == 'B90. C270.':                                                 #B90C270  CONDITION 8
                    X_rtcp = 'Z-'                                                
                    Y_rtcp = 'X'
                    Z_rtcp = 'Y-'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)
                    
                elif rot[test] == 'B-90. C0.':                                                 #B-90C0 CONDITION 9
                    X_rtcp = 'Z'                                                
                    Y_rtcp = 'Y'
                    Z_rtcp = 'X-'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)

                elif rot[test] == 'B-90. C90.':                                                 #B-90C90 CONDITION 10
                    X_rtcp = 'Z'                                                
                    Y_rtcp = 'X-'
                    Z_rtcp = 'Y-'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)

                elif rot[test] == 'B-90. C180.':                                                 #B-90C180 CONDITION 11
                    X_rtcp = 'Z'                                                
                    Y_rtcp = 'Y-'
                    Z_rtcp = 'X'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)
#
                elif rot[test] == 'B-90. C270.':                                                 #B-90C270 CONDITION 12
                    X_rtcp = 'Z'                                                
                    Y_rtcp = 'X'
                    Z_rtcp = 'Y'
                    conversion_commit(line, X_rtcp, Y_rtcp, Z_rtcp, g43_4)
                    
            elif edit_tlpath == False:
                g43_4.write(line)  
                if '( ROTATE )' in line:
                    edit_tlpath = True

print('Program NC1661T_01_030_A (G43.4) Posted')
#%% ===========================================================================
# G43 with kinematic model
# =============================================================================
#initialise
test = -1
clamp_on = 0
edit_tlpath = False
safety_xy = False

def find_XYZ(line):
    pos_start = line.find('X'), line.find('Y'), line.find('Z')
    pos_end = [pos_start[x] + line[pos_start[x]:].find(' ') for x in [0,1,2]]
    for x in [0,1,2]:
        if line[pos_start[x]:].find(' ') == -1:
            pos_end[x] = -1
    XYZ = [line[pos_start[i] + 1 : pos_end[i]] for i in [0,1,2]]
    
    return XYZ, pos_start, pos_end

with open('NC1661T_01_030_A.nc', 'r') as g43_4:
    with open('NC1661T_01_020_A.nc', 'w') as g43:
    
        for line in g43_4:
            #top level housekeeping
            if '( STOP )' in line or '( END )' in line:
                line = line
                edit_tlpath = False
                
            elif 'TEST CONDITION' in line:
                line = line
                test = test + 1
#                print(line)
            
            elif '( PROGRAM END )' in line:
                line = 'N00 M5 ( END )\n'
                edit_tlpath = False
            
            elif 'G43.4' in line:
                line = 'N00 G43 H{}\n'.format(tool_num)
                    
            elif 'O0001 (01_030_A)' in line:
                line = ('O0001 (NC1661T_01_020_A)\n')
            
            elif safety_xy == True:
                line = 'N00 G1 X0. Y0.\nN00 M11\n'
                safety_xy = False
                
            elif '( SAFETY MOVE )' in line:
                if 'B0' in rot[test] or 'B90' in rot[test]:
                    line = 'N00 G1 G58 Z-250. ( SAFETY MOVE )\n'
                    safety_xy = True
                elif 'B-90' in rot[test]:
                    line = 'N00 G1 G59 Z-250. ( SAFETY MOVE )\n'
                    safety_xy = True
                
            elif 'G55' in line:
                line = '{}G54{}'.format(
                        line[:line.find('G55')],
                        line[line.find('G55') + 3:]
                            )
                
            if '( ROTATE )' in line:# and rot[test] == 'B-90. C0.':
                line = '{}( ROTATE )\nN00 G54\n'.format(line[:line.find('X')])
            
#            elif '( ROTATE )' in line:
#                line = '{}N00 G54\n'.format(line)    
                
            if '( START )' in line:
                edit_tlpath = True
            
            #convert tool tip CL data into G54 with kinematics already handled 
            if edit_tlpath == True:
                
                XYZ, pos_start, pos_end = find_XYZ(line)
                b = float(rot[test][rot[test].find('B') + 1 : rot[test].find('.')])
                c = float(rot[test][rot[test].find('C') + 1 : rot[test][rot[test].find('C')].find('.')])
                
                XYZ = HTM(float(XYZ[0]), float(XYZ[1]), float(XYZ[2]), b, c, w_offset)
                
                XYZ_start = min([len(line[:pos_start[x]]) for x in [0,1,2]])
                XYZ_end = max([len(line[:pos_end[x]]) for x in [0,1,2]])

                line = '{}X{} Y{} Z{}{}'.format(
                        line[:XYZ_start],
                        float(XYZ[0]),
                        float(XYZ[1]),
                        float(XYZ[2]),
                        line[XYZ_end:]
                        )
                
                g43.write(line)
                
            else:
                g43.write(line)    

print('Program NC1661T_01_020_A (G43) Posted')
#%% ===========================================================================
# G68.2 3+2
# =============================================================================
                    
 #initialise
test = -1
edit_tlpath = False
home_axes = False
IJK = {
        'B0. C0.': 'I0. J0. K0.',
        'B0. C90.': 'I90. J0. K0.',
        'B0. C180.': 'I180. J0. K0.',
        'B0. C270.': 'I270. J0. K0.',
        'B0. C360.': 'I360. J0. K0.', 
        'B90. C0.': 'I90. J90. K-90.',
        'B90. C90.': 'I0. J-90. K90.', 
        'B90. C180.': 'I90. J-90. K90.',
        'B90. C270.': 'I0. J90. K-90.',
        'B-90. C0.': 'I90. J-90. K-90.',
        'B-90. C90.': 'I0. J90. K90.',
        'B-90. C180.': 'I90. J90. K90.',
        'B-90. C270.': 'I0. J-90. K-90.'
        }
  
with open('NC1661T_01_010_A.nc', 'r') as g54_2:
    with open('NC1661T_01_040_A.nc', 'w') as g68_2:
    
        for line in g54_2:
            #top level housekeeping
            if '( STOP )' in line:
                line = '{}N00 G49 \nN00 G1 G69 ( TILTED WORKPLANE CANCEL )\n'.format(line)
            
            elif '( START )' in line:
                C = line.find('C')
                B = line.find('B')
                G54 = line.find('G54') + 4
                
                if C != -1:
                    line = 'N00 G1 {}( START )\n'.format(line[G54:C])
                elif B != -1:
                    line = 'N00 G1 {}( START )\n'.format(line[G54:B])
                else:
                    line = 'N00 G1 {}'.format(line[G54:])
            
            elif '( ROTATE )' in line:
                if rot[test] == 'B-90. C0.':
                    line = """N00 G1 B-1. F300. ( INIT TILT FOR SHORTEST PATH )
N00 G49
N00 G69
N00 G55 
N00 G1 G68.2 X0. Y0. Z0. {} F300. ( ROTATE )
N00 G53.1
N00 G43 H{}\n""".format(
                            IJK[rot[test]],
                            tool_num
                            )   
                    
                elif 'B0' in rot[test] and rot[test] != 'B0. C0.':
                    #kick the b-axis by -1 deg to rotate
                    J = IJK[rot[test]].find('J')
                    angle = int(IJK[rot[test]][1:J-2]) 
                    b_kick = """( KICK TO B-1 TO ROTATE ) 
N00 G49 
N00 G69 
N00 G55 
N00 G1 G68.2 X0. Y0. Z0. I{}. J-1. K-90. F300. 
N00 G53.1 
N00 G43 H{} 
N00 G49 
N00 G69 
N00 G55 
N00 G1 G68.2 X0. Y0. Z0. I{}. J-1. K-90. F300. 
N00 G53.1 
N00 G43 H{}\n""".format(
                            angle,
                            tool_num,
                            angle + 90, 
                            tool_num
                            )
                    rot_line = """N00 G49
N00 G69
N00 G55
N00 G1 G68.2 X0. Y0. Z0. {} F300. ( ROTATE )
N00 G53.1
N00 G43 H{}\n""".format(
                            IJK[rot[test]],
                            tool_num
                            )   
                    line = b_kick + rot_line
                else:
                    line = 'N00 G1 G55\nN00 G49\nN00 G69\nN00 G1 G68.2 X0. Y0. Z0. {} F300. ( ROTATE )\nN00 G53.1\nN00 G43 H{}\n'.format(
                            IJK[rot[test]],
                            tool_num
                            )

            elif '( SAFETY MOVE )' in line:
                home_axes = True
                if 'B-90.' in rot[test]:
                    line = 'N00 G1 G59 Z0. F7480. ( SAFETY MOVE )\n '
                else:
                    line = 'N00 G1 G58 Z0. F7480. ( SAFETY MOVE )\n '
                
            elif 'TEST CONDITION' in line:
                line = line
                test = test + 1
            
            elif '( PROGRAM END )' in line:
                line = 'N00 M5 ( END )\n'
                
            elif 'G54.2 P0' in line:
                line = ''
 
            elif 'G54.2 P1' in line:
               line = ''
                    
            elif 'O0001 (01_010_A)' in line:
                line = ('O0001 (NC1661T_01_040_A)\n')

            else:
                line = line
                
            g68_2.write(line)
            
print('Program NC1661T_01_040_A (G68.2) Posted\n\n ######################################################### \n\n')
