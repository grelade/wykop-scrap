#!/bin/bash

#SBATCH --job-name=graph-scrap
#SBATCH --qos=quick
#SBATCH --mem=64G
#SBATCH --partition=rtx2080

eval "$(/home/jgrela/miniconda3/bin/conda shell.bash hook)"

export CUDA_VISIBLE_DEVICES=0

conda deactivate
conda activate graph_scrap

cd $HOME/graph_scrap/wykop-scrap

#port=$1
./example_scripts/05-pipeline-link_ids_to_links.sh
#/usr/bin/ssh -N -f -R $port:localhost:$port gw.gmum
#jupyter notebook --no-browser --port $port
#jupyter notebook --ip 0.0.0.0 --port $port
