#!/bin/bash
#SBATCH --partition=medium
#SBATCH -o slurm-%j.out
#SBATCH -e slurm-%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=simon.moulds@ouce.ox.ac.uk
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=48
#SBATCH --job-name=esmvaltool
#SBATCH --time=48:00:00

cd $SCRATCH || exit 1

module load Anaconda3/2020.11
module load NCO/5.0.1-foss-2021a
source activate $DATA/envs/esmvaltool

# PYTHONPATH sometimes causes issues
export PYTHONPATH=

WORKDIR=/home/cenv0857/decadal-prediction-data-preparation

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True $WORKDIR/esmvaltool-recipes/recipe_s20_cmip5_autogen.yml
# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True $WORKDIR/esmvaltool-recipes/recipe_s20_cmip6_autogen.yml

python $WORKDIR/03_process-ncar-prec-data.py --config $WORKDIR/arc-config.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_cvdp_cmip5_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_s20_grid_cmip5_autogen.yml
# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-flood-prediction/esmvaltool-recipes/recipe_s20_grid_cmip6_autogen.yml

# ~/decadal-flood-prediction/XX_process-ncar-prec-data.py --config ~/decadal-flood-prediction/arc-config.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip5_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_canesm5_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_canesm5_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=ignore --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_cesm1_1_cam5_cmip5_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_ec_earth3_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=ignore --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_hadgem3_gc31_mm_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_ipsl_cm6a_lr_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_miroc6_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=ignore --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_mpi_esm1_2_hr_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_cmip6_norcpm1_autogen.yml

# esmvaltool run --skip-nonexistent=True --check_level=relaxed --offline=True ~/decadal-prediction-data-preparation/esmvaltool-recipes/recipe_s20_grid_cmip6_autogen.yml

rsync -av esmvaltool_output $DATA
