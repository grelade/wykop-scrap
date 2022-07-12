#!/bin/bash
STARTDATE="2022-07-07"
ENDDATE=$(date --iso-8601)
FILE="data/best_neuropa_${STARTDATE}_${ENDDATE}.id"
echo $FILE
python scrap_best_link_ids.py --start_date $STARTDATE --tag neuropa --ixs_file $FILE
python scrap_links_from_link_ids.py --ixs_file $FILE