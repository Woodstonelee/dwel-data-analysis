#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=4
#$ -l h_rt=72:00:00
#$ -N dwel-ndi-gap-fill-hfhd20140919-20
#$ -V
#$ -m ae
#$ -t 1-10

NIRPCINFOFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_E/HFHD_20140919_E_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_N/HFHD_20140919_N_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_S/HFHD_20140919_S_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_W/HFHD_20140919_W_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_C/HFHM_20140920_C_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_E/HFHM_20140920_E_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_N/HFHM_20140920_N_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_S2/HFHM_20140920_S2_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_W/HFHM_20140920_W_1064_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
)

SWIRPCINFOFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_E/HFHD_20140919_E_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_N/HFHD_20140919_N_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_S/HFHD_20140919_S_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_W/HFHD_20140919_W_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_C/HFHM_20140920_C_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_E/HFHM_20140920_E_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_N/HFHM_20140920_N_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_S2/HFHM_20140920_S2_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_W/HFHM_20140920_W_1548_cube_bsfix_pxc_update_atp2_ptcl_pcinfo.img" \
)

NDIFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_E/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_N/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_S/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_W/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_C/HFHM_20140920_C_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_E/HFHM_20140920_E_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_N/HFHM_20140920_N_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_S2/HFHM_20140920_S2_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140920/HFHM_20140920_W/HFHM_20140920_W_dual_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-projected-image-analysis/dwel_ndi_image_gap_filling.py"

python $PYCMD -n ${NIRPCINFOFILES[$SGE_TASK_ID-1]} -s ${SWIRPCINFOFILES[$SGE_TASK_ID-1]} -o ${NDIFILES[$SGE_TASK_ID-1]} -k 3