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

from func import base_wykop,user_wykop,link_wykop,list_wykop,tag_wykop,mikroblog_wykop
from func import link_ids_to_data



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--links_file',default='',type=str)
    parser.add_argument('--start_date',default='2022-07-01',type=str)
    parser.add_argument('--tag',default='neuropa',type=str)
    parser.add_argument('--timeout',default=240,type=int)
    parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    links_file = args.links_file
    start_date = args.start_date
    end_date = date.today().isoformat()
    tag = args.tag
    timeout = args.timeout
    overwrite = args.overwrite

    if links_file == '':
        links_file = f'tag_links/{tag}_{start_date}_{end_date}.csv'
    
    print(f'scraping links in tag {tag}; starting date {start_date}')
    
    tw = tag_wykop(tag,timeout=timeout)
    links = tw.best_link_ids(mode='start_date',start_date=start_date,conv_to_data=True)
 
    df = pd.DataFrame(links)
    df['author'] = df['author'].apply(lambda x: x['login'])
    df.to_csv(links_file)