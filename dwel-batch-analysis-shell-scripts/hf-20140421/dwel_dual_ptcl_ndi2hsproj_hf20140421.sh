#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-ptsndi2hs-hf20140421
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_-0.154.txt" \
)

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points-class-by-ndi/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_NDI_hsp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"

python $PYCMD -i ${CLSPTSFILES[$SGE_TASK_ID-1]} -o ${HSPRJFILES[$SGE_TASK_ID-1]} -p 15 --pixelfunc "mean" -H 1.5 --maxzen=117