import argparse
from requests import get
import json
import time
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime,date,timedelta
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
import os

from func import base_wykop,user_wykop,link_wykop,list_wykop,tag_wykop,mikroblog_wykop
from func import link_ids_to_data
from func import file

if __name__ == "__main__":
    
    print(f'\n======= {os.path.basename(__file__)} =======\n')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ixs_file',default='',type=str)
    parser.add_argument('--start_date',type=str,required=True)
    parser.add_argument('--tag',type=str,required=True)
    parser.add_argument('--timeout',default=240,type=int)
    parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    ixs_file = args.ixs_file
    start_date = args.start_date
    end_date = date.today().isoformat()
    tag = args.tag
    timeout = args.timeout
    overwrite = args.overwrite

    if ixs_file == '':
        ixs_file = f'data/best_{tag}_{start_date}_{end_date}.id'
    
    print(f'scraping link_ids in tag {tag}; starting date {start_date}...')
    
    ixs_file_exists = os.path.exists(ixs_file)
    if not ixs_file_exists or overwrite:
        
        tw = tag_wykop(tag,timeout=timeout)
        output = tw.best_link_ids(mode='start_date',
                                  start_date=start_date,
                                  conv_to_data=False)

        #trim extra indices
        for i,link_id in enumerate(output[::-1]):
            o = link_wykop(link_id,timeout=timeout).basic_data()
            if datetime.fromisoformat(start_date) <= datetime.fromisoformat(o['date']): 
                break

        output = output[:-i] if i>0 else output
        print(f'... found {len(output)} link_ids.')
        print(f'saving to {ixs_file}')

        file.save_link_ids(output,ixs_file)
    
    else:
        print(f'file {ixs_file} exists, skipping.')
    
        