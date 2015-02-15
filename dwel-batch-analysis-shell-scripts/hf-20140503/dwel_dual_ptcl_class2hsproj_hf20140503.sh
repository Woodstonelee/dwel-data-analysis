#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-clspts2hs-hf20140503
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051.txt" \
)

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class_NDI_thresh_0.051_hsp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"

python $PYCMD -i ${CLSPTSFILES[$SGE_TASK_ID-1]} -o ${HSPRJFILES[$SGE_TASK_ID-1]} -p 16 --pixelfunc "mode" -C -M --pulseno=6 --intensity=4 -H 1.5 --maxzen=117