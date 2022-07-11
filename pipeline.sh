#!/bin/bash

python scrap_ixs.py --id_min 40 --id_max 41 --overwrite
python scrap_arts.py --overwrite
python scrap_users.py --overwrite
