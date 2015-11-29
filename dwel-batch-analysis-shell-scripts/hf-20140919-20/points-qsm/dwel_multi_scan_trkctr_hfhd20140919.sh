#!/bin/bash
#$ -pe omp 4
#$ -l mem_total=8
#$ -l h_rt=24:00:00
#$ -N dwel-multiscan-trkctr-hfhd20140919
#$ -V
#$ -m ae

ML="/usr/local/bin/matlab -nodisplay -nojvm -singleCompThread -r "

# Input point cloud file
INFILE="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/HFHD_20140919_5aligned_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt"
# a temporary folder to store all intermediate files, no trailing path seperator.
TMPDIR="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-clustering/merging/multi-scan-qsm"

MLSCRIPT="/usr3/graduate/zhanli86/Programs/TIES-TLS/Script_MultiScanAsciiPts2TrkCtr.m"

$ML "ScanPtsFile='$INFILE'; TmpDir='$TMPDIR'; run $MLSCRIPT;"
