# Contents
* [what is it?](#what-is-it)
* [scraping programs](#scraping-programs)
* [transform programs](#transform-programs)
* [example automation scripts](#example-automation-scripts)

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


# example automation scripts

We provide automation scripts *##-pipeline.sh* in *example_scripts* directory. They roughly form a pipeline ordered by the prefixes. We describe the steps below. Working directory is *data*. All scripts have SLURM variants *##-gmum-sbatch.sh*.

* **Find top tags**. Top tags are extracted using the scrap_top_tags.py and saved to *top_tags.txt*.

  **input**: none
  
  **output**: *top_tags.txt*
  
  ```
  python scrap_top_tags.py --tags_file top_tags.txt
  ```
* **Find lists of link ids**. In this stage we go through all of the tags in the top_tags.txt (TAGSFILE) file and,
for each, compose an *.id file containing a list of link_ids within the hardcoded date boundaries [STARTDATE, ENDDATE]. Store it in *data* (DATADIR) directory.

  **input**: *top_tags.txt*
  
  **output**: *data/best_\*.id* and *data/all_\*.id*
  
  ```
	./example_scripts/04a-pipeline-tags-to-link_ids-best.sh top_tags.txt
	./example_scripts/04b-pipeline-tags-to-link_ids-all.sh top_tags.txt
  ```

* **Gather links from link_id lists**. For each .id file create an .link file with scraped data about particular link. Store everything in *data* (DATADIR) directory.
Since it is the labourious process, it has a safety feature which does not pursue the .id file if there is already an associated .link file.

  **input**: *data/\*.id*
  
  **output**: *data/\*.link*
  

  ```
	./example_scripts/05-pipeline-link_ids-to-links.sh 
  ```


* **Cleaning link files**. As an additional step we clean the link files which may contain nans and empty records. Furthermore, it ensures that both id and link files are in accordance and match the set time interval. By default these run on all files in the *data* (DATADIR) directory. They are quite fast so gmum script is not included.

  **input**: *data/\*.id* and *data/\*.link* and *data/\*.vote*
  
  **output**: *data/\*.id* and *data/\*.link* and *data/\*.vote*

  ```
	./example_scripts/06-pipeline-clean-data_links.sh
  ```

* **Discard best/all duplicate links**. Loop over *top_tags.txt* (TAGSFILE). Discard the best links from *data/best_\*.link* from all links stored in *data/all_\*.link*. As is, the *all_\*.link* file contains literally all links and so the best links are also included. On top of updating all links, the corresponding *.id* files are modified.

  **input**: *top_tags.txt*, *data/\*.id* and *data/\*.link*
  
  **output**: *data/\*.id* and *data/\*.link*
  
  ```
  ./example_scripts/07-pipeline-difference-links.sh top_tags.txt
  ```

* **Gather votes for a subset of tags**. Loop over *tags_to_votes.txt* (TAGSFILE) and collect voting structure for each *.id* file in *data* (DATADIR) directory. Store everything in a *.vote* file.

  **input**: *tags_to_votes.txt*, *data/\*.id*
  
  **output**: *data/\*.vote*

  ```
  ./example_scripts/08a-pipeline-link_ids-to-votes-subset.sh tags_to_votes.txt
  ```

* **Gather basic userdata for authors in a subset of tags**. Loop over *tags_to_users.txt* (TAGSFILE), collect basic user data of the authors found in each *data/\*.link* file. Store everything in *data* (DATADIR) directory in a corresponding *.user* file. 

  **input**: *tags_to_users.txt*, *data/\*.link*
  
  **output**: *data/\*.user*

  ```
  ./example_scripts/09a-pipeline-links-to-basic-userdata-subset.sh tags_to_users.txt
  ```
