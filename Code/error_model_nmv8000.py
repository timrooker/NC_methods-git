# -*- coding: utf-8 -*-
"""
Created on Wed May 29 10:42:05 2019

@author: mep16tjr
"""
import numpy as np
import pandas as pd

def HTM(x,y,z,b,c,w_offset,q_w=None):
    #takes an input tool position q_w in the workpiece CSYS and translates it into the reference (machine G54 pivot point) CSYS
    #if q_w == None, input position is taken as program zero
    
    o_H_wp = np.matrix(([1, 0, 0, w_offset[0]],
                      [0, 1, 0, w_offset[1]],
                      [0, 0, 1, w_offset[2]],
                      [0, 0, 0, 1]
                      )) 
    
    def Trans_x(x):
        D_x = np.matrix(([1, 0, 0, x],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]
                          )  
        )
        return D_x
    
    def Trans_y(y):
        D_y = np.matrix(([1, 0, 0, 0],
                          [0, 1, 0, y],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]
                          )   
        )
        return D_y
    
    def Trans_z(z):
        D_z = np.matrix(([1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, z],
                          [0, 0, 0, 1]
                          )   
        )
        return D_z
    
    def Rot_b(b):                                                               #axis directions flipped for TT config, sines with diff signs to literature
        b = np.deg2rad(b)
        D_b = np.matrix(([np.cos(b), 0, -np.sin(b), 0],
                          [0, 1, 0, 0],
                          [np.sin(b), 0, np.cos(b), 0],
                          [0, 0, 0, 1]
                          )
        )
        return D_b
    
    def Rot_c(c):                                                               #axis directions flipped for TT config, sines with diff signs to literature
        c = np.deg2rad(c)
        D_c = np.matrix(([np.cos(c), np.sin(c), 0, 0],
                          [-np.sin(c), np.cos(c), 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]
                          )
        )
        return D_c
    
    if q_w == None:
        q_w = [0,0,0]
    
    o_T_tl = Trans_x(x) * Trans_y(y) * Trans_z(z)                               #linear translation in xyz, no tool offset necessary due to G43
    o_T_wp = Rot_b(b) * Rot_c(c) * o_H_wp                                       #rotary motion in b&c and offset to wp

    w_T_r = o_T_wp * o_T_tl
    
    q_w = np.matrix([q_w[0], q_w[1], q_w[2], 1]).T
    r_q = np.around((w_T_r * q_w), decimals = 4)

#    print('\ninput:\n', np.around(q_w, 4))
#    print('\noutput:\n', np.around(r_q, 4))
    return r_q

#%%
def error_model(B, C, e_p, w_offset=None, q_w=None):
    #takes an input tool position q_w in the workpiece CSYS and translates it into the reference (machine G54 pivot point) CSYS
    #if q_w == None, input position is taken as program zero
    
    P_ideal = HTM(0, 0, 0, B, C, w_offset=w_offset)
    
    
    def Trans_wo(w_offset):
        D_wo = np.matrix(([1, 0, 0, w_offset[0]],
                  [0, 1, 0, w_offset[1]],
                  [0, 0, 1, w_offset[2]],
                  [0, 0, 0, 1]
                  )) 
        return D_wo
        
    def Trans_x(x):
        D_x = np.matrix(([1, 0, 0, x],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]
                          )  
        )
        return D_x
    
    def Trans_y(y):
        D_y = np.matrix(([1, 0, 0, 0],
                          [0, 1, 0, y],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]
                          )   
        )
        return D_y
    
    def Trans_z(z):
        D_z = np.matrix(([1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, z],
                          [0, 0, 0, 1]
                          )   
        )
        return D_z 

    def Rot_b(b):                                                               
        b = np.deg2rad(b)
        D_b = np.matrix(([np.cos(b), 0, np.sin(b), 0],
                          [0, 1, 0, 0],
                          [-np.sin(b), 0, np.cos(b), 0],
                          [0, 0, 0, 1]
                          )
        )
        return D_b
    
    def Rot_c(c):                                                               
        c = np.deg2rad(c)
        D_c = np.matrix(([np.cos(c), -np.sin(c), 0, 0],
                          [np.sin(c), np.cos(c), 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]
                          )
        )
        return D_c
    
    def Err_rot(ex, ey, ez, theta):
        theta = np.deg2rad(theta)
        D_err_r = np.matrix(([  1,                      -ez * np.sin(theta),    ey * np.sin(theta),     0],
                          [     ez * np.sin(theta),     1,                      -ex * np.sin(theta),    0],
                          [     -ey * np.sin(theta),    ex * np.sin(theta),     1,                      0],
                          [     0,                      0,                      0,                      1]
                          )
        )
        return D_err_r
    
    def Err_trans(dx, dy, dz):
        D_err_t = np.matrix(([  1,      0,      0,      dx],
                          [     0,      1,      0,      dy],
                          [     0,      0,      1,      dz],
                          [     0,      0,      0,      1]
                          )
        )
        return D_err_t
    
    try:
        if q_w == None:
            q_w = [0,0,0]
    except ValueError:
        q_w = q_w
                
    r_T_tl = (Trans_y(P_ideal[1]) * Trans_x(P_ideal[0])) * Trans_z(P_ideal[2])

    B = Rot_b(B) * Err_rot(e_p['ex_B'], e_p['ey_B'], e_p['ez_B'], B) * Err_trans(e_p['dx_B'], e_p['dy_B'], e_p['dz_B'])
    C = Rot_c(C) * Err_rot(e_p['ex_C'], e_p['ey_C'], e_p['ez_C'], C) * Err_trans(e_p['dx_C'], e_p['dy_C'], e_p['dz_C'])

    r_T_wp =  B * C #* Trans_wo(w_offset)
    w_T_tl = r_T_wp * r_T_tl
    
    q_w = np.matrix([q_w[0], q_w[1], q_w[2], 1]).T
    r_q = np.around((w_T_tl.astype(float) * q_w.astype(float)), decimals = 4)
    error = P_ideal[:3] - r_q[:3]
    return r_q, error

# =============================================================================
# define data generation function
# =============================================================================
def generate_training_data(points, start_stop, fm, error_parameters, checker_cycle, shift_xy=None, shift_z=None):   
    
    ### FAULT MODES ###
    
    ### modelled kinematic faults ###
    ### A - ideal results, threshold 10%. limit generated data to 100um error and set <10um as this case.
    ### B - Primary axis kinematic error, dx_C
    ### C - Primary axis kinematic error, dy_C
    ### D - Primary axis kinematic error (combined)
    ### E - Secondary axis kinematic error (pivot point), dy_C (for BC config)
    ### F - Secondary axis kinematic error (pivot length), dz_C 
    ### G - Secondary axis kinematic error (combined), dy_C and dz_C
    ### H - Axis tilt error motion, ex_C for primary, ex_B for secondary
    ### I - Axis tilt error motion, ey_C for primary, ez_B for secondary
    ### J - Axis tilt error motion, ex_C and ey_C for primary, ex_B and ez_B for secondary (combined)
    
    ### REMOVE K AND L AS WE CANNOT DISCERN ANGULAR POSITIONING FROM PIVOT POINT + LENGTH COMBINED WITH PROBE PATTERNS
    ### need alternative solution to separate - higher order network/inference system
    ### K - Axis angular positioning error, ez_C for primary and ey_B for secondary
    ### L - Axis tilt and angular errors (combined)
    
    ### undefined additional faults ###
    ### AA - undefined mechanical, erratic
    ### BB - encoder/scale reader errors
    ### CC - compensation error

    if checker_cycle == 'ps0':                  
        r1 = np.zeros(points)
        r2 = np.linspace(start_stop[0], start_stop[1], points)

    elif checker_cycle == 'rs_plus_p0':
        r1 = np.linspace(start_stop[0], start_stop[1], points)
        r2 = np.zeros(points)
#        
    r1_ang_all = np.linspace(float(start_stop[0]), float(start_stop[1]), points)
        
    if len(fm) == 4: 
        fm = 'kinematic'
        
    if fm == 'kinematic':                                                               #kinematic error modelling for fm generation
            error_map = pd.DataFrame(data=np.zeros((4, len(r1_ang_all))))
            for i in range(len(r1_ang_all)):
                error_map[i], _ = error_model(r1[i], r2[i], error_parameters, w_offset=[0,0,0])
                
            data = {'Error X' : error_map.iloc[0], 
                                 'Error Y' : error_map.iloc[1], 
                                 'Error Z' : error_map.iloc[2], 
                                 'Rotary 1' : r1, 
                                 'Rotary 2' : r2
                    }
 
    if fm == 'fm_AA':                                                               #mechanical error - erratic
        #introduce a kinematic error and corrupt it with noise
        if checker_cycle == 'ps0':
            error_parameters['dx_C'] = ep_values()
        elif checker_cycle == 'rs_plus_p0':
            error_parameters['dx_B'] = ep_values()
        
        error_map = pd.DataFrame(data=np.zeros((4, len(r1_ang_all))))
        for i in range(len(r1_ang_all)):   
            error_map[i], _ = error_model(r1[i], r2[i], error_parameters, w_offset=[0,0,0]) 
            error_map[i] += noise_mech(size=4).T

        data = {'Error X' : error_map.iloc[0], 
                'Error Y' : error_map.iloc[1], 
                'Error Z' : error_map.iloc[2], 
                'Rotary 1' : r1,    
                'Rotary 2' : r2
                }        

    if fm == 'fm_BB':                                                               #scale/encoder damage
        if checker_cycle == 'rs_plus_p0':
            
            radius_Z = float(noise_mech())
            shift_X = shifts()
            shift_Z = shifts()
            data = {'Error X' : np.linspace(-0.05, 0.05, len(r1_ang_all)) + (noise_nat(size=points) / 3) - shift_X, 
                    'Error Y' : (noise_nat(size=points) / 3), 
                    'Error Z' : np.linspace(-abs(radius_Z), abs(radius_Z), len(r1_ang_all)) + (noise_nat(size=points) / 3) - shift_Z, 
                    'Rotary 1' : r1, 
                    'Rotary 2' : r2
                        }
            
    if fm == 'fm_CC':
        if checker_cycle == 'ps0':
            radius = noise_mech()
            data = {'Error X' : [radius * np.sign(1.99 * np.cos(np.deg2rad(i))) + (noise_nat() / 3) for i in r1_ang_all[:-1]] + [radius], 
                    'Error Y' : [radius * np.sign(1.99 * np.sin(np.deg2rad(i))) + (noise_nat() / 3) for i in r1_ang_all[:-1]] + [0], 
                    'Error Z' : np.zeros(points) + (noise_nat(size=points) / 3), 
                    'Rotary 1' : r1, 
                    'Rotary 2' : r2
                    }
#            data = {'Error X' : np.linspace(-0.05,0.05,len(r1_ang_all)) + noise_nat, 
#                    'Error Y' : noise_nat, 
#                    'Error Z' : np.linspace(float(noise_mech(1)), float(noise_mech(1)), len(r1_ang_all)) + noise_nat, 
#                    'Rotary 1' : r1, 
#                    'Rotary 2' : r2
#                    }
            
    data = pd.DataFrame(data).astype(float).values
    for i in range(13):
        if len(data) < 13: 
            data = np.vstack((data, data[len(data)-1]))
    data = pd.DataFrame(data)
    return data
    
# def error_model(B, C, l_e, w_offset=None, q_w=None):
#     #takes an input tool position q_w in the workpiece CSYS and translates it into the reference (machine G54 pivot point) CSYS
#     #if q_w == None, input position is taken as program zero
    
#     delta_X = float( -(l_e['E_x0b'] * np.cos(B) + l_e['E_z0b'] * np.sin(B) + l_e['E_x(0b)c']) * np.cos(C) + l_e['E_y0c'] * np.sin(C) )
#     delta_Y = float( -(l_e['E_x0b'] * np.cos(B) + l_e['E_z0b'] * np.sin(B) + l_e['E_x(0b)c']) * np.sin(C) + l_e['E_y0c'] * np.cos(C) )
#     delta_Z = float( l_e['E_x0b'] * np.sin(B) - l_e['E_z0b'] * np.cos(B) )
#     delta_A = float( -(l_e['E_a0b'] * np.cos(B) + l_e['E_c0b'] * np.sin(B) + l_e['E_a(0b)c']) * np.cos(C) + l_e['E_b0b'] * np.sin(C) )
#     delta_B = float( -(l_e['E_a0b'] * np.cos(B) + l_e['E_c0b'] * np.sin(B) + l_e['E_a(0b)c']) * np.sin(C) + l_e['E_b0b'] * np.sin(C) )
#     delta_C = float( l_e['E_a0b'] * np.sin(B) - l_e['E_c0b'] * np.cos(B) )
    
#     def Trans_x(x):
#         D_x = np.matrix(([1, 0, 0, x],
#                           [0, 1, 0, 0],
#                           [0, 0, 1, 0],
#                           [0, 0, 0, 1]
#                           )  
#         )
#         return D_x
    
#     def Trans_y(y):
#         D_y = np.matrix(([1, 0, 0, 0],
#                           [0, 1, 0, y],
#                           [0, 0, 1, 0],
#                           [0, 0, 0, 1]
#                           )   
#         )
#         return D_y
    
#     def Trans_z(z):
#         D_z = np.matrix(([1, 0, 0, 0],
#                           [0, 1, 0, 0],
#                           [0, 0, 1, z],
#                           [0, 0, 0, 1]
#                           )   
#         )
#         return D_z
    
#     def Rot_a(a):                                                               #axis directions flipped for TT config, sines with diff signs to literature
#         a = np.deg2rad(a)
#         D_a = np.matrix(([1, 0, 0, 0],
#                           [0, np.cos(a), -np.sin(a), 0],
#                           [0, np.sin(a), np.cos(a), 0],
#                           [0, 0, 0, 1]
#                           )
#         )
#         return D_a
    
#     def Rot_b(b):                                                               
#         b = np.deg2rad(b)
#         D_b = np.matrix(([np.cos(b), 0, np.sin(b), 0],
#                           [0, 1, 0, 0],
#                           [-np.sin(b), 0, np.cos(b), 0],
#                           [0, 0, 0, 1]
#                           )
#         )
#         return D_b
    
#     def Rot_c(c):                                                               
#         c = np.deg2rad(c)
#         D_c = np.matrix(([np.cos(c), -np.sin(c), 0, 0],
#                           [np.sin(c), np.cos(c), 0, 0],
#                           [0, 0, 1, 0],
#                           [0, 0, 0, 1]
#                           )
#         )
#         return D_c
    
#     try:
#         if q_w == None:
#             q_w = [0,0,0]
#     except ValueError:
#         q_w = q_w
                
    
#     o_T_tl = Trans_x(delta_X) * Trans_y(delta_Y) * Trans_z(delta_Z)                               #linear translation in xyz, no tool offset necessary due to G43
# #    print(delta_X, delta_Y, delta_Z)
#     if w_offset == None:
#         o_T_wp = Rot_a(delta_A) * Rot_b(delta_B) * Rot_c(delta_C) #* Rot_b(-B) * Rot_c(-C) 
#     else:
#             o_H_wp = np.matrix(([1, 0, 0, w_offset[0]],
#                   [0, 1, 0, w_offset[1]],
#                   [0, 0, 1, w_offset[2]],
#                   [0, 0, 0, 1]
#                   )) 
#             o_T_wp = Rot_a(delta_A) * Rot_b(delta_B) * Rot_c(delta_C) * o_H_wp #* Rot_b(-B) * Rot_c(-C)                                       #rotary motion in b&c and offset to wp
    
#     w_T_r =  o_T_tl * o_T_wp
#     print('\nto Z\n')
#     print(o_T_tl)
#     print('\nto A \n')
#     print(o_T_tl * Rot_a(delta_A))
#     print('\nto B \n')
#     print(o_T_tl * Rot_a(delta_A) * Rot_b(delta_B))
#     print('\n to C \n')
#     print(w_T_r)
# #    r_T_a = Trans_x(l_e['E_x0b']) * Trans_y(l_e['E_y0c']) * Trans_z(l_e['E_z0b']) * Rot_a(l_e['E_a0b']) * Rot_b(l_e['E_b0b']) * Rot_c(l_e['E_c0b']) * Rot_b(-B)
# #    
# #    a_T_c = Trans_x(l_e['E_x(0b)c']) * Rot_a(l_e['E_a(0b)c']) * Rot_c(-C)
# #    print(r_T_a)
# #    
# #    w_T_r =  a_T_c * r_T_a

#     q_w = np.matrix([q_w[0], q_w[1], q_w[2], 1]).T
#     r_q = np.around((w_T_r.astype(float) * q_w.astype(float)), decimals = 4)

# #    print('\ninput:\n', np.around(q_w, 4))
# #    print('\noutput:\n', np.around(r_q, 4))
#     return r_q
