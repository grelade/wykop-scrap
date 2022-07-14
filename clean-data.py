import os
import sys
import numpy as np

files = os.listdir('data')
files = sorted(files)[1:]

files0 = []
for file in files:
    if '.id' in file:
        files0+=[file]
        
files1 = []
for file in files:
    if '.link' in file:
        files1+=[file]
        
l = []
totl0 = []

for i,file in enumerate(files0[:-1]):
    # pass
    a = files0[i]
    l += [a]
    b = files0[i+1]
    a_tag = os.path.splitext(a)[0].split('_')[1]
    b_tag = os.path.splitext(b)[0].split('_')[1]
    if a_tag == b_tag:
        l+=[b]
    else:
        totl0 += [l[-1]]
        l = []
        
l = []
totl1 = []

for i,file in enumerate(files1[:-1]):
    # pass
    a = files1[i]
    l += [a]
    b = files1[i+1]
    a_tag = os.path.splitext(a)[0].split('_')[1]
    b_tag = os.path.splitext(b)[0].split('_')[1]
    if a_tag == b_tag:
        l+=[b]
    else:
        totl1 += [l[-1]]
        l = []
        
files0_rm = sorted(list(set(files0)-set(totl0)))
files1_rm = sorted(list(set(files1)-set(totl1)))

for f in files0_rm:
    os.remove(f'data/{f}')
    
for f in files1_rm:
    os.remove(f'data/{f}')