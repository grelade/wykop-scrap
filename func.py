from requests import get,post
import time
import json
import pandas as pd

from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime
from tqdm import tqdm

def flag_404(response,html_soup):
    # examples
    # i = 17
    # i = 22
    return response.status_code == 404

def flag_mainpage(response,html_soup):
    # examples
    # i = 6716548
    return html_soup.find('html').title.text == 'Wykop.pl - newsy, aktualności, gry, wiadomości, muzyka, ciekawostki, filmiki'

def flag_archive(response,html_soup):
    # examples
    # i = 44676
    if block := html_soup.find(class_='annotation type-light-success space clearfix'):
        return 'Przeglądasz archiwalną wersję znaleziska.' in block.text
    else:
        return False

def flag_zakopane(response,html_soup):
    # examples
    # i = 6716527
    # i = 6621541
    if block := html_soup.find(class_='annotation type-light-silver space clearfix'):
        return 'Znalezisko zostało zakopane. Głosowanie na treść nie jest już możliwe.' in block.text
    else:
        return False

def flag_duplicate(response,html_soup):
    # examples 
    # i = 5901753
    if block := html_soup.find(class_='annotation type-light-red space clearfix'):
        return 'Duplikat:' in block.text
    else:
        return False
    
def flag_over18(response,html_soup):
    # examples
    # i = 5901773
    # NOT IMPLEMENTED needs selenium...
    return False

def flag_deleted(response,html_soup):
    # examples
    # i = 6617345
    if block := html_soup.find(class_='annotation type-light-red space clearfix'):
        return 'Znalezisko usunięte' in block.text
    else:
        return False

def flag_deleted_author(response,html_soup):
    # examples
    # i = 1718236
    if block := html_soup.find(class_='annotation type-light-red space clearfix'):
        return 'Treść usunięta na prośbę autora znaleziska' in block.text
    else:
        return False

def flag_deleted_regulations(response,html_soup):
    # examples
    # i = 5686723
    if block := html_soup.find(class_='annotation type-light-red space clearfix'):
        return 'Naruszenie regulaminu - brak wiarygodnych źródeł informacji' in block.text
    else:
        return False

def flag_manipulation(response,html_soup):
    # examples
    # i = 6349155
    if block := html_soup.find(class_='annotation type-light-red space clearfix'):
        return 'Manipulacja' in block.text
    else:
        return False
    
def flags(news_response,html_soup):
    f_404 = flag_404(news_response,html_soup)
    f_mainpage = flag_mainpage(news_response,html_soup)
    f_deleted = flag_deleted(news_response,html_soup)
    f_deleted_author = flag_deleted_author(news_response,html_soup)
    f_deleted_regulations = flag_deleted_regulations(news_response,html_soup)
    f_archive = flag_archive(news_response,html_soup)
    f_zakopane = flag_zakopane(news_response,html_soup)
    f_duplicate = flag_duplicate(news_response,html_soup)
    f_manipulation = flag_manipulation(news_response,html_soup)
    f_over18 = flag_over18(news_response,html_soup)
    
    return f_404,f_mainpage,f_deleted,f_deleted_author,f_deleted_regulations,f_archive,f_zakopane,f_duplicate,f_manipulation,f_over18

def flags_code(*flags):
    s = ''
    for flag in flags:
        s+=str(1*flag)
    # s = s[::-1]
    return s

def flags_decode(s):
    # out = out[::-1]
    flags = []
    for ss in s:
        flags += [bool(int(ss))]
    return flags





def get_decorated(url,timeout: int = 240):
    block = True
    while block:
        try:
            response = get(url)
            block = False
        except (ConnectionResetError, ConnectionError, OSError):
            print(f'sleep t={timeout}s')
            time.sleep(timeout)
    return response



class base_wykop:
    
    def __init__(self,
                 # api_key: str,
                 base_url: str = 'https://www.wykop.pl',
                 method: str = 'ajax',
                 timeout: int = 240):
        self.base_url = base_url
        self.method  = method
        self.timeout = timeout
        
    def _get_decorated_func(self):
        return lambda x: get_decorated(x,timeout = self.timeout)
    
    def ajax_data(self,
                  url: str):
        response = self._get_decorated_func()(url)
        return json.loads(response.text[8:])
    
    @staticmethod
    def _batch_data(iter_func):
        data = []
        p = 1
        stop = False
        
        while not stop:
            datum = iter_func(p)
            if len(datum)==0:
                stop = True
            else:
                p += 1
                data += datum
        return data
    
    @staticmethod
    def _batch_data_start_date(iter_func,start_date):
        data = []
        start_date = datetime.fromisoformat(start_date)
        p = 1
        stop = False
        while not stop:
            datum = iter_func(p)
            incorrect_mask = np.array([start_date > datetime.fromisoformat(d['date']) for d in datum])
            if incorrect_mask.any():
                data += list(np.array(datum)[~incorrect_mask])
                stop = True
            else:
                data += datum
                p += 1
                
        return data
    

        
    
class user_wykop(base_wykop):
    
    def __init__(self,
                 user: str,
                 *args,
                 **kwargs):
        
        super(user_wykop,self).__init__(*args,**kwargs)
        self.user = user
        
    def basic_data(self):
        '''
        basic user data
        '''
        url = f'{self.base_url}/ajax2/ludzie/{self.user}'
        data = self.ajax_data(url)
        
        return data['data']

    def links_added(self):
        url_base = f'{self.base_url}/ajax2/ludzie/dodane/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)
    
    def links_published_all(self):
        url_base = f'{self.base_url}/ajax2/ludzie/opublikowane/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)

    def links_published_start_date(self,
                                   start_date: str):
        url_base = f'{self.base_url}/ajax2/ludzie/opublikowane/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data_start_date(iter_func,start_date=start_date)

    def links_comments(self):
        url_base = f'{self.base_url}/ajax2/ludzie/comments/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)

    def links_digged(self):
        url_base = f'{self.base_url}/ajax2/ludzie/digged/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)
    
    def mikroblog_entries(self):
        url_base = f'{self.base_url}/ajax2/ludzie/wpisy/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)    

    def mikroblog_comments(self):
        url_base = f'{self.base_url}/ajax2/ludzie/komentowane-wpisy/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)
    
    def mikroblog_digged(self):
        print('not implemented')
        # url_base = f'{self.base_url}/ajax2/ludzie/komentowane-wpisy/{self.user}/page'
        # iter_func = lambda p: wykop.ajax_data(f'{url_base}/{p}')['data']
        return None
    
    def community_followers(self):
        url_base = f'{self.base_url}/ajax2/ludzie/followers/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)
    
    def community_followed(self):
        url_base = f'{self.base_url}/ajax2/ludzie/followed/{self.user}/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data(iter_func)
    
class link_wykop(base_wykop):
    
    def __init__(self,
                 link_id: int,
                 *args,
                 **kwargs):
        
        super(link_wykop,self).__init__(*args,**kwargs)
        self.link_id = link_id
    
    def basic_data(self):
        url = f'{self.base_url}/ajax2/links/link/{self.link_id}'
        data = self.ajax_data(url)
        return data['data']
    
    def upvotes(self):
        url = f'{self.base_url}/ajax2/link/upvoters/{self.link_id}'
        data = self.ajax_data(url)
        return data['data']
    
    def downvotes(self):
        url = f'{self.base_url}/ajax2/link/downvoters/{self.link_id}'
        data = self.ajax_data(url)
        return data['data']
    
    def comments(self):
        url = f'{self.base_url}/ajax2/link/comments/{self.link_id}'
        data = self.ajax_data(url)
        return data['data']
    

def link_ids_to_data(link_ids: list,
                     timeout: int = 240,
                     verbose: bool = False,
                     output_df: bool = False):
    
    loop = tqdm(link_ids) if verbose else link_ids    
    data = []
    for link_id in loop:
        data += [link_wykop(link_id,timeout=timeout).basic_data()]
    
    if output_df:
        df = pd.DataFrame(data)
        df['author'] = df['author'].apply(lambda x: x['login'])

        return df
    else:
        return data

def link_ids_to_votes(link_ids: list,
                      timeout: int = 240,
                      verbose: bool = False,
                      output_df: bool = False):
    
    loop = tqdm(link_ids) if verbose else link_ids
    
    df = None
    
    for link_id in loop:

        lw = link_wykop(link_id,timeout=timeout)
        out = lw.upvotes()
        if len(out)>0:
            df_up = pd.DataFrame(out)
            
            df_up['author'] = df_up['author'].apply(lambda x: x['login'])
            df_up['link_id'] = link_id
            df_up['vote_type'] = 1
            df_up['reason'] = -1
        else:
            df_up = None
            
        out2 = lw.downvotes()
        if len(out2)>0:
            df_down = pd.DataFrame(out2)

            df_down['author'] = df_down['author'].apply(lambda x: x['login'])
            df_down['link_id'] = link_id
            df_down['vote_type'] = -1
        else:
            df_down = None
            
        delta_df = pd.concat((df_down,df_up),axis=0)
        df = delta_df if df is None else df.append(delta_df,ignore_index=True)
    
    if output_df:
        return df
    else:
        data = df.to_dict(orient='records')
        return data
    
def users_to_data(users: list,
                  timeout: int = 240,
                  verbose: bool = False,
                  output_df: bool = False):

    loop = tqdm(users) if verbose else users
    
    data = []
    for user in loop:
        uw = user_wykop(user,timeout=timeout)
        out = uw.basic_data()
        if out:
            data += [out]
    
    if output_df:
        return pd.DataFrame(data)
    else:
        return data
    
    
    
class list_wykop(base_wykop):
    
    def __init__(self,
                 *args,
                 **kwargs):
        
        super(list_wykop,self).__init__(*args,**kwargs)   
        
    def promoted_links(self,
                 page_min: int,
                 page_max: int):
        url_base = f'{self.base_url}/ajax2/link/promoted/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data_interval(iter_func,page_min,page_max)

    def upcoming_links(self,
                 page_min: int,
                 page_max: int):
        url_base = f'{self.base_url}/ajax2/link/upcoming/page'
        iter_func = lambda p: self.ajax_data(f'{url_base}/{p}')['data']
        return self._batch_data_interval(iter_func,page_min,page_max)
    
    def top_links(self,
            year: int,
            month: int):
        url = f'{self.base_url}/ajax2/links/top/{year}/{month}'
        data = self.ajax_data(url)
        return data['data']
    
    def top_tags(self):
        url = 'https://www.wykop.pl/tagi/'
        response = self._get_decorated_func()(url)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        out = html_soup.find(class_ = 'fix-tagline')
        out2 = out.find_all(class_ = 'tag create')
        out3 = [o['href'].split('/')[-2] for o in out2]
        return out3


    
class tag_wykop(base_wykop):
    
    def __init__(self,
                 tag: str,
                 *args,
                 **kwargs):
        
        super(tag_wykop,self).__init__(*args,**kwargs) 
        self.tag = tag
    
    
    
    def best_link_ids(self,
                      start_date: str,
                      mode: str='start_date', # or pages
                      pages: int = 0,
                      conv_to_data: bool = True):

        first_id = 1
        link_ids = []
        
        if mode == 'start_date':
            start_date = datetime.fromisoformat(start_date)
        elif mode == 'pages':
            p = 0
        
        stop = False
        while not stop:
            
            # print(first_id)
            url = f'https://www.wykop.pl/ajax2/tag/znaleziska/{self.tag}/najlepsze/next/link-{first_id}/'
            response = self._get_decorated_func()(url)
            out = json.loads(response.text[8:])
            out2 = out['operations'][0]['data']
            html_soup = BeautifulSoup(out2, 'html.parser')
            out3 = html_soup.find_all(class_="media-content m-reset-float")
            out3 = [o.a['href'] for o in out3]
            
            out4 = []
            for o in out3:
                if o != 'https://www.wykop.pl/rejestracja/':
                    out4 += [o]
            
            delta_ids = [int(o.split('/')[-3]) for o in out4]
            
            first_id = delta_ids[-1]
            link_ids += delta_ids
            
            
            if mode == 'start_date':
                curr_date = datetime.fromisoformat(link_wykop(first_id).basic_data()['date'])
                if start_date > curr_date:
                    break
            elif mode == 'pages':
                if p<=pages:
                    break
                p+=1
            
        if conv_to_data:
            out = link_ids_to_data(link_ids)
            out2 = []
            
            for o in out:
                if start_date <= datetime.fromisoformat(o['date']): 
                    out2 += [o]
                # else:
                #     break
            
            return out2
        else:
            return link_ids
    
    def recent_link_ids(self,
                        pages: int,
                        conv_to_data: bool = True):

        first_id = 1
        link_ids = []
        for p in range(pages):
            # print(first_id)
            url = f'https://www.wykop.pl/ajax2/tag/znaleziska/{self.tag}/wszystkie/next/link-{first_id}/'
            response = self._get_decorated_func()(url)
            out = json.loads(response.text[8:])
            out2 = out['operations'][0]['data']
            html_soup = BeautifulSoup(out2, 'html.parser')
            out3 = html_soup.find_all(class_="media-content m-reset-float")
            delta_ids = [int(o.a['href'].split('/')[-3]) for o in out3]
            
            first_id = delta_ids[-1]
            
            link_ids+=delta_ids 
        
        if conv_to_data:
            return 
        else:
            return link_ids
    
    def best_entry_ids(self,
                       pages: int):
        print('not implemented')
        return None
    
    def recent_entry_ids(self,
                         pages: int):
        print('not implemented')
        return None    
    
    
    
class mikroblog_wykop(base_wykop):
    
    def __init__(self,
                 *args,
                 **kwargs):
        
        super(mikroblog_wykop,self).__init__(*args,**kwargs)

        

class file:
        
    def read_link_ids(ixs_file):
        return np.loadtxt(ixs_file,dtype=int,ndmin=1)

    def save_link_ids(ixs,ixs_file):
        np.savetxt(ixs_file,ixs,fmt='%d')

    def read_links(links_file):
        return pd.read_csv(links_file,index_col=0)

    def save_links(df,links_file):
        df.to_csv(links_file)

    def read_user(user_file):
        pass

    def save_user(df,user_file):
        df.to_csv(user_file)

    def read_votes(vote_file):
        pass

    def save_votes(df,votes_file):
        df.to_csv(votes_file)