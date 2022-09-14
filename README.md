# Contents
* [what is it?](#what-is-it)
* [scraping scripts](#scraping-scripts)
* [transform scripts](#transform-scripts)

# what is it?

Scraping programs for <a href="http://wykop.pl">wykop.pl</a> website. Using BeatifulSoup4 and custom-made API.

# scraping programs

Scraping programs are collected under the prefix ```scrap_*.py```. Overall strategy is to gather information around tags. 


- (**```scrap_top_tags.py```**) - scrapes the top tags from <a href="https://www.wykop.pl/tagi">https://www.wykop.pl/tagi</a>.
  
  **Available options**:
  ```
  --tags_file TAGS_FILE   txt file with tags (REQUIRED)
  --timeout TIMEOUT       connection limit timeout
  --overwrite             overwrite existing files
  ```
  **Example usage**:
  ```
  python scrap_top_tags.py --tags_file top_tags.txt
  ```
  which creates a text file top_tags.txt.


- (**```scrap_tags_to_link_ids.py```**) - scrapes link indices for a single tag within time interval. Outputs an .id file. 
  
  **Available options**:
  ```
    --ixs_file IXS_FILE     file with link indices; 
                            if not given, a default format:
                              [MODE]_[TAG]_[START_DATE]_[END_DATE].id is used
    --data_dir DATA_DIR     data directory
    --mode {best,all}       scrape either all or only best (upvoted) link indices
    --start_date START_DATE initial date to start scraping from
                            given in ISO format YYYY-MM-DD (REQUIRED)
    --end_date END_DATE     final date to end scraping at; given in ISO format YYYY-MM-DD;
                            if not given, current date is used
    --tag TAG               tag to scrape (REQUIRED)
    --timeout TIMEOUT       connection limit timeout
    --overwrite             overwrite existing files
  ```
  **Example usage**:
  ```
  python scrap_tags_to_link_ids.py --data_dir datadir 
                                   --start_date 2022-07-01 
                                   --end_date 2022-08-01 
                                   --tag wydarzenia
  ```
  which creates a file with link indices in *datadir/best_wydarzenia_2022-07-01_2022-08-01.id*.
  
  
- (**```scrap_link_ids_to_links.py```**) - scrapes detailed data on links from a link id .id file. Outputs a .link file.
  
  **Available options**:
  ```
  --ixs_file IXS_FILE     file with link indices (REQUIRED)
  --links_file LINKS_FILE file with detailed data on links in a csv format;
                          if not given, default name is the IXS_FILE with .link extension.
  --timeout TIMEOUT       connection limit timeout
  --overwrite             overwrite existing files
  ```
  **Example usage**:
  ```
  python scrap_link_ids_to_links.py --ixs_file datadir/best_wydarzenia_2022-07-01_2022-08-01.id
  ```
  which creates a csv file *datadir/best_wydarzenia_2022-07-01_2022-08-01.link* containing detailed data about the links in the IXS_FILE.
  
  
- (**```scrap_link_ids_to_votes.py```**) - scrapes detailed data on voting on link id in an .id file. Outputs a .vote file.

  **Available options**:
  ```
  --ixs_file IXS_FILE     file with link indices (REQUIRED)
  --votes_file VOTES_FILE file with voting information in a csv format;
                          if not given, default name is the IXS_FILE with .vote extension.
  --timeout TIMEOUT       connection limit timeout
  --overwrite             overwrite existing files 
  ```
  **Example usage**:
  ```
  python scrap_link_ids_to_votes.py --ixs_file datadir/best_wydarzenia_2022-07-01_2022-08-01.id
  ```
  which creates a csv file *datadir/best_wydarzenia_2022-07-01_2022-08-01.vote* containing detailed data about the votes given in links found in IXS_FILE.
  
  
- (**```scrap_links_to_basic_userdata.py```**) - scrapes basic userdata of article authors found in a .link file. Outputs a .user file.

  **Available options**:
  ```
  --links_file LINKS_FILE file with link details (REQUIRED)
  --user_file USER_FILE   file with basic user data in a csv format;
                          if not given, default name is the LINKS_FILE with .user extension.
  --timeout TIMEOUT       connection limit timeout
  --overwrite             overwrite existing files
  ```
  **Example usage**:
  ```
  python scrap_links_to_basic_userdata.py --links_file best_wydarzenia_2022-07-01_2022-08-01.link
  ```
  which creates a csv file *datadir/best_wydarzenia_2022-07-01_2022-08-01.user* containing basic userdata about authors found in links LINKS_FILE.

# transform programs

After the scraping, we provide scripts (collected under the prefix ```transform_*.py```) which either clean or otherwise transform the scraped data into single format, unifies the missing records etc.

- (**```transform_clean_links_link_ids.py```**) - script for cleaning links and link_ids data. Scans the DATA_DIR directory; takes all .link and their corresponding .id files matching the DATA_MODE and cleans them. Afterwards, it saves them in the NEW_DATA_DIR.

  **Available options**:
  ```
  --data_mode {best,all}      which mode (best or all) to clean
  --data_dir DATA_DIR         data directory
  --new_data_dir NEW_DATA_DIR new data directory (cleaned); if not given, uses DATA_DIR
  --manual_mode               use manual mode
  ```

  **Example usage**:
  ```
  python transform_clean_links_link_ids.py --data_mode best
                                           --data_dir datadir
                                           --new_data_dir newdir
  ```
  
- (**```transform_diff_links.py```**) - script for subtracting two link files. Used to divide the best links from the remaining ones.

  **Available options**:
  ```
  --links_file LINKS_FILE        source links file; typically scraped in "all" mode (REQUIRED)
  --links_file_diff LINKS_FILE_D diff links file; typically scraped in "best" mode (REQUIRED)
  --links_file_new LINKS_FILE_N  new link file after subtraction; if empty, use the LINKS_FILE
  --overwrite                    overwrite existing files
  --update_ixs                   update the .id files with matching names
  ```
  
  **Example usage**:
  ```
  python transform_diff_links.py --links_file all_wydarzenia_2022-07-01_2022-08-01.link 
                                 --lins_file_diff best_wydarzenia_2022-07-01_2022-08-01.link
  ```


# example scripts
