#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dual-ptcl-class-hf20140503
#$ -V
#$ -m ae
#$ -t 1-10

DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points.txt" \
)

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-ndi/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-sr/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-sr/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-sr/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-sr/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-dual-points-class-by-sr/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac9_ptcl_points_class.txt" \
)

INDEX=( \
"NDI" \
"NDI" \
"NDI" \
"NDI" \
"NDI" \
"SR" \
"SR" \
"SR" \
"SR" \
"SR" \
)

NDITHRESH=( \
0.031 \
0.031 \
0.031 \
0.031 \
0.031 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_points_classifier_index.py"

if [ $SGE_TASK_ID -le 5 ]
then
    python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${CLSPTSFILES[$SGE_TASK_ID-1]} -x ${INDEX[$SGE_TASK_ID-1]} -v -t ${NDITHRESH[$SGE_TASK_ID-1]}
else
    python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${CLSPTSFILES[$SGE_TASK_ID-1]} -x ${INDEX[$SGE_TASK_ID-1]} -v
fi
