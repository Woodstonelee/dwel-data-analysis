#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dualpts2hs-hf20140421
#$ -V
#$ -m ae
#$ -t 1-10

DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

HSPRJFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/HFHD20140421-dual-points/HFHD_20140421_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_swir_hsp2.img" \
)

PIXELCOL=( \
4 \
4 \
4 \
4 \
4 \
5 \
5 \
5 \
5 \
5 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2hsproj.py"
python $PYCMD -i ${DUALPTSFILES[$SGE_TASK_ID-1]} -o ${HSPRJFILES[$SGE_TASK_ID-1]} -p ${PIXELCOL[$SGE_TASK_ID-1]} --pixelfunc "mean" -M --pulseno=6 --intensity=${PIXELCOL[$SGE_TASK_ID-1]} -H 1.5 --maxzen=117
