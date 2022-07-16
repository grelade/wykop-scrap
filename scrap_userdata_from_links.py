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
from func import link_ids_to_data, link_ids_to_votes, users_to_data
from func import file

if __name__ == "__main__":

    print(f'\n======= {os.path.basename(__file__)} =======\n')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--links_file',type=str,required=True)
    parser.add_argument('--user_file',default='',type=str)
    parser.add_argument('--timeout',default=240,type=int)
    parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    links_file = args.links_file
    user_file = args.user_file
    timeout = args.timeout
    overwrite = args.overwrite

    if user_file == '':
        s = os.path.splitext(links_file)
        user_file = f'{s[0]}.user'
    
    print(f'scraping users from {links_file}')
    links = file.read_links(links_file)

    user_file_exists = os.path.exists(user_file)
    if not user_file_exists or overwrite:
    
        file.save_user(pd.DataFrame([]),user_file)
    
        users = links['author'].unique()

        df = users_to_data(users,
                           timeout=timeout,
                           verbose=True,
                           output_df = True)
        
        file.save_user(df,user_file)

        print(f'scraped dataframe with {df.shape[0]} records and {df.shape[1]} fields')
        print(f'...saving to {user_file}')
        
    else:
        print(f'file {user_file} exists, skipping.')