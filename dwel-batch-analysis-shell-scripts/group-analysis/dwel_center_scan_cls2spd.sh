#!/bin/bash
#$ -V
#$ -l mem_total=8
#$ -l h_rt=24:00:00
#$ -pe omp 4
#$ -m ae
#$ -N dwel-center-scan-cls2spd
#$ -t 1:4

INFILENAMES=( \
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

PYCMD="/usr3/graduate/zhanli86/Programs/tlsrepo/tlsiig_brisbane/converters/dwel/nsfdwelclspoints2spd.py"

python $PYCMD -i ${INFILENAMES[$SGE_TASK_ID-1]} --agh ${INSHEIGHTS[$SGE_TASK_ID-1]} --inres 0.115 --nrow 1022 --ncol 3142
