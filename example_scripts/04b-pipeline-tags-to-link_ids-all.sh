#!/bin/bash


TAGSFILE=${1}

DATADIR="data"
STARTDATE="2022-07-01"
ENDDATE="2022-08-01"
# ENDDATE=$(date --iso-8601)

#find absolute path to script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $SCRIPT_DIR/04-pipeline-tags-to-link_ids.sh $DATADIR $TAGSFILE all $STARTDATE $ENDDATE