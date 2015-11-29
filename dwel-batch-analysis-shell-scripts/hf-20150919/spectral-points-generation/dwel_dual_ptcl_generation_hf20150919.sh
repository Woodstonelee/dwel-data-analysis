#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-dual-ptcl-gen-hf20150919
#$ -V
#$ -m ae
#$ -t 1-5

# recover more points in the spectral point cloud from union of two point clouds
UNION=1
if [ $UNION -eq 1 ]
then
    echo "Will generate spectral point cloud from union of two point clouds"
fi

NIRPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-C/HFHD_20150919_C_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-E/HFHD_20150919_E_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-N/HFHD_20150919_N_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-S/HFHD_20150919_S_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-W/HFHD_20150919_W_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

SWIRPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-C/HFHD_20150919_C_1548_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-E/HFHD_20150919_E_1548_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-N/HFHD_20150919_N_1548_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-S/HFHD_20150919_S_1548_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-W/HFHD_20150919_W_1548_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-points-analysis/dwel-spectral-points-generation/dwel_generate_spectral_points.py"

if [ $UNION -eq 1 ]
then
NDIFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-C/HFHD_20150919_C_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-E/HFHD_20150919_E_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-N/HFHD_20150919_N_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-S/HFHD_20150919_S_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/HFHD20150919-W/HFHD_20150919_W_cube_bsfix_pxc_update_atp2_ptcl_pcinfo_ndi.img" \
)
DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-union/hfhd20150919-dual-points/HFHD_20150919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-union/hfhd20150919-dual-points/HFHD_20150919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-union/hfhd20150919-dual-points/HFHD_20150919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-union/hfhd20150919-dual-points/HFHD_20150919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-union/hfhd20150919-dual-points/HFHD_20150919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

python $PYCMD -n ${NIRPTSFILES[$SGE_TASK_ID-1]} -s ${SWIRPTSFILES[$SGE_TASK_ID-1]} -o ${DUALPTSFILES[$SGE_TASK_ID-1]} --union --ndi ${NDIFILES[$SGE_TASK_ID-1]}

else
DUALPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-intersect/hfhd20150919-dual-points/HFHD_20150919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-intersect/hfhd20150919-dual-points/HFHD_20150919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-intersect/hfhd20150919-dual-points/HFHD_20150919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-intersect/hfhd20150919-dual-points/HFHD_20150919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2015/HFHD20150919/spectral-points-by-intersect/hfhd20150919-dual-points/HFHD_20150919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt" \
)

python $PYCMD -n ${NIRPTSFILES[$SGE_TASK_ID-1]} -s ${SWIRPTSFILES[$SGE_TASK_ID-1]} -o ${DUALPTSFILES[$SGE_TASK_ID-1]}
fi