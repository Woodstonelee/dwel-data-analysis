import canupo

# mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_az10.msc")
mscfile = canupo.MSCFile("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points-sacc/HFHD_20140919_W_dual_cube_bsfix_pxc_update_atp2_ptcl_points.msc")

header = mscfile.get_header()
import pdb; pdb.set_trace()
pt_data = mscfile.read_point()
