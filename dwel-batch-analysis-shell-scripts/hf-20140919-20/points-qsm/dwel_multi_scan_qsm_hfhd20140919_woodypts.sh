#!/bin/bash
#$ -q "geo*"
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=24:00:00
#$ -N dwel-multiscan-qsm-hfhd20140919-woodypts
#$ -V
#$ -m ae
#$ -t 1-5

# ML="/usr/local/bin/matlab -nodisplay -nojvm -singleCompThread -r "
ML="/usr/local/bin/matlab -nodisplay -nojvm -r "

# path to the QSM tool
QSMPATH="/usr3/graduate/zhanli86/Programs/Tree_model_2.0"
# script file to run
MLSCRIPT="/usr3/graduate/zhanli86/Programs/Tree_model_2.0/scripts/make_models_DWEL.m"

# input point cloud file of a single tree
INPTSFILES=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/HFHD_20140919_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_tree1.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/HFHD_20140919_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_tree2.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/HFHD_20140919_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_tree3.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/HFHD_20140919_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_tree4.asc" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/HFHD_20140919_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_tree5.asc" \
)
# descriptive suffix for output files
SUFFIXES=( \
"hfhd20140919_tree1_woodypts" \
"hfhd20140919_tree2_woodypts" \
"hfhd20140919_tree3_woodypts" \
"hfhd20140919_tree4_woodypts" \
"hfhd20140919_tree5_woodypts" \
)

DIRSUFFIX=$(date '+%Y%m%d%H%M%S')
# output directory where output files are moved to
OUTDIRS=( \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/woody-points/$DIRSUFFIX" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/woody-points/$DIRSUFFIX" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/woody-points/$DIRSUFFIX" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/woody-points/$DIRSUFFIX" \
"/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm/qsm-param-sensitivity/woody-points/$DIRSUFFIX" \
)
for f in "${OUTDIRS[@]}"
do
    if [ ! -d "$f" ]; then
	mkdir -p $f
    fi
done

# input parameters for running QSM
WOOD_ONLY="true"
QSM_FILTERING="true"
RFIL1=0.1
NFIL1=3
RFIL2=0.2
NFIL2=3
DMIN0=0.20
RCOV0=0.22
NMIN0=3
DMINVAR="[0.11]"
NMIN=3
LCYL=6
NOGROUND="true"
N=30

MLLINES="\
singletreeptsfile = '${INPTSFILES[$SGE_TASK_ID-1]}'; \
suffix = '${SUFFIXES[$SGE_TASK_ID-1]}'; \
outdir = '${OUTDIRS[$SGE_TASK_ID-1]}'; \
wood_only = $WOOD_ONLY; \
qsm_filtering = $QSM_FILTERING; \
rfil1 = $RFIL1; \
nfil1 = $NFIL1; \
rfil2 = $RFIL2; \
nfil2 = $NFIL2; \
dmin0 = $DMIN0; \
rcov0 = $RCOV0; \
nmin0 = $NMIN0; \
dminvar = $DMINVAR; \
nmin = $NMIN; \
lcyl = $LCYL; \
NoGround = $NOGROUND; \
N = $N; \
addpath(genpath('$QSMPATH')); \
run '$MLSCRIPT'; \
"
$ML "$MLLINES"
