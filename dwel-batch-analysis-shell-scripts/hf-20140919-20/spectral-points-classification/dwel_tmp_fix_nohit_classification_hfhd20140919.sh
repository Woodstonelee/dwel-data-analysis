#!/bin/bash
#$ -pe omp 4
#$ -l h_rt=24:00:00
#$ -l mem_total=4
#$ -V
#$ -N dwel-tmp-fix-nohit-classification-hfhd20140919
#$ -m ae
#$ -t 1-5

CLSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
)

DUALFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

FIXEDFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed.txt" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_tmp_fix_canupo_class_nohit.py"
python $PYCMD --classpts ${CLSFILES[$SGE_TASK_ID-1]} --dualpts ${DUALFILES[$SGE_TASK_ID-1]} --fixed ${FIXEDFILES[$SGE_TASK_ID-1]}