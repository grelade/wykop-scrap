import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import numpy as np
import os

from func import get_decorated

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--ixs_file',default='ixs.txt',type=str)
    parser.add_argument('--id_min',default=40,type=int)
    parser.add_argument('--id_max',default=800,type=int)
    parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    ixs_file = args.ixs_file
    page_id_min = args.id_min
    page_id_max = args.id_max
    overwrite = args.overwrite

    print(f'scraping latest article indexes to : {ixs_file}')
    
    
    ixs = np.array([])

    if os.path.exists(ixs_file) and not overwrite:
        ixs = np.loadtxt(ixs_file,dtype=int)
        print(f'appending to {ixs_file} with {len(ixs)} indexes')

    # if overwrite or os.path.exists(ixs_file):
    #     ixs = []

    # page_id_min = 40
    # page_id_max = 45

    for page_id in tqdm(range(page_id_min,page_id_max)):
        url = f'https://www.wykop.pl/strona/{page_id}'
        news_response = get_decorated(url)
        html_soup2 = BeautifulSoup(news_response.text, 'html.parser')
        outs = html_soup2.find_all(name='h2')

        for out in outs:
            link = out.a['href']

            if 'paylink' in link:
                # print('paylink')
                continue
            else:
                p = urlparse(link).path.split('/')
                if 'link'==p[1]:
                    # print('link')
                    idd = int(p[2])

                    ixs = np.append(ixs,idd)

        if page_id % 10 == 0:
            # print('aaa')
            np.savetxt(ixs_file,ixs,fmt='%d')
      
    np.savetxt(ixs_file,ixs,fmt='%d')

    print(f'saving {len(ixs)} latest articles')