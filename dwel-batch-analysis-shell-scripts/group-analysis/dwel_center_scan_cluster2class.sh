#!/bin/bash
# #$ -pe omp 4
# #$ -l mem_total=8
# #$ -l h_rt=24:00:00
# #$ -N dwel-center-scan-cluster2class
# #$ -V
# #$ -m ae
# #$ -t 1:6

MIXCLSFILES=( \
""/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_0.txt" "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_-2.txt"" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_0.txt" \
)

CANUPOCLSFILES=( \
""/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_0_canupo.txt" "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_-2_canupo.txt"" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_0_canupo.txt" \
)

PURECLSFILES=( \
""/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_1.txt" "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_2.txt" "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_-1.txt"" \
""/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_1.txt" "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_2.txt" "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_-1.txt"" \
)

OUTFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
)

echo ${MIXCLSFILES[0]}

echo ${MIXCLSFILES[1]}