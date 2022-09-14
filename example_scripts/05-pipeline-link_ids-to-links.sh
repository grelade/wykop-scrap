#!/bin/bash

DATADIR="data"
# KEY=${1}

FILES="${DATADIR}/*.id"

for f in $FILES; do
  ff=${f%%.*}.link

  if [[ -f "$ff" ]]; then
    echo "links file found; skipping"
  else
    python scrap_link_ids_to_links.py --ixs_file $f
  fi
  
done  
