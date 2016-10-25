#!/usr/bin/env python

import canupo

from dwel_points_cluster import DWELPointsCluster

# import pdb; pdb.set_trace()
mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc")
# mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-sacc/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.msc")
# mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-sacc/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_az15_nohdr.msc")

# header = mscfile.get_header()

# pt_data = mscfile.read_point()

# pt_data_new = mscfile.read_point(5)

mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc")

dpc = DWELPointsCluster()

dpc.openMSC("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc")
dpc.openMSC("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_N_dual_cube_bsfix_pxc_update_atp2_ptcl_points_return.msc")

