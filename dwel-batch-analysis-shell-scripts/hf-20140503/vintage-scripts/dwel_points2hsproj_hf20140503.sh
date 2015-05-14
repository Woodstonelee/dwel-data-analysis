#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-pts2hs-hf20140503
#$ -V
#$ -m ae
#$ -t 1-10

PTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-C/HFHD_20140503_C_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-E/HFHD_20140503_E_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-N/HFHD_20140503_N_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-S/HFHD_20140503_S_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-W/HFHD_20140503_W_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-C/HFHD_20140503_C_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-E/HFHD_20140503_E_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-N/HFHD_20140503_N_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-S/HFHD_20140503_S_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-W/HFHD_20140503_W_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
)

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-C/HFHD_20140503_C_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-E/HFHD_20140503_E_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-N/HFHD_20140503_N_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-S/HFHD_20140503_S_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-W/HFHD_20140503_W_1064_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-C/HFHD_20140503_C_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-E/HFHD_20140503_E_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-N/HFHD_20140503_N_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-S/HFHD_20140503_S_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-W/HFHD_20140503_W_1548_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_meanmax_hsproj.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"

python $PYCMD -i ${PTSFILES[$SGE_TASK_ID-1]} -o ${HSPRJFILES[$SGE_TASK_ID-1]} -p 4 --pixelfunc "mean" -M --pulseno=7 --intensity=4 -H 1.5 --maxzen=117