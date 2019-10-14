

#%%
import numpy as np
import pandas as pd
import os
os.chdir(r'c:\\Users\\mep16tjr\\Desktop\\Python\\02 NC Methods\\NC_Methods-git\\Code')
from error_model_nmv8000 import HTM, error_model, generate_training_data
import matplotlib.pyplot as plt
os.chdir(r'c:\\Users\\mep16tjr\\Desktop\\Python\\02 NC Methods')
plt.style.use('ggplot')
%matplotlib qt
matplotlib.rcParams['text.color'] = 'black'

#%%
# initialise

checker_cycle = 'rs_plus_p0'
if checker_cycle == 'rs_plus_p0':
    p = 7
    ss = [0,90]

fm = 'kinematic'


examples = {'B90C0': {}, 'B-90C0': {}, 'B0C360': {}, 'B90C360': {}, 'B-90C360': {}}
#%%

error_parameters = pd.DataFrame(data = np.zeros((1,12)), 
                                columns = ['dx_B', 'dy_B', 'dz_B', 'dx_C', 
                                            'dy_C', 'dz_C', 'ex_B', 'ey_B', 
                                            'ez_B', 'ex_C', 'ey_C', 'ez_C'
                                            ]
                                )

error_parameters['dx_B'] = 0.219
error_parameters['dz_B'] = 0.217

examples['B90C0']['G54'] = generate_training_data(
                        p, ss, fm, error_parameters, checker_cycle
                        )

error_parameters['dx_C'] = 0.009
error_parameters['dy_C'] = 0.193

examples['B90C0']['19700-5'] = generate_training_data(
                        p, ss, fm, error_parameters, checker_cycle
                        )

# print(examples)

#%%

def plot_example(rotary_case, examples, savefig=False):
    plt.close('all')

    alpha = 1
    lw = 1
    fig = plt.figure()
    ax = fig.add_subplot(111)

    colors = ['b', 'r']
    comp_cases = ['G54', '19700-5']

    for i, c in zip(comp_cases, colors):
        X = examples[rotary_case][i][0]
        Y = examples[rotary_case][i][1]
        Z = examples[rotary_case][i][2]
        X -= np.mean(X)
        Y -= np.mean(Y)
        Z -= np.mean(Z)
        
        #find the max and min values in XYZ
        xyz_max = max([max(abs(X)), max(abs(Y)), max(abs(Z))])
        
        #set threshold to 0.1mm unless data is out of range, in which case allow max value + 5% border to preserve shape 
        if xyz_max >= 0.095:                  
            xy_lim = xyz_max * 1.05
        else:
            xy_lim = 0.1
        
        ax.plot(X, Y, color=c, alpha = alpha, label=i, linewidth = lw)         #Y vs X as this is B-axis, X vs Y for A-axis
        ax.scatter(X, Y, color=c, marker='.', label=None, s = 1)
        ax.scatter(X[0], Y[0], color=c, marker='D', label=None, s=10)
        
        ax.plot(Y, Z, color=c, alpha = alpha, label=None, linewidth = lw)
        ax.scatter(Y, Z, color=c, marker='.', label=None, s = 1)
        ax.scatter(Y[0], Z[0], color=c, marker='D', label=None, s=10 )
        
        ax.plot(X, Z, color=c, alpha = alpha, label=None, linewidth = lw)
        ax.scatter(X, Z, color=c, marker='.', label=None, s = 1)
        ax.scatter(X[0], Z[0], color=c, marker='D', label=None, s=10)
        
        plt.axhline(c='black', linewidth=0.2)
        plt.axvline(c='black', linewidth=0.2)
        ax.legend()
        ax.set_xlim(-xy_lim, xy_lim)
        ax.set_ylim(-xy_lim, xy_lim)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xlabel('First axis')
        ax.set_ylabel('Second axis')
        fig.show()
        if savefig == True:
            directory_img = r'Results/Simulation'
            fig.savefig(r'{}\{}_{}'.format(directory_img, rotary_case, comp_case)) 
        print(X, Y, Z, np.mean(X), np.mean(Y))


plot_example('B90C0', examples)

#%%
