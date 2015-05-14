#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-cc-hsp-hfhd20140608-09
#$ -V
#$ -m ae
#$ -t 1-10

NIRFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
)

SWIRFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
)

CCFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/HFHD_20140608_dual_points/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/HFHM_20140609_dual_points/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_cc_hsproj.py"

python $PYCMD -n ${NIRFILES[$SGE_TASK_ID-1]} -s ${SWIRFILES[$SGE_TASK_ID-1]} -c ${CCFILES[$SGE_TASK_ID-1]}
