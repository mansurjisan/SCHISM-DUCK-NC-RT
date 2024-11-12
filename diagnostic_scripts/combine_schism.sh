#!/bin/bash
#SBATCH --job-name=combine_schism    # Job name
#SBATCH --nodes=1                    # Number of nodes
#SBATCH --ntasks=19                  # Total number of tasks
#SBATCH --time=02:00:00              # Wall time limit (2 hours)
#SBATCH --output=combine_%j.log      # Standard output log
#SBATCH --error=combine_%j.err       # Standard error log

# Exit on any error
set -e

# Print start time

echo "Starting SCHISM output combination at $(date)"


# Function to check if a file exists
check_file() {
    if [ ! -f "$1" ]; then
        echo "Error: Required file $1 not found"
        exit 1
    fi
}

# Check for required files

check_file "load_env.sh"

check_file "combine_output11_MPI"

# Load environment

echo "Loading environment..."

source load_env.sh

if [ $? -ne 0 ]; then
    echo "Error: Failed to source load_env.sh"
    exit 1
fi

# Load required modules

echo "Loading required modules..."

module load contrib/0.1 intel-oneapi-mpi/2021.7.1 netcdf-c/4.9.2

if [ $? -ne 0 ]; then
    echo "Error: Failed to load required modules"
    exit 1
fi

# Run the combine command

echo "Starting combination process..."

srun --label -n 19 ./combine_output11_MPI -b 1 -e 17 -w 1 -v "elev" -o schout_elev

if [ $? -ne 0 ]; then
    echo "Error: Combination process failed"
    exit 1
fi

# Print completion message
echo "SCHISM output combination completed successfully at $(date)"

# Optional: List the output files
echo "Generated output files:"
ls -lh schout_elev*
