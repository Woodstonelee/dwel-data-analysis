#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=72:00:00
#$ -N dwel-apprefl2at-center-scans
#$ -V
#$ -m ae
#$ -t 1-4

CLSPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/spectral-points-by-union/HFHD_20140608_dual_points-clustering/merging/HFHD_20140608_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt" \
)

INSHEIGHTS=( \
1.32 \
1.37 \
1.33 \
1.30 \
)

NORTHAZ=( \
0.0 \
274.03 \
0.0 \
0.0 \
)

PYCMD="/usr3/graduate/zhanli86/Programs/dwel-data-analysis/dwel-data-utils/dwel_points2atproj.py"

BASENAME=${CLSPTSFILES[$SGE_TASK_ID-1]}

INFILENAME=${BASENAME:0:${#BASENAME}-4}".txt"
OUTFILENAME=${BASENAME:0:${#BASENAME}-4}"_nir_atp2.img"
python $PYCMD -i $INFILENAME -o $OUTFILENAME -p 4 --pixelfunc "mean" --indexfunc "all" -H ${INSHEIGHTS[$SGE_TASK_ID-1]} --maxzen=117 -r 2.5 -N ${NORTHAZ[$SGE_TASK_ID-1]}
OUTFILENAME=${BASENAME:0:${#BASENAME}-4}"_swir_atp2.img"
python $PYCMD -i $INFILENAME -o $OUTFILENAME -p 5 --pixelfunc "mean" --indexfunc "all" -H ${INSHEIGHTS[$SGE_TASK_ID-1]} --maxzen=117 -r 2.5 -N ${NORTHAZ[$SGE_TASK_ID-1]}