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

def error_model(B, C, l_e, w_offset=None, q_w=None):
    #takes an input tool position q_w in the workpiece CSYS and translates it into the reference (machine G54 pivot point) CSYS
    #if q_w == None, input position is taken as program zero
    
    delta_X = float( -(l_e['E_x0b'] * np.cos(B) + l_e['E_z0b'] * np.sin(B) + l_e['E_x(0b)c']) * np.cos(C) + l_e['E_y0c'] * np.sin(C) )
    delta_Y = float( -(l_e['E_x0b'] * np.cos(B) + l_e['E_z0b'] * np.sin(B) + l_e['E_x(0b)c']) * np.sin(C) + l_e['E_y0c'] * np.cos(C) )
    delta_Z = float( l_e['E_x0b'] * np.sin(B) - l_e['E_z0b'] * np.cos(B) )
    delta_A = float( -(l_e['E_a0b'] * np.cos(B) + l_e['E_c0b'] * np.sin(B) + l_e['E_a(0b)c']) * np.cos(C) + l_e['E_b0b'] * np.sin(C) )
    delta_B = float( -(l_e['E_a0b'] * np.cos(B) + l_e['E_c0b'] * np.sin(B) + l_e['E_a(0b)c']) * np.sin(C) + l_e['E_b0b'] * np.sin(C) )
    delta_C = float( l_e['E_a0b'] * np.sin(B) - l_e['E_c0b'] * np.cos(B) )
    
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
    
    def Rot_a(a):                                                               #axis directions flipped for TT config, sines with diff signs to literature
        a = np.deg2rad(a)
        D_a = np.matrix(([1, 0, 0, 0],
                          [0, np.cos(a), -np.sin(a), 0],
                          [0, np.sin(a), np.cos(a), 0],
                          [0, 0, 0, 1]
                          )
        )
        return D_a
    
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
    
    try:
        if q_w == None:
            q_w = [0,0,0]
    except ValueError:
        q_w = q_w
                
    
    o_T_tl = Trans_x(delta_X) * Trans_y(delta_Y) * Trans_z(delta_Z)                               #linear translation in xyz, no tool offset necessary due to G43
#    print(delta_X, delta_Y, delta_Z)
    if w_offset == None:
        o_T_wp = Rot_a(delta_A) * Rot_b(delta_B) * Rot_c(delta_C) #* Rot_b(-B) * Rot_c(-C) 
    else:
            o_H_wp = np.matrix(([1, 0, 0, w_offset[0]],
                  [0, 1, 0, w_offset[1]],
                  [0, 0, 1, w_offset[2]],
                  [0, 0, 0, 1]
                  )) 
            o_T_wp = Rot_a(delta_A) * Rot_b(delta_B) * Rot_c(delta_C) * o_H_wp #* Rot_b(-B) * Rot_c(-C)                                       #rotary motion in b&c and offset to wp
    
    w_T_r =  o_T_tl * o_T_wp
    print('\nto Z\n')
    print(o_T_tl)
    print('\nto A \n')
    print(o_T_tl * Rot_a(delta_A))
    print('\nto B \n')
    print(o_T_tl * Rot_a(delta_A) * Rot_b(delta_B))
    print('\n to C \n')
    print(w_T_r)
#    r_T_a = Trans_x(l_e['E_x0b']) * Trans_y(l_e['E_y0c']) * Trans_z(l_e['E_z0b']) * Rot_a(l_e['E_a0b']) * Rot_b(l_e['E_b0b']) * Rot_c(l_e['E_c0b']) * Rot_b(-B)
#    
#    a_T_c = Trans_x(l_e['E_x(0b)c']) * Rot_a(l_e['E_a(0b)c']) * Rot_c(-C)
#    print(r_T_a)
#    
#    w_T_r =  a_T_c * r_T_a

    q_w = np.matrix([q_w[0], q_w[1], q_w[2], 1]).T
    r_q = np.around((w_T_r.astype(float) * q_w.astype(float)), decimals = 4)

#    print('\ninput:\n', np.around(q_w, 4))
#    print('\noutput:\n', np.around(r_q, 4))
    return r_q
