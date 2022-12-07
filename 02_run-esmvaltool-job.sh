#!/bin/bash
#SBATCH --partition=medium
#SBATCH -o slurm-%j.out
#SBATCH -e slurm-%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=simon.moulds@ouce.ox.ac.uk
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=48
#SBATCH --job-name=esmvaltool
#SBATCH --time=24:00:00

cd $SCRATCH || exit 1

module load Anaconda3/2020.11
module load NCO/5.0.1-foss-2021a
source activate $DATA/envs/esmvaltool

# PYTHONPATH sometimes causes issues
export PYTHONPATH=

WORKDIR=/home/cenv0857/decadal-prediction-data-preparation

esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True $WORKDIR/esmvaltool-recipes/recipe_s20_cmip5_autogen.yml
esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True $WORKDIR/esmvaltool-recipes/recipe_s20_cmip6_autogen.yml

# python $WORKDIR/03_process-ncar-prec-data.py --config $WORKDIR/arc-config.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_s20_grid_cmip5_autogen.yml
# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_s20_grid_cmip6_autogen.yml

rsync -av esmvaltool_output $DATA
