#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-clspts2at-hfhd20140919
#$ -V
#$ -m ae
#$ -t 1-5

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_S_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
)

CAMHEIGHTS=( \
  1.30 1.40 1.10 1.12 1.36 \
)

OUTRES=3

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2atproj.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

INFILENAME=${BASENAME:0:${#BASENAME}-4}".txt"
OUTFILENAME=${BASENAME:0:${#BASENAME}-4}"_atp3.img"

python $PYCMD -i $INFILENAME -o $OUTFILENAME -p 24 --pixelfunc "mode" -C -M --pulseno=8 --intensity=4 -H ${CAMHEIGHTS[$SGE_TASK_ID-1]} --maxzen=117 -r $OUTRES