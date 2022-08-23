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
                                     description='Script for scraping detailed data on links from a link id .id file. Outputs a .link file.')
    
    parser.add_argument('--ixs_file',type=str,default='',required=True,
                        help='file with link indices (REQUIRED)')
    parser.add_argument('--links_file',default='',type=str,
                        help='file with detailed data on links in a csv format; if not given, default name is the IXS_FILE with .link extension.')
    parser.add_argument('--timeout',default=240,type=int,
                        help='connection limit timeout')
    parser.add_argument('--overwrite',action="store_true",
                        help='overwrite existing files')
    
    args = parser.parse_args()
    ixs_file = args.ixs_file
    links_file = args.links_file
    timeout = args.timeout
    overwrite = args.overwrite

    if links_file == '':
        s = os.path.splitext(ixs_file)
        links_file = f'{s[0]}.link'
    
    print(f'scraping links from {ixs_file}')
    link_ids = file.read_link_ids(ixs_file)

    links_file_exists = os.path.exists(links_file)
    if not links_file_exists or overwrite:
    
        file.save_links(pd.DataFrame([]),links_file)
        
        df = link_ids_to_data(link_ids,
                              timeout=timeout,
                              verbose=True,
                              output_df=True)

        file.save_links(df,links_file)
        
        print(f'scraped dataframe with {df.shape[0]} records and {df.shape[1]} fields')
        print(f'...saving to {links_file}')
    else:
        print(f'file {links_file} exists, skipping.')
    