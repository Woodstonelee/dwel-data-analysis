#!/usr/bin/env bash

# Convert the old format, mainly the header format of DWEL point
# clouds, single-spectral or bi-special to the new format.
# 
# Old header format:
# [DWEL Point Cloud Data]
# Run made at: Tue Mar 17 21:21:57 2015
# X,Y,Z,d_I,Return_Number,Number_of_Returns,Shot_Number,Run_Number,range,theta,phi,rk,Sample,Line,Band,d0,fwhm
#
# New header format:
# X,Y,Z,d_I,Return_Number,Number_of_Returns,Shot_Number,Run_Number,range,theta,phi,rk,Sample,Line,Band,d0,fwhm
# // [DWEL Point Cloud Data]
# // Run made at: Tue Mar 17 21:21:57 2015
# USAGE:
#  dwel_points_fmt_old2new.sh ASCII_POINTS_OLD_FMT ASCII_POINTS_NEW_FMT

read -d '' USAGE <<EOF
$(basename ${0}) ASCII_POINTS_OLD_FMT ASCII_POINTS_NEW_FMT

Convert the old format, mainly the header format of DWEL point
clouds, single-spectral or bi-special to the new format.

Old header format:
[DWEL Point Cloud Data]
Run made at: Tue Mar 17 21:21:57 2015
X,Y,Z,d_I,Return_Number,Number_of_Returns,Shot_Number,Run_Number,range,theta,phi,rk,Sample,Line,Band,d0,fwhm

New header format:
X,Y,Z,d_I,Return_Number,Number_of_Returns,Shot_Number,Run_Number,range,theta,phi,rk,Sample,Line,Band,d0,fwhm
// [DWEL Point Cloud Data]
// Run made at: Tue Mar 17 21:21:57 2015

EOF

if [[ -z ${1} ]]; then
    echo "${USAGE}"
    exit
fi
if [[ -z ${2} ]]; then
    echo "${USAGE}"
    exit
fi

OLD=${1}
NEW=${2}

head -n 3 ${OLD} | tail -n 1 > ${NEW}
echo "// "$(head -n 1 HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt | tail -n 1) >> ${NEW}
echo "// "$(head -n 2 HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt | tail -n 1) >> ${NEW}
tail -n +4 ${OLD} >> ${NEW}
