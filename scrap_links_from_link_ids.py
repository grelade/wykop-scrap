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

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--ixs_file',default='',type=str)
    parser.add_argument('--links_file',default='',type=str)
    parser.add_argument('--timeout',default=240,type=int)
    # parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    ixs_file = args.ixs_file
    links_file = args.links_file
    timeout = args.timeout
    # overwrite = args.overwrite

    if links_file == '':
        s = os.path.splitext(ixs_file)
        links_file = f'{s[0]}.link'
    
    print(f'scraping links from {ixs_file}')
    link_ids = np.loadtxt(ixs_file,dtype=int)
    
    links = link_ids_to_data(link_ids,timeout=timeout)

    df = pd.DataFrame(links)

    df['author'] = df['author'].apply(lambda x: x['login'])
    df.to_csv(links_file)
    print(f'scraped dataframe with {df.shape[0]} records and {df.shape[1]} fields')
    print(f'...saving to {links_file}')
    