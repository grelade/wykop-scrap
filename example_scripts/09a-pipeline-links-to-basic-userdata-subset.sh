#!/bin/bash

DATADIR="data"
TAGSFILE=$1
# KEY=${1}

# FILES="${DATADIR}/${KEY}_*.id"


FILES="${DATADIR}/*.link"


found=false
while read tag; do
  echo $tag
  # ./02-pipeline.sh $p
  for f in $FILES; do
    # echo "$f"
    if [[ "$f" == *_"$tag"_* ]]; then
      found=true
      break
    fi

  done
  # break
  
  if [ "$found" = true ]; then
    echo $f
    python scrap_links_to_basic_userdata.py --links_file $f
  else
    echo "no links file found"
    # FILE="${DATADIR}/${KEY}_${tag}_${STARTDATE}_${ENDDATE}.id"
    # eval $SCRIPT --start_date $STARTDATE --end_date $ENDDATE --tag $tag --ixs_file $FILE --mode $KEY
  fi
  found=false
done < $TAGSFILE


