# Contents
* [what is it?](#what-is-it)
* [scraping scripts](#scraping-scripts)

# what is it?

Scraping scripts for <a href="http://wykop.pl">wykop.pl</a> website. Using BeatifulSoup4.

# scraping scripts

Scraping scripts are collected under the scrap prefix ```scrap_*.py```. Overall strategy is to gather information around tags.

- ```scrap_top_tags.py``` - scrapes the top tags from <a href="https://www.wykop.pl/tagi">https://www.wykop.pl/tagi</a>.

  ```
  --tags_file TAGS_FILE   txt file with tags (REQUIRED)
  --timeout TIMEOUT       connection limit timeout
  --overwrite             overwrite existing files
  ```
  **example usage**:
  ```
  python scrap_top_tags.py --tags_file top_tags.txt
  ```

- ```scrap_link_ids.py``` - scrapes link indices for a single tag within time interval. Outputs an *.id file.

  ```
    --ixs_file IXS_FILE     file with link indices; 
                            if not given, a default format [MODE]_[TAG]_[START_DATE]_[END_DATE].id is used
    --data_dir DATA_DIR     data directory
    --mode {best,all}       scrape either all or only best (upvoted) link indices
    --start_date START_DATE initial date to start scraping from; given in ISO format YYYY-MM-DD (REQUIRED)
    --end_date END_DATE     final date to end scraping at; given in ISO format YYYY-MM-DD;
                            if not given, current date is used
    --tag TAG               tag to scrape (REQUIRED)
    --timeout TIMEOUT       connection limit timeout
    --overwrite             overwrite existing files
  ```
  **example usage**:
  ```
  python scrap_link_ids.py --data_dir datadir --start_date 2022-07-01 --end_date 2022-08-01 --tag wydarzenia
  ```
  which creates a file with link indices in *datadir/best_wydarzenia_2022-07-01_2022-08-01.id*.
  
  - 
