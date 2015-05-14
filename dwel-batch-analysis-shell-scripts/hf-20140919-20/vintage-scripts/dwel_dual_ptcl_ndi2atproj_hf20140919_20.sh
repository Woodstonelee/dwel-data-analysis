#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-ptsndi2at-hf20140919-20
#$ -V
#$ -m ae
#$ -t 1-10

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.503.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.414.txt" \
)

ATPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_atp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2atproj.py"

python $PYCMD -i ${CLSPTSFILES[$SGE_TASK_ID-1]} -o ${ATPRJFILES[$SGE_TASK_ID-1]} -p 15 --pixelfunc "mean" -H 1.5 --maxzen=117