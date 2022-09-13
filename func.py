from requests import get,post
import time
import json
import pandas as pd
import random
import ast
import os
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime
from tqdm import tqdm
from jinja2 import Template
import plotly


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
        out = data['data']
        # empty output
        if isinstance(out,list) and len(out)==0:
            out = dict(id=self.link_id)
        return out
    
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
        # if 'author' in df.keys():
        #     df['author'] = df['author'].apply(lambda x: x['login'])
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
        print(link_id)
        lw = link_wykop(link_id,timeout=timeout)
        out = lw.upvotes()
        print(len(out))
        if len(out)>0:
            df_up = pd.DataFrame(out)
            
            df_up['author'] = df_up['author'].apply(lambda x: x['login'])
            df_up['link_id'] = link_id
            df_up['vote_type'] = 1
            df_up['reason'] = -1
        else:
            df_up = None
            
        out2 = lw.downvotes()
        print(len(out2))
        if len(out2)>0:
            df_down = pd.DataFrame(out2)

            df_down['author'] = df_down['author'].apply(lambda x: x['login'])
            df_down['link_id'] = link_id
            df_down['vote_type'] = -1
        else:
            df_down = None
            
        if df_down == None and df_up == None:
            delta_df = None
        else:
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
        out3 = [o['href'].split('/')[-2].lower() for o in out2]
        return out3


    
class tag_wykop(base_wykop):
    
    def __init__(self,
                 tag: str,
                 *args,
                 **kwargs):
        
        super(tag_wykop,self).__init__(*args,**kwargs) 
        self.tag = tag.lower()
    
    def link_ids(self,
                 start_date : str,
                 end_date : str = '',
                 mode : str = 'best',
                 scrap_type : str = 'dates',
                 pages : int = 0,
                 conv_to_data : bool = False):
                
        if mode not in ['best','all']:
            raise Error(f'unknown mode={mode}')
        else:
            mode_dict = {'best': 'najlepsze',
                         'all': 'wszystkie'}
            mode_link = mode_dict[mode]

        if scrap_type not in ['pages','dates']:
            raise Error(f'unknown scrap_type={scrap_type}')

        first_id = 1
        link_ids = []
        
        if scrap_type == 'dates':
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
            
        elif scrap_type == 'pages':
            p = 1
        
        # return 0
    
        # stop = False
        while True:
            
            # print(first_id)
            url = f'https://www.wykop.pl/ajax2/tag/znaleziska/{self.tag}/{mode_link}/next/link-{first_id}/'
            response = self._get_decorated_func()(url)
            r = response.text[8:]
            if r == '':
                # no link_ids found
                link_ids = []
                break 
            out = json.loads(r)
            out2 = out['operations'][0]['data']
            html_soup = BeautifulSoup(out2, 'html.parser')
            out3 = html_soup.find_all(class_="media-content m-reset-float")
            out3 = [o.a['href'] for o in out3]
            
            out4 = []
            for o in out3:
                if o != 'https://www.wykop.pl/rejestracja/':
                    out4 += [o]
            
            delta_ids = [int(o.split('/')[-3]) for o in out4]

            if len(delta_ids)==0:
                break
            
            first_id = delta_ids[-1]
            link_ids += delta_ids

            if scrap_type == 'dates':
                curr_date = datetime.fromisoformat(link_wykop(first_id).basic_data()['date'])
                if start_date > curr_date:
                    break
            elif scrap_type == 'pages':
                if p>=pages:
                    break
                p+=1
        
        if scrap_type == 'dates':
            
            mask = [True]*len(link_ids)

            # trim extra link_ids up to start_date
            for i in range(len(mask)-1,-1,-1):
                # print(i)
                link_id = link_ids[i]
                o = link_wykop(link_id).basic_data()
                curr_date = datetime.fromisoformat(o['date'])

                if start_date<=curr_date:
                    break
                else:
                    mask[i] = False

            # trim extra link_ids up to end_date
            for i in range(len(mask)):
                # print(i)
                link_id = link_ids[i]
                o = link_wykop(link_id).basic_data()
                curr_date = datetime.fromisoformat(o['date'])

                if end_date>=curr_date:
                    break
                else:
                    mask[i] = False 

            link_ids = list(np.array(link_ids)[mask])

        #convert to data
        if conv_to_data:
            return link_ids_to_data(link_ids)
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
    
    def load_link_ids(*args,**kwargs):
        return file.read_link_ids(*args,**kwargs)

    def save_link_ids(ixs,ixs_file):
        np.savetxt(ixs_file,ixs,fmt='%d')

    def read_links(links_file):
        return pd.read_csv(links_file,index_col=0)

    def load_links(*args,**kwargs):
        return file.read_links(*args,**kwargs)
    
    def save_links(df,links_file):
        df.to_csv(links_file)

    def read_user(user_file):
        pass

    def load_user(*args,**kwargs):
        return file.read_user(*args,**kwargs)
    
    def save_user(df,user_file):
        df.to_csv(user_file)

    def read_votes(votes_file):
        return pd.read_csv(votes_file,index_col=0)
    
    def load_votes(*args,**kwargs):
        return file.read_votes(*args,**kwargs)
    
    def save_votes(df,votes_file):
        df.to_csv(votes_file)
        
    def read_tags(tags_file):
        return np.loadtxt(tags_file,dtype=str,ndmin=1)
    
    def load_tags(*args,**kwargs):
        return file.read_tags(*args,**kwargs)
    
    def save_tags(tags,tags_file):
        np.savetxt(tags_file,tags,fmt='%s')
        
# aliases
file_handler = file  
fh = file

def fig_to_plotly_js(fig,output_file='output.html'):
    '''
    generate plotly figure in html format read to use on the web
    '''
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    r = random.randint(1,2**20)
    
    template = u"""<div id="plotly-fig-NUMBER"></div><script src="https://cdn.plot.ly/plotly-latest.min.js"></script><script>var graph = {{plot_json}};Plotly.plot('plotly-fig-NUMBER', graph, {});</script>""".replace('NUMBER',str(r))
    data = {"plot_json": plot_json}
    j2_template = Template(template)
    
    out = j2_template.render(data,trim_blocks=True,lstrip_blocks=True)
    
    with open(output_file,'w') as f:
        f.write(out)
        


class links_data_cleaner:
    
    COLUMNS = ['id', 'title', 'description', 'tags', 'source_url', 'vote_count','bury_count', 'comments_count', 'related_count', 'date', 'author','preview', 'plus18', 'status', 'can_vote', 'is_hot', 'app', 'info']
    NULL_VALUES = {'id': -1,
                   'title': '',
                   'description':'',
                   'tags':'',
                   'source_url':'',
                   'vote_count':0,
                   'bury_count':0,
                   'comments_count':0,
                   'related_count':0,
                   'date':'',
                   'author': '',
                   'preview': '',
                   'plus18': '',
                   'status': '',
                   'can_vote': '',
                   'is_hot': '',
                   'app': '',
                   'info': '{}'}
    
    def __init__(self,
                 links_file: str,
                 data_path: str = 'data') -> None:
        
        self.links_file = links_file
        self.data_path = data_path
        self.links_file_path = os.path.join(data_path,links_file)
        
        # self.report = None
        
        if not os.path.exists(self.links_file_path):
            print('warning: link file does not exist!')
        
    def load_links(self) -> None:
        
        self.df = fh.load_links(self.links_file_path)

    def save_links(self,
                   links_file: str = '',
                   overwrite: bool = False) -> None:
        
        f = self.links_file_path if links_file == '' else links_file
        f_exists = os.path.exists(f)
        if not f_exists or overwrite:
            print(f'saving links to {f}')
            fh.save_links(self.df, f)
        else:
            print(f'file {f} exists, skipping.')

    def adjust_columns(self) -> None:
        '''
        ensure .link file has correct columns
        '''
        print('============ running adjust_columns() ============')
        print(f'input df.shape = {self.df.shape}')
        i = 0
        if self.df.shape[1] != len(links_data_cleaner.COLUMNS):
            for col in links_data_cleaner.COLUMNS:
                if col not in self.df.columns:
                    # self.df[col] = links_data_cleaner.NULL_VALUES[col]
                    self.df[col] = np.nan
                    
        print(f'output df.shape = {self.df.shape}')
        
    def clean_nans(self) -> None:
        '''
        fill nan fields with non-nan values
        and
        remove nan records from .link
        '''
        print('============ running clean_nans() ============')
        print(f'input df.shape = {self.df.shape}')
        def clean(col):
            if col in self.df.keys():
                self.df[col] = self.df[col].fillna(links_data_cleaner.NULL_VALUES[col]) 
        
        
        # empty record has only nans and an id
        empty_rec_mask = (self.df.iloc[::,1:].isna().sum(axis=1)==(self.df.shape[1]-1))
        self.df = self.df[~empty_rec_mask]
        
        for col in links_data_cleaner.COLUMNS:
            clean(col)
        
        self.df = self.df.dropna()
        print(f'output df.shape = {self.df.shape}')
        
    def clean_author_column(self) -> None:
        '''
        ensure author column is not a dict
        '''
        print('============ running clean_author_column() ============')
        def conv_dict(s):
            if len(s)==0:
                return s
            else:
                if s[0]=='{' and s[-1]=='}':
                    return ast.literal_eval(s)
                
            return s
            
        # print(f'input df.shape = {self.df.shape}')
        
        newauthor = []
        for author in self.df['author']:
            out = ''
            try:
                out = conv_dict(author)
                if isinstance(out,dict) and 'login' in out.keys():
                    out = out['login']
                    
            except ValueError as err:
                out = author
                print(f'ValueError: {err} for ast.literal_eval({author})')
                
            except SyntaxError as err:
                out = author
                print(f'SyntaxError: {err} for ast.literal_eval({author})')

            finally:
                newauthor += [out]

        self.df['author'] = newauthor
        # print(f'output df.shape = {self.df.shape}')
        
    def trim_dates(self,
                   start_date : str = '',
                   end_date : str = '') -> None:
        '''
        trim record to start and end dates
        '''
        print('============ running trim_dates() ============')
        print(f'input df.shape = {self.df.shape}')
        
        n,e = os.path.splitext(self.links_file)

        # n.split('_') -> ['best', 'f1', '2022-01-01', '2022-07-12']
        _,_,start_date0,end_date0 = n.split('_')

        if start_date != '':
            start_date0 = start_date
        if end_date != '':
            end_date0 = end_date
        
        start_date = datetime.fromisoformat(start_date0)
        end_date = datetime.fromisoformat(end_date0)

        dates = self.df['date'].map(datetime.fromisoformat)
        mask = (dates >= start_date) & (dates <= end_date)

        self.df = self.df[mask]
        print(f'output df.shape = {self.df.shape}')
        
    def get_adjusted_link_ids(self) -> np.array:
        '''
        create .id file adjusted to the .link file
        '''
        
        link_ids_from_df = self.df['id'].to_numpy()
        link_ids_from_df = np.sort(link_ids_from_df)[::-1]
               
        return link_ids_from_df
         
    def save_adjusted_link_ids(self,
                               ixs_file: str = '',
                               overwrite: bool = False):
        
        print('============ running save_adjusted_link_ids() ============')
        n,e = os.path.splitext(self.links_file)
        fid = n+'.id'
        fidpath = os.path.join(self.data_path,fid)
        if os.path.exists(fidpath):
            link_ids = fh.load_link_ids(fidpath) 
            print(f'len(link_ids) = {len(link_ids)}')
        else:
            print(f'base link_ids file is missing!')
        
        link_ids_from_df = self.get_adjusted_link_ids()
        
        print(f'adjusted len(link_ids) = {len(link_ids_from_df)}') 
        
        f = fidpath if ixs_file == '' else ixs_file
        f_exists = os.path.exists(f)
        if not f_exists or overwrite:
            print(f'saving link_ids to {f}')
            fh.save_link_ids(link_ids_from_df, f)
        else:
            print(f'file {f} exists, skipping.')
        