import os
import argparse

from func import links_data_cleaner

def map_d2(f,d2):
    '''
    map for two-level dict
    '''
    return {k0: {k: f(v) for k,v in v0.items() } for k0,v0 in d2.items()}



if __name__ == "__main__":
    
    print(f'\n======= {os.path.basename(__file__)} =======\n')
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Script for cleaning links and link_ids data. Scans the DATA_DIR directory; takes all .link and their corresponding .id files matching the DATA_MODE and cleans them. Afterwards, it saves them in the NEW_DATA_DIR.')
    
    # parser.add_argument('--data_class',default='links',type=str)
    parser.add_argument('--data_mode',default='best',type=str,choices=['best','all'],
                        help='which mode (best or all) to clean')
    parser.add_argument('--data_dir',default='data',type=str,
                        help='data directory')
    parser.add_argument('--new_data_dir',default='',type=str,
                        help='new data directory (cleaned); if not given, uses DATA_DIR')
    parser.add_argument('--manual_mode',action="store_true",
                        help='use manual mode')
    # parser.add_argument('--overwrite',action="store_true")
    
    args = parser.parse_args()
    # data_class = args.data_class
    data_class = 'links'
    data_mode = args.data_mode
    data_dir = args.data_dir
    new_data_dir = args.new_data_dir
    manual_mode = args.manual_mode
    # overwrite = args.overwrite
    
    if new_data_dir == '':
        new_data_dir = data_dir
    
    # generate files dict
    files = os.listdir(data_dir)
    files = sorted(files)
    keys = ['best','all']

    dict_files = {'ids':{key: [] for key in keys},
                  'links':{key: [] for key in keys},
                  'votes':{key: [] for key in keys}}

    other_files = []

    for file in files:
        f,e = os.path.splitext(file)
        prefix = f.split('_')[0]

        best_flag = True if 'best' == prefix else False
        all_flag = True if 'all' == prefix else False
        id_flag = True if '.id' == e else False
        link_flag = True if '.link' == e else False
        vote_flag = True if '.vote' == e else False

        if id_flag:
            if best_flag:
                dict_files['ids']['best'] += [file]
            elif all_flag:
                dict_files['ids']['all'] += [file]
            else:
                other_files += [file]

        elif link_flag:
            if best_flag:
                dict_files['links']['best'] += [file]
            elif all_flag:
                dict_files['links']['all'] += [file]
            else:
                other_files += [file]

        elif vote_flag:
            if best_flag:
                dict_files['votes']['best'] += [file]
            elif all_flag:
                dict_files['votes']['all'] += [file]
            else:
                other_files += [file]

        else:
            other_files += [file]
        
    
    
    print(map_d2(len,dict_files))
    # print(dict_files)
    
    stop = True
        
    for f in dict_files[data_class][data_mode]:
        print('#'*20)
        print(f'file = {f}')
        
        ldc = links_data_cleaner(links_file = f,data_path=data_dir)
        ldc.load_links()
        ldc.adjust_columns()
        ldc.clean_nans()
        ldc.clean_author_column()
        ldc.trim_dates()
        
        links_file_path = os.path.join(new_data_dir,f)
        ldc.save_links(links_file=links_file_path,overwrite=True)

        ixs_file = os.path.splitext(links_file_path)[0]+'.id'
        ldc.save_adjusted_link_ids(ixs_file=ixs_file,overwrite=True)

        if manual_mode:
            if stop:
                print('***MANUAL MODE*** type [stop,run, <enter>]:')
                a = input()
            if a == 'stop':
                stop = False
                break
            elif a == 'run':
                stop = False