#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dual-ptcl-class-hf20140608-09
#$ -V
#$ -m ae
#$ -t 1-20

DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt" \
)

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_ndi/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_ndi/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_sr/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_sr/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_sr/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_sr/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points_class_by_sr/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_sr/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_sr/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_sr/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_sr/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points_class_by_sr/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt" \
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
0.418 \
0.405 \
0.395 \
0.405 \
0.465 \
0.462 \
0.475 \
0.475 \
0.462 \
0.435 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-points-classifier/dwel_points_classifier_index.py"

if [ $SGE_TASK_ID -le 10 ]
then
    python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${CLSPTSFILES[$SGE_TASK_ID-1]} -x ${INDEX[$SGE_TASK_ID-1]} -v -t ${NDITHRESH[$SGE_TASK_ID-1]}
else
    python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${CLSPTSFILES[$SGE_TASK_ID-1]} -x ${INDEX[$SGE_TASK_ID-1]} -v
fi

