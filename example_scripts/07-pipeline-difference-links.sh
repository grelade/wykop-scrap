#!/bin/bash

DATADIR="data"
TAGSFILE=${1}

while read tag; do

  FILES="${DATADIR}/*_${tag}_*.link"
  IXS_FILE=""
  IXS_FILE_DIFF=""
  
  FLAG_IXS=false
  FLAG_IXS_DIFF=false
  
  for f in $FILES; do
  # ff=${f%%.*}.link
    # echo $f
    
    if [[ "$f" == *"/all_"* ]] && [ "$FLAG_IXS" = false ]; then
      IXS_FILE=${f}
      # FLAG_IXS=true
    fi
    
    if [[ "$f" == *"/best_"* ]] && [ "$FLAG_IXS_DIFF" = false ]; then
      IXS_FILE_DIFF=${f}
      # FLAG_IXS_DIFF=true
    fi
          
  done
  # echo "==============="
  # echo "ixs_file = ${IXS_FILE}" 
  # echo "ixs_file_diff = ${IXS_FILE_DIFF}" 
  # break
  if [ "$IXS_FILE" != "" ] && [ "$IXS_FILE_DIFF" != "" ]; then
    python transform_diff_links.py --links_file $IXS_FILE --links_file_diff $IXS_FILE_DIFF --overwrite --update_ixs
  fi
done < $TAGSFILE
