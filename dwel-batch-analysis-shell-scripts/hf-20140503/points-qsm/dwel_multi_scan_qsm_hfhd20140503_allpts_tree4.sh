#!/bin/bash
#$ -q "geo*"
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=36:00:00
#$ -N dwel-multiscan-qsm-hfhd20140503-allpts-tree4
#$ -V
#$ -m ae
#$ -t 1

# ML="/usr/local/bin/matlab -nodisplay -nojvm -singleCompThread -r "
ML="/usr/local/bin/matlab -nodisplay -nojvm -r "

# path to the QSM tool
QSMPATH="/usr3/graduate/zhanli86/Programs/Tree_model_2.0"
# script file to run
MLSCRIPT="/usr3/graduate/zhanli86/Programs/Tree_model_2.0/scripts/make_models_DWEL.m"

# input point cloud file of a single tree
INPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_reg2hfhd20140919_tree1.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_reg2hfhd20140919_tree2.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_reg2hfhd20140919_tree3.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_reg2hfhd20140919_tree4.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/HFHD_20140503_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_reg2hfhd20140919_tree5.asc" \
)
# descriptive suffix for output files
SUFFIXES=( \
"hfhd20140503_tree1_allpts" \
"hfhd20140503_tree2_allpts" \
"hfhd20140503_tree3_allpts" \
"hfhd20140503_tree4_allpts" \
"hfhd20140503_tree5_allpts" \
)

DIRSUFFIX=$(date '+%Y%m%d%H%M%S')
# output directory where output files are moved to
OUTDIRS=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/all-points/$DIRSUFFIX" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/all-points/$DIRSUFFIX" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/all-points/$DIRSUFFIX" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/all-points/tree4" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/all-points/$DIRSUFFIX" \
)

TREE_ID=4

if [ ! -d "${OUTDIRS[$TREE_ID-1]}" ]; then
    mkdir -p ${OUTDIRS[$TREE_ID-1]}
fi

# input parameters for running QSM
WOOD_ONLY="false"
QSM_FILTERING="true"
RFIL1=0.1
NFIL1=3
RFIL2=0.2
NFIL2=3
DMIN0=0.20
RCOV0=0.22
NMIN0=3
DMINVAR=(0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20)
NMIN=3
LCYL=6
NOGROUND="true"
N=30


MLLINES="\
singletreeptsfile = '${INPTSFILES[$TREE_ID-1]}'; \
suffix = '${SUFFIXES[$TREE_ID-1]}'; \
outdir = '${OUTDIRS[$TREE_ID-1]}'; \
wood_only = $WOOD_ONLY; \
qsm_filtering = $QSM_FILTERING; \
rfil1 = $RFIL1; \
nfil1 = $NFIL1; \
rfil2 = $RFIL2; \
nfil2 = $NFIL2; \
dmin0 = $DMIN0; \
rcov0 = $RCOV0; \
nmin0 = $NMIN0; \
dminvar = [${DMINVAR[$SGE_TASK_ID-1]}]; \
nmin = $NMIN; \
lcyl = $LCYL; \
NoGround = $NOGROUND; \
N = $N; \
addpath(genpath('$QSMPATH')); \
run '$MLSCRIPT'; \
"
$ML "$MLLINES"
