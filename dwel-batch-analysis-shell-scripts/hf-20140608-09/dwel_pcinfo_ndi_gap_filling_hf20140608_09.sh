#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-ndi-gap-fill-hfhd20140608-09
#$ -V
#$ -m ae
#$ -t 1-10

NIRPCINFOFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/C/HFHD_20140608_C_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/E/HFHD_20140608_E_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/N/HFHD_20140608_N_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/S/HFHD_20140608_S_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/W/HFHD_20140608_W_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/C/HFHM_20140609_C_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/E/HFHM_20140609_E_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/N/HFHM_20140609_N_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/S/HFHM_20140609_S_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/W/HFHM_20140609_W_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
)

SWIRPCINFOFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/C/HFHD_20140608_C_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/E/HFHD_20140608_E_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/N/HFHD_20140608_N_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/S/HFHD_20140608_S_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/W/HFHD_20140608_W_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/C/HFHM_20140609_C_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/E/HFHM_20140609_E_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/N/HFHM_20140609_N_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/S/HFHM_20140609_S_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/W/HFHM_20140609_W_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
)

NDIFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/C/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/E/HFHD_20140608_E_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/N/HFHD_20140608_N_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/S/HFHD_20140608_S_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/W/HFHD_20140608_W_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/C/HFHM_20140609_C_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/E/HFHM_20140609_E_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/N/HFHM_20140609_N_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/S/HFHM_20140609_S_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/W/HFHM_20140609_W_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-projected-image-analysis/dwel_ndi_image_gap_filling.py"

python $PYCMD -n ${NIRPCINFOFILES[$SGE_TASK_ID-1]} -s ${SWIRPCINFOFILES[$SGE_TASK_ID-1]} -o ${NDIFILES[$SGE_TASK_ID-1]} -k 3