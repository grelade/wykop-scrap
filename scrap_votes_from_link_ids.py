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
from func import link_ids_to_data, link_ids_to_votes
from func import file

if __name__ == "__main__":

    print(f'\n======= {os.path.basename(__file__)} =======\n')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--ixs_file',type=str, required=True)
    parser.add_argument('--votes_file',default='',type=str)
    parser.add_argument('--timeout',default=240,type=int)
    parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    ixs_file = args.ixs_file
    votes_file = args.votes_file
    timeout = args.timeout
    overwrite = args.overwrite

    if votes_file == '':
        s = os.path.splitext(ixs_file)
        votes_file = f'{s[0]}.vote'
    
    print(f'scraping votes from {ixs_file}')
    link_ids = file.read_link_ids(ixs_file)
    
    votes_file_exists = os.path.exists(votes_file)
    if not votes_file_exists or overwrite:
        
        df = link_ids_to_votes(link_ids,
                               timeout=timeout,
                               verbose=True,
                               output_df = True)
        
        file.save_votes(df,votes_file)
        

        print(f'scraped dataframe with {df.shape[0]} records and {df.shape[1]} fields')
        print(f'...saving to {votes_file}')
    else:
        print(f'file {votes_file} exists, skipping.')
    