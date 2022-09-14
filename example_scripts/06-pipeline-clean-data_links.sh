#!/bin/bash

DATADIR="data"

python transform_clean_links_link_ids.py --data_mode best --data_dir $DATADIR
python transform_clean_links_link_ids.py --data_mode all --data_dir $DATADIR

