import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import json
import os
import pytz
from datetime import datetime,timezone,timedelta

from func import get_decorated, flags, flags_code, flags_decode



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--ixs_file',default='ixs.txt',type=str)
    parser.add_argument('--news_file',default='news.csv',type=str)
    parser.add_argument('--upvotes_file',default='upvotes.csv',type=str)
    parser.add_argument('--downvotes_file',default='downvotes.csv',type=str)
    parser.add_argument('--overwrite',action="store_true")

    args = parser.parse_args()
    ixs_file = args.ixs_file
    news_file = args.news_file
    upvotes_file = args.upvotes_file
    downvotes_file = args.downvotes_file
    overwrite = args.overwrite

        
    ixs = np.loadtxt(ixs_file,dtype=int)

    news = pd.DataFrame(columns=['art_id','title','desc','author','outlet','pub_date','scrap_date','n_comments','n_upvotes','n_downvotes','flags'])
    downvotes = pd.DataFrame(columns=['art_id','user','date'])
    upvotes = pd.DataFrame(columns=['art_id','user','date'])
    
    if os.path.exists(news_file) and not overwrite:
        news = pd.read_csv(news_file,index_col=0)
        
    if os.path.exists(upvotes_file) and not overwrite:
        upvotes = pd.read_csv(upvotes_file,index_col=0)
        
    if os.path.exists(downvotes_file) and not overwrite:
        downvotes = pd.read_csv(downvotes_file,index_col=0)
        
    def save_csvs():
        news.to_csv(news_file)
        upvotes.to_csv(upvotes_file)
        downvotes.to_csv(downvotes_file)
        
    for i in tqdm(ixs):

        if (news['art_id']==i).any():
            print('art_id exists in db; skipping')
            continue

        if len(news) % 100 == 0:
            print('saving to csv')
            save_csvs()

        url = f'https://www.wykop.pl/link/{i}'
        news_response = get_decorated(url)
        url_downvotes = f'https://www.wykop.pl/ajax2/links/downvoters/{i}/'
        downvotes_response = get_decorated(url_downvotes)
        url_upvotes = f'https://www.wykop.pl/ajax2/links/upvoters/{i}/'
        upvotes_response = get_decorated(url_upvotes)    

        html_soup = BeautifulSoup(news_response.text, 'html.parser')

        fgs = flags(news_response,html_soup)
        fgs_coded = flags_code(*fgs)
        f_404,f_mainpage,f_deleted,f_deleted_author,f_deleted_regulations,f_archive,f_zakopane,f_duplicate,f_manipulation,f_over18 = fgs

        if f_404 or f_mainpage or f_deleted or f_deleted_author or f_deleted_regulations:
            print('delete')
            news = news.append({'art_id': i,
                 'title': '',
                 'desc': '',
                 'author': '',
                 'outlet': '',
                 'pub_date': '',
                 'scrap_date': '',
                 'n_comments': 0,
                 'n_upvotes': 0,
                 'n_downvotes': 0,
                 'flags': fgs_coded },ignore_index=True)

            continue

        #title = html_soup.find(class_='data-wyr').text
        title = html_soup.find(class_='lcontrast m-reset-float m-reset-margin').h2.span.text
        desc = html_soup.find(class_='lcontrast m-reset-float m-reset-margin').p.text
        author = html_soup.find(class_='fix-tagline').a.text[1:]
        outlet = html_soup.find('span',class_='affect').text
        pub_date = html_soup.find_all('time')[0]['datetime']

        d_aware = pytz.timezone('Europe/Warsaw').localize(datetime.now())
        scrap_date = d_aware.isoformat(timespec='seconds')

        #n_comments = int(html_soup.find_all(class_='info m-reset-float')[1].em.text)
        n_comments = int(html_soup.find(class_='nav fix-b-border').p.em.text)



        datum = json.loads(downvotes_response.text[8:])
        out = datum['operations'][-1]['html']
        v = BeautifulSoup(out, 'html.parser')
        voters = v.find_all('a')
        n_downvotes = len(voters)
        for g in voters:
            user = g.b.text
            d = g.time['datetime']
            downvotes = downvotes.append({'art_id':int(i),
                                          'user':user,
                                          'date':d},ignore_index=True)



        datum = json.loads(upvotes_response.text[8:])
        out = datum['operations'][-1]['html']
        v = BeautifulSoup(out, 'html.parser')
        voters = v.find_all('a')
        n_upvotes = len(voters)
        for g in voters:
            user = g.b.text
            d = g.time['datetime']
            upvotes = upvotes.append({'art_id':int(i),
                                      'user':user,
                                      'date':d},ignore_index=True) 



        news = news.append({'art_id': i,
                 'title': title,
                 'desc': desc,
                 'author': author,
                 'outlet': outlet,
                 'pub_date': pub_date,
                 'scrap_date': scrap_date,
                 'n_comments': n_comments,
                 'n_upvotes': n_upvotes,
                 'n_downvotes': n_downvotes,
                 'flags': fgs_coded},ignore_index=True)
        
        
    save_csvs()