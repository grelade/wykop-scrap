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

if __name__ == "__main__":

    print(f'\n======= {os.path.basename(__file__)} =======\n')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--links_file',default='',type=str)
    parser.add_argument('--user_file',default='',type=str)
    parser.add_argument('--timeout',default=240,type=int)
    # parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    links_file = args.links_file
    user_file = args.user_file
    timeout = args.timeout
    # overwrite = args.overwrite

    if user_file == '':
        s = os.path.splitext(links_file)
        user_file = f'{s[0]}.user'
    
    print(f'scraping users from {links_file}')
    links = pd.read_csv(links_file,index_col=0)
    # link_ids = np.loadtxt(ixs_file,dtype=int)
    
    users = links['author'].unique()
    
    df = users_to_data(users,
                       timeout=timeout,
                       verbose=True,
                       output_df = True)
    df.to_csv(user_file)

    print(f'scraped dataframe with {df.shape[0]} records and {df.shape[1]} fields')
    print(f'...saving to {user_file}')
    