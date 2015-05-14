#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-randsample-hsp-hfhd20140919
#$ -V
#$ -m ae
#$ -t 1-5

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2.img" \
)

SAMPLEFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/hfhd20140919-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/hfhd20140919-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/hfhd20140919-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/hfhd20140919-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/hfhd20140919-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples.txt" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-projected-image-analysis/dwel_image_random_sampling.py"

python $PYCMD -m ${HSPRJFILES[$SGE_TASK_ID-1]} -a ${HSPRJFILES[$SGE_TASK_ID-1]} -o ${SAMPLEFILES[$SGE_TASK_ID-1]} --maskband=1 --ancband=1 --classes 1 2 -n 15 76 --center 1022 1022 --radius 750