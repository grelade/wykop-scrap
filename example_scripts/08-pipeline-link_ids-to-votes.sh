#!/bin/bash

DATADIR="data"
# KEY=${1}

FILES="${DATADIR}/*.id"

for f in $FILES; do
  ff=${f%%.*}.vote

  if [[ -f "$ff" ]]; then
    echo "vote file found; skipping"
  else
    python scrap_link_ids_to_votes.py --ixs_file $f
  fi
  
done  
