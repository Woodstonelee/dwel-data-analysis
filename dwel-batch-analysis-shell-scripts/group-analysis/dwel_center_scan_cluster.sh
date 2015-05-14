#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-center-scan-cluster
#$ -V
#$ -m ae
#$ -t 1:6

SPECPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/spectral-points-by-union/HFHM_20140609_dual_points/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

CLSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/spectral-points-by-union/HFHM_20140609_dual_points-clustering/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/spectral-points-by-union/HFHM_20140920_dual_points-clustering/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans.txt" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_classify_points.py"

python $PYCMD -i "${SPECPTSFILES[$SGE_TASK_ID-1]}" -o "${CLSFILES[$SGE_TASK_ID-1]}" --classifier KMeans --nclusters 100

