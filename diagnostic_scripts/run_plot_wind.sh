#!/bin/bash
#SBATCH --job-name=plot_elev         # Job name
#SBATCH --account=nosofs             # Account/Project
#SBATCH --time=02:00:00             # Wall time limit (2 hours)
#SBATCH --nodes=1                    # Number of nodes
#SBATCH --ntasks-per-node=1         # Tasks per node
#SBATCH --output=plot_elev_%j.log    # Standard output log
#SBATCH --error=plot_elev_%j.err     # Standard error log

# Load conda environment

source /apps/spack-managed/gcc-11.3.1/miniconda3-24.3.0-avnaftwsbozuvtsq7jrmpmcvf6c7yzlt/etc/profile.d/conda.sh
conda activate pyschism_mjisan

# Run the Python script
python plot_wspd.py

# Deactivate conda environment
conda deactivate
