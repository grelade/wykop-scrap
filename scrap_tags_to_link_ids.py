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
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Script for scraping link indices for a single tag within time interval. Outputs an *.id file.')
    
    parser.add_argument('--ixs_file',default='',type=str,
                        help='file with link indices; if not given, a default format [MODE]_[TAG]_[START_DATE]_[END_DATE].id is used')
    parser.add_argument('--data_dir',default='data',type=str,
                        help='data directory')
    parser.add_argument('--mode',default='best',type=str,choices=['best','all'],
                        help='scrape either all or only best (upvoted) link indices')
    parser.add_argument('--start_date',type=str,default='',required=True,
                        help='initial date to start scraping from; given in ISO format YYYY-MM-DD (REQUIRED)')
    parser.add_argument('--end_date',type=str,default='',
                        help='final date to end scraping at; given in ISO format YYYY-MM-DD; if not given, current date is used')
    parser.add_argument('--tag',type=str,default='',required=True,
                        help = 'tag to scrape (REQUIRED)')
    parser.add_argument('--timeout',default=240,type=int,
                        help='connection limit timeout')
    parser.add_argument('--overwrite',action="store_true",
                        help='overwrite existing files')
    
    args = parser.parse_args()
    ixs_file = args.ixs_file
    data_dir = args.data_dir
    mode = args.mode
    start_date = args.start_date
    end_date = args.end_date
    tag = args.tag
    timeout = args.timeout
    overwrite = args.overwrite
    
    if end_date == '':
        end_date = date.today().isoformat()
        
    if ixs_file == '':
        fn = f'{mode}_{tag}_{start_date}_{end_date}.id'
        ixs_file = os.path.join(data_dir,fn)
    
    print(f'scraping {mode} link_ids in tag *{tag}* between {start_date} and {end_date}.')
    
    ixs_file_exists = os.path.exists(ixs_file)
    if not ixs_file_exists or overwrite:
        
        file.save_link_ids([],ixs_file)
        
        tw = tag_wykop(tag,timeout=timeout)
        
        output = tw.link_ids(start_date = start_date,
                             end_date = end_date,
                             mode = mode,
                             scrap_type = 'dates')
        # if mode == 'all':
        #     output = tw.all_link_ids(mode = 'interval',
        #                              start_date = start_date,
        #                              end_date = end_date, 
        #                              conv_to_data = False)
        # elif mode == 'best':
        #     output = tw.best_link_ids(mode = 'interval',
        #                              start_date = start_date,
        #                              end_date = end_date, 
        #                              conv_to_data = False)

        print(f'... found {len(output)} link_ids.')
        print(f'saving to {ixs_file}')

        file.save_link_ids(output,ixs_file)
    
    else:
        print(f'file {ixs_file} exists, skipping.')
    
        