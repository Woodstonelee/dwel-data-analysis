#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-randsample-hsp-hf20140421
#$ -V
#$ -m ae
#$ -t 1-5

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
)

SAMPLEFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/hfhd20140421-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/hfhd20140421-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/hfhd20140421-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/hfhd20140421-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/hfhd20140421-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
)

# start Zhan Li's python environment
module load anaconda
source activate zhanli_py27

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-projected-image-analysis/dwel_image_random_sampling.py"

python $PYCMD -m ${HSPRJFILES[$SGE_TASK_ID-1]} -o ${SAMPLEFILES[$SGE_TASK_ID-1]} --maskband=2 -n 100