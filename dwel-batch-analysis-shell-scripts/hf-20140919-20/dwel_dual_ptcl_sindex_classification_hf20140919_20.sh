#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dual-ptcl-class-hf20140919-20
#$ -V
#$ -m ae
#$ -t 1-20

DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
)

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_ndi/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_ndi/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_sr/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_sr/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_sr/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_sr/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points_class_by_sr/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_sr/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_sr/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_sr/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_sr/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points_class_by_sr/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
)

INDEX=( \
"NDI" \
"NDI" \
"NDI" \
"NDI" \
"NDI" \
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
"SR" \
"SR" \
"SR" \
"SR" \
"SR" \
)

NDITHRESH=( \
0.565 \
0.562 \
0.535 \
0.562 \
0.585 \
0.545 \
0.615 \
0.575 \
0.565 \
0.575
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_points_classifier_index.py"

if [ $SGE_TASK_ID -le 10 ]
then
    python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${CLSPTSFILES[$SGE_TASK_ID-1]} -x ${INDEX[$SGE_TASK_ID-1]} -v -t ${NDITHRESH[$SGE_TASK_ID-1]}
else
    python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${CLSPTSFILES[$SGE_TASK_ID-1]} -x ${INDEX[$SGE_TASK_ID-1]} -v
fi
