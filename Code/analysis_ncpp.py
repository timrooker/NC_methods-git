#%%
import os
from xml.etree import ElementTree as ET
import pandas as pd
import sys
import numpy as np

#%%
# initialise
program_dict = {620: pd.DataFrame(), 
                621: pd.DataFrame(), 
                622: pd.DataFrame(), 
                623: pd.DataFrame(), 
                624: pd.DataFrame()
                }
data_pp = {'G43' : program_dict, 
            'G43_4' : program_dict, 
            'G54_2' : program_dict, 
            'G68_2' : program_dict
            }
file_path = r'Data/NC_PP-results'

#%%

cases = ['G43', 'G43_4', 'G54_2', 'G68_2']
programs = ['620', '621', '622', '623', '624']

def pull_data(case, program):
    file_extract = r'{}/{}/{}.xml'.format(file_path, case, program)
    tree = ET.parse(file_extract)
    root = tree.getroot()

    root_xyz = root[2]
    rows = root_xyz[-1].find('Key').text[3:-8]

    d = []
    n_positions = int(float(rows)/3)
    for i in range(int(rows)):
        i = i + 1
        for child in root_xyz.findall("./Parameter/[Key='Row{}Value5']".format(i)):
            d.append(float(child.find('Value').text))

    d_xyz = []
    for n in range(n_positions):
        d_xyz.append((d[n*3], d[1 + n*3], d[2 + n*3])) 
    p = pd.DataFrame(d_xyz, columns=list('xyz'))

    return p

for case in cases:
    for program in programs:
        data_pp[case][program] = pull_data(case, program)

#%%

data_pp['G54_2']['622']


#%%
for i in range(int(rows)):
    i = i + 1
    for child in root.findall("./Parameter/[Key='Row{}Value2']".format(i)):
        d.append(float(child.find('Value').text))
#%% PROBED POSITIONS TRANSFER DEFINITION
def xyz_transfer(file):
    global transfer_xyz, transfer_abc
    file_extract = file_path + file + '/Statistics.xml'
    root = ET.parse(file_extract)
    
    #Scan the Information Data node and return the test's timestamp
    timestamp = file
    date = '{}-{}-{}'.format(timestamp[:4], timestamp[4:6], timestamp[6:8])
    time = '{}:{}:{}'.format(timestamp[8:10], timestamp[10:12], timestamp[12:14])
    
    print('File selected: {} {}'.format(date, time))
    
    p_l = pd.DataFrame()                                                        #define DF to store complex report links
    
    x = 0
    for i in root.findall("mspStatsDataElement"):
        element= [i.find(n).text for n in (
                "title",
                "link", 
                )]
        p_l[x] = element
        x = x + 1 
    
    db_tables = ('xyz_ps0',               #0
                 'xyz_ps90',              #1 
                 'xyz_rs_plus_p0',        #2
                 'xyz_rs_neg_p0',         #3
                 'xyz_rs_plus_p90',       #4
                 'xyz_rs_neg_p90',        #5
                 )
    abc_tables = ('abc_ps0',               #0
                 'abc_ps90',              #1 
                 'abc_rs_plus_p0',        #2
                 'abc_rs_neg_p0',         #3\
                 'abc_rs_plus_p90',       #4
                 'abc_rs_neg_p90',        #5
                 )
    
    for t in range(2):
        if t == 0:
            table = abc_tables
        elif t == 1:
            table = db_tables
        p_links = p_l                                                           #reset xml link object to iterate
        for i in range(len(p_l.columns)):
            if p_links[i][0] == 'Rotary Single Primary':
                p_links = p_links.rename(columns={i:table[0]})   
            elif p_links[i][0] == 'Rotary Dual Primary':
                p_links = p_links.rename(columns={i:table[1]})
                                                        
            elif p_links[i][0] == 'Rotary Single Secondary (+)':
                p_links = p_links.rename(columns={i:table[2]})   
            elif p_links[i][0] == 'Rotary Single Secondary (-)':
                p_links = p_links.rename(columns={i:table[3]})  
                        
            elif p_links[i][0] == 'Rotary Dual Secondary (+)':
                p_links = p_links.rename(columns={i:table[4]})        
            elif p_links[i][0] == 'Rotary Dual Secondary (-)':
                p_links = p_links.rename(columns={i:table[5]})   
            else:
                p_links = p_links.drop(columns={i})  
        
        table = p_links.columns
        if t == 0:
            abc_tables = table
        elif t == 1:
            db_tables = table
      
    p_xyz = pd.DataFrame(columns=db_tables)
    p_abc = pd.DataFrame(columns=abc_tables)
    p_positions = pd.DataFrame(columns=db_tables)
    
    for x, y in zip(db_tables, abc_tables):
        file_extract_complex = r'C:/Users/mep16tjr/Desktop/Data/' + db_name + p_links[x][1][5:] 
        file_extract_xml = file_extract_complex[:-5] + '.xml'
        file_extract_txt = file_extract_complex[:-5] + '.msr'        
        tree = ET.parse(file_extract_xml)
        
        root = tree.getroot()
        root_xyz = root[2]                                                              #select measured XYZ position node, CustomReport2
        
        rows = root_xyz[-1].find('Key').text[3:-8]
        n_positions = []
        n_positions.append(int(float(rows)/3))
    
        d_xyz = [timestamp]
        for i in range(int(rows)):
            i = i + 1
            for child in root_xyz.findall("./Parameter/[Key='Row{}Value2']".format(i)):
                d_xyz.append(float(child.find('Value').text))
                
        if len(d_xyz) < 40:
            Nans = 40 - len(d_xyz)
            for i in range(Nans):
                d_xyz.append('NULL')
        p_xyz[x] = d_xyz
        p_positions[x] = n_positions
       
        d_abc = [timestamp]
        
        searchfile = open(file_extract_txt,'r')
        for line in searchfile:
            if 'G801 N1' in line: 
                for i in range(3):
                    i = i+6
                    d_abc.append(line.split()[i][1:])
        #            
        if len(d_abc) < 40:
            Nans = 40 - len(d_abc)
            for i in range(Nans):
                d_abc.append('NULL')
        p_abc[y] = d_abc
        
    p_cols = p_xyz.columns