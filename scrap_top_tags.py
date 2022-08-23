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
                                     description='Script for scraping the top tags from https://www.wykop.pl/tagi')
    
    parser.add_argument('--tags_file',type=str,default='',required=True,
                        help='txt file with tags (REQUIRED)')
    parser.add_argument('--timeout',default=240,type=int,
                        help='connection limit timeout')
    parser.add_argument('--overwrite',action="store_true",
                        help='overwrite existing files')
    
    args = parser.parse_args()
    tags_file = args.tags_file
    timeout = args.timeout
    overwrite = args.overwrite
    
    print(f'scraping top tags...')
    
    tags_file_exists = os.path.exists(tags_file)
    if not tags_file_exists or overwrite:
        
        file.save_tags([],tags_file)
        
        w = list_wykop(timeout=timeout)
        tags = w.top_tags()
        
        print(f'... found {len(tags)} tags.')
        print(f'saving to {tags_file}')
        
        file.save_tags(tags,tags_file)
    
    else:
        print(f'file {tags_file} exists, skipping.')
    
        