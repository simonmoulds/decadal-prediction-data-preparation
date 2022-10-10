#!/bin/bash
#SBATCH --partition=medium
#SBATCH -o slurm-%j.out
#SBATCH -e slurm-%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=simon.moulds@ouce.ox.ac.uk
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=48
#SBATCH --mem-per-cpu=4G
#SBATCH --job-name=esmvaltool
#SBATCH --time=48:00:00

cd $SCRATCH || exit 1

module load Anaconda3/2020.11
module load NCO/5.0.1-foss-2021a
source activate $DATA/envs/esmvaltool

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_cvdp_cmip5_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_s20_grid_cmip5_autogen.yml
# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_s20_grid_cmip6_autogen.yml

# ~/decadal-flood-prediction/XX_process-ncar-prec-data.py --config ~/decadal-flood-prediction/arc-config.yml

esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip5_autogen.yml
# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_s20_cmip6_autogen.yml

rsync -av esmvaltool_output $DATA
