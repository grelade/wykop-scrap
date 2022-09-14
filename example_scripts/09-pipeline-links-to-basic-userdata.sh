#!/bin/bash

DATADIR="datadir"
# KEY=${1}

FILES="${DATADIR}/*.link"

for f in $FILES; do
  ff=${f%%.*}.user

  if [[ -f "$ff" ]]; then
    echo "userdata file found; skipping"
  else
    python scrap_links_to_basic_userdata.py --links_file $f
  fi

done
