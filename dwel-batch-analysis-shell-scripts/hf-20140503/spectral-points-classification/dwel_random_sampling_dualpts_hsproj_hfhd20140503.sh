#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-randsample-hsp-hf20140503
#$ -V
#$ -m ae
#$ -t 1-5

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
)

# HSPRJFILES=( \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
# "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
# )

SAMPLEFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-projected-image-analysis/dwel_image_random_sampling.py"

python $PYCMD -m ${HSPRJFILES[$SGE_TASK_ID-1]} -a ${HSPRJFILES[$SGE_TASK_ID-1]} -o ${SAMPLEFILES[$SGE_TASK_ID-1]} --maskband=1 --ancband=1 --classes 1 2 -n 68 15 --center 1022 1022 --radius 750