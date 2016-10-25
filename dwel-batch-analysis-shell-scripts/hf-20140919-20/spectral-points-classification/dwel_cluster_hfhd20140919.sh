#!/bin/bash
#$ -pe omp 8
#$ -l mem_total=8G
#$ -l h_rt=72:00:00
#$ -N dwel-cluster-hfhd20140919
#$ -V
#$ -m ae
#$ -t 1:5

SPECPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.txt" \
)

MSCFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc" \
)

CLSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return_spabirch.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return_spabirch.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return_spabirch.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return_spabirch.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return_spabirch.txt" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/spectral-and-canupo-clustering/dwel_classify_points.py"

python $PYCMD -i "${SPECPTSFILES[$SGE_TASK_ID-1]}" -o "${CLSFILES[$SGE_TASK_ID-1]}" --classifier "Spatial-BIRCH" --mscfile "${MSCFILES[$SGE_TASK_ID-1]}"
