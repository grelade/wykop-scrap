#!/bin/bash

#SBATCH --job-name=graph-scrap
#SBATCH --qos=quick
#SBATCH --mem=64G
#SBATCH --partition=cpu

eval "$(/home/jgrela/miniconda3/bin/conda shell.bash hook)"

export CUDA_VISIBLE_DEVICES=0

conda deactivate
conda activate graph_scrap

cd $HOME/graph_scrap/wykop-scrap

#port=$1
./06a-pipeline-link_ids-to-votes-subset.sh
#/usr/bin/ssh -N -f -R $port:localhost:$port gw.gmum
#jupyter notebook --no-browser --port $port
#jupyter notebook --ip 0.0.0.0 --port $port
