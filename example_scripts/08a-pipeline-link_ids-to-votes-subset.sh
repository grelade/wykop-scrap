#!/bin/bash

DATADIR="data"
# KEY=${1}

# FILES="${DATADIR}/${KEY}_*.id"


FILES="${DATADIR}/*.id"


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
    python scrap_link_ids_to_votes.py --ixs_file $f
  else
    echo "no link_ids file found"
    # FILE="${DATADIR}/${KEY}_${tag}_${STARTDATE}_${ENDDATE}.id"
    # eval $SCRIPT --start_date $STARTDATE --end_date $ENDDATE --tag $tag --ixs_file $FILE --mode $KEY
  fi
  found=false
done < tags_to_votes.txt


