import os
import sys
import numpy as np
import argparse

from func import file
from func import links_data_cleaner

def diff_links(links,links_diff):
    ixd = set(links['id']).difference(set(links_diff['id']))
    df = links.set_index('id').loc[ixd].reset_index().sort_values(by='id',ascending=False).reset_index()
    del df['index']
    return df

if __name__ == "__main__":
    
    print(f'\n======= {os.path.basename(__file__)} =======\n')
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Script for ')
    
    parser.add_argument('--links_file',required=True,default='',type=str)
    parser.add_argument('--links_file_diff',required=True,default='',type=str)
    parser.add_argument('--links_file_new',default='',type=str)    
    parser.add_argument('--overwrite',action="store_true")
    parser.add_argument('--update_ixs',action="store_true")

    args = parser.parse_args()
    links_file = args.links_file
    links_file_diff = args.links_file_diff
    links_file_new = args.links_file_new
    overwrite = args.overwrite
    update_ixs = args.update_ixs

    if links_file_new == '':
        links_file_new = links_file
    links = file.read_links(links_file)
    links_diff = file.read_links(links_file_diff)    
    
    print(f'performing {links_file} [{len(links)} records] MINUS {links_file_diff} [{len(links_diff)} records] subtraction...')

    links_file_new_exists = os.path.exists(links_file_new)
    if not links_file_new_exists or overwrite:

        output = diff_links(links,links_diff)
        
        # print(output)
        
        print(f'... resulting in {len(output)} links.')
        print(f'saving to {links_file_new}')

        file.save_links(output,links_file_new)
        
        if update_ixs:
            n,e = os.path.splitext(links_file_new)
            f = n+'.id'

            link_ids_from_df = output['id'].to_numpy()
            link_ids_from_df = np.sort(link_ids_from_df)[::-1]
            file.save_link_ids(link_ids_from_df, f)
        
    else:
        print(f'file {links_file_new} exists, skipping.')
    
    