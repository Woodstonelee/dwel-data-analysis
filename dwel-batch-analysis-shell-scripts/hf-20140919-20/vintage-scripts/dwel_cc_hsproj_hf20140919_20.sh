#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-cc-hsp-hfhd20140919-20
#$ -V
#$ -m ae
#$ -t 1-10

NIRFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
)

SWIRFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
)

CCFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_dual_points/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_dual_points/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_cc_hsp2.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_cc_hsproj.py"

python $PYCMD -n ${NIRFILES[$SGE_TASK_ID-1]} -s ${SWIRFILES[$SGE_TASK_ID-1]} -c ${CCFILES[$SGE_TASK_ID-1]}
