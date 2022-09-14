#!/bin/bash

DATADIR=${1}
TAGSFILE=${2}
KEY=${3}
# cd data

STARTDATE=${4}
ENDDATE=${5}
    
FILES="${DATADIR}/${KEY}_*.id"
# SCRIPT="python scrap_${KEY}_link_ids.py"
SCRIPT="python scrap_tags_to_link_ids.py"

found=false
while read tag; do
  echo $tag
  # ./02-pipeline.sh $p
  for f in $FILES; do
    # echo "$f"
    if [[ "$f" == *_"$tag"_* ]]; then
      found=true
    fi

  done
  # break
  
  if [ "$found" = true ]; then
    echo "link_ids file found; skipping"
  else
    # echo "##### computation"
    FILE="${DATADIR}/${KEY}_${tag}_${STARTDATE}_${ENDDATE}.id"
    eval $SCRIPT --start_date $STARTDATE --end_date $ENDDATE --tag $tag --ixs_file $FILE --mode $KEY
  fi
  found=false
done < $TAGSFILE
