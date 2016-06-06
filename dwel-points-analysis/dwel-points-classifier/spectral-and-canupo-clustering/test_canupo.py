import canupo

# mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.msc")
# mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-sacc/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.msc")
mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-sacc/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_az15_nohdr.msc")

header = mscfile.get_header()
import pdb; pdb.set_trace()
pt_data = mscfile.read_point()
