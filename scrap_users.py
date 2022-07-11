import argparse
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
import json
import os
import pytz
from datetime import datetime,timezone,timedelta
import time
from func import get_decorated,flag_404


def enlarge_follows(user,follows):
    
    l=1
    i=1
    users = []
    while l>0:
        # print(i)
        url = f'https://www.wykop.pl/ajax2/ludzie/followers/{user}/page/{i}'
        response = get_decorated(url)
        out = json.loads(response.text[8:]) 
        l = len(out['data'])
        # print(l)
        for rec in out['data']:
            users+= [rec['login']]
        break
        i+=1
        
    out = [{'follower':o, 'following': user} for o in users]

    for d in out:
        follows = follows.append(d,ignore_index=True)
        
    l=1
    i=1
    users = []
    while l>0:
        # print(i)
        url = f'https://www.wykop.pl/ajax2/ludzie/follows/{user}/page/{i}'
        response = get_decorated(url)
        out = json.loads(response.text[8:]) 
        l = len(out['data'])
        # print(l)
        for rec in out['data']:
            users+= [rec['login']]
        break
        i+=1
        
    out = [{'follower':user, 'following': o} for o in users]

    for d in out:
        follows = follows.append(d,ignore_index=True)
    
    return follows.drop_duplicates()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--news_file',default='news.csv',type=str)
    parser.add_argument('--users_file',default='users.csv',type=str)
    parser.add_argument('--follows_file',default='follows.csv',type=str)
    parser.add_argument('--overwrite',action="store_true")

    args = parser.parse_args()
    news_file = args.news_file
    users_file = args.users_file
    follows_file = args.follows_file
    overwrite = args.overwrite
    
    
    news = pd.read_csv(news_file,index_col=0)
    users_list = news['author'].unique()

    
    users = pd.DataFrame(columns=['user','joined_date','scrap_date',
                                  'links_added_count','links_published_count',
                                  'comments_count','followers','following',
                                  'entries','entries_comments','diggs'])
    follows = pd.DataFrame(columns=['follower','following'])
    
    if os.path.exists(users_file) and not overwrite:
        users = pd.read_csv(users_file,index_col=0)
        
    if os.path.exists(follows_file) and not overwrite:
        follows = pd.read_csv(follows_file,index_col=0)        
    
    def save_csvs():
        users.to_csv(users_file)
        follows.to_csv(follows_file)        

    pairs = list(zip(range(len(users_list)),users_list))
    for p in tqdm(pairs):
        ii,user = p
        url = f'https://www.wykop.pl/ajax2/ludzie/{user}'

        user_response = get_decorated(url)
        datum = json.loads(user_response.text[8:])
        d = datum['data']
        
        if 'error' in datum.keys():
            print(f'{user} does not exist?')
            continue       
        
        rec = d

        rec['user'] = d['login']
        rec['joined_date'] = d['signup_at']
        d_aware = pytz.timezone('Europe/Warsaw').localize(datetime.now())
        rec['scrap_date'] = d_aware.isoformat(timespec='seconds')

        rec = {k: rec[k] for k in users.columns}

        users = users.append(rec,ignore_index=True)       

        follows = enlarge_follows(user,follows)     

        if ii % 10 == 0:
            save_csvs()
            
    save_csvs()
        
