import os
import sys
import numpy as np
import argparse
from func import file

def diff_link_ids(link_ids,link_ids_diff):
    out = set(link_ids).difference(set(link_ids_diff))
    out = np.sort(list(out))[::-1]
    return out

if __name__ == "__main__":
    
    print(f'\n======= {os.path.basename(__file__)} =======\n')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ixs_file',required=True,type=str)
    parser.add_argument('--ixs_file_diff',required=True,type=str)
    parser.add_argument('--ixs_file_new',default='',type=str)
    parser.add_argument('--overwrite',action="store_true")

    args = parser.parse_args()
    ixs_file = args.ixs_file
    ixs_file_diff = args.ixs_file_diff
    ixs_file_new = args.ixs_file_new
    overwrite = args.overwrite

    if ixs_file_new == '':
        ixs_file_new = ixs_file
    link_ids = file.read_link_ids(ixs_file)
    link_ids_diff = file.read_link_ids(ixs_file_diff)    
    
    print(f'performing {ixs_file} [{len(link_ids)} records] MINUS {ixs_file_diff} [{len(link_ids_diff)} records] subtraction...')

    ixs_file_new_exists = os.path.exists(ixs_file_new)
    if not ixs_file_new_exists or overwrite:

        output = diff_link_ids(link_ids,link_ids_diff)
        
        print(f'... resulting in {len(output)} link_ids.')
        print(f'saving to {ixs_file_new}')

        file.save_link_ids(output,ixs_file_new)
    
    else:
        print(f'file {ixs_file_new} exists, skipping.')
    
    