#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-randsample-hsp-hf20140608-09
#$ -V
#$ -m ae
#$ -t 1-10

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
)

SAMPLEFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/hfhd20140608-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/hfhd20140608-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/hfhd20140608-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/hfhd20140608-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/hfhd20140608-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/hfhm20140609-points-classification-accuracy-assessment/hsproj-random-samples/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/hfhm20140609-points-classification-accuracy-assessment/hsproj-random-samples/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/hfhm20140609-points-classification-accuracy-assessment/hsproj-random-samples/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/hfhm20140609-points-classification-accuracy-assessment/hsproj-random-samples/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/hfhm20140609-points-classification-accuracy-assessment/hsproj-random-samples/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
)

# start Zhan Li's python environment
module load anaconda
source activate zhanli_py27

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-projected-image-analysis/dwel_image_random_sampling.py"

python $PYCMD -m ${HSPRJFILES[$SGE_TASK_ID-1]} -o ${SAMPLEFILES[$SGE_TASK_ID-1]} --maskband=2 -n 100