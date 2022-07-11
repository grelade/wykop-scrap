from requests import get,post
import time
import json


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



from requests import get
import json
import time
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime
from tqdm import tqdm

def get_decorated(url,timeout: int = 240):
    block = True
    while block:
        try:
            response = get(url)
            block = False
        except (ConnectionResetError, ConnectionError, OSError):
            print('sleep')
            time.sleep(timeout)
    return response



class base_wykop:
    
    def __init__(self,
                 # api_key: str,
                 base_url: str = 'https://www.wykop.pl',
                 method: str = 'ajax'):
        self.base_url = base_url
        self.method  = method
    
    @staticmethod
    def ajax_data(url: str):
        response = get_decorated(url)
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
    

def link_ids_to_data(link_ids):
    data = [link_wykop(link_id).basic_data() for link_id in link_ids]
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
        response = get_decorated(url)
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
            response = get_decorated(url)
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
            response = get_decorated(url)
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
