#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-ndi-gap-fill-hfhd20140503
#$ -V
#$ -m ae
#$ -t 1-5

NIRPCINFOFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-C/HFHD_20140503_C_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-E/HFHD_20140503_E_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-N/HFHD_20140503_N_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-S/HFHD_20140503_S_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-W/HFHD_20140503_W_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
)

SWIRPCINFOFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-C/HFHD_20140503_C_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-E/HFHD_20140503_E_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-N/HFHD_20140503_N_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-S/HFHD_20140503_S_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-W/HFHD_20140503_W_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
)

NDIFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-C/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-E/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-N/HFHD_20140503_N_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-S/HFHD_20140503_S_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/HFHD20140503-W/HFHD_20140503_W_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-projected-image-analysis/dwel_ndi_image_gap_filling.py"

python $PYCMD -n ${NIRPCINFOFILES[$SGE_TASK_ID-1]} -s ${SWIRPCINFOFILES[$SGE_TASK_ID-1]} -o ${NDIFILES[$SGE_TASK_ID-1]} -k 3