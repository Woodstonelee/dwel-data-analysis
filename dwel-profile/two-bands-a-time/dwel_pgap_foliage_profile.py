#!/usr/bin/env python
"""
Generate PAI and PAVD estimates from a DWEL scan at both wavelengths and for
both classes (leaves and woodies)

Heavily copied from a script by
John Armston (j.armston@uq.edu.au)

USAGE:

OPTIONS:

AUTHORS:
    Zhan Li, zhanli86@bu.edu
"""

# from __future__ import print_function

import argparse
import sys
import os

import numpy as np

# import matplotlib as mpl
# mpl.use('TkAgg')
# import matplotlib.pyplot as plt

# from spdtlstools import spdtlsground
# from spdtlstools import spdtlsprofile

import spddwelprofile

def getCmdArgs():
    """
    Get command line arguments
    """
    
    p = argparse.ArgumentParser(description=("Generate foliage/woody profiles from a DWEL scan in SPD files."))

    p.add_argument("-n","--nirfile", dest="nirfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.550_small_nir.spd", help=("Input SPD file of NIR scan"))
    p.add_argument("-s","--swirfile", dest="swirfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class_NDI_thresh_0.550_small_swir.spd", help=("Input SPD file of SWIR scan"))
    p.add_argument("-o","--outprefix", dest="outprefix", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/hfhd_20140919_c_dual", help=("Prefix including a full path to a directory for multiple output files"))

    # p.add_argument("-n","--nirfile", dest="nirfile", default=None, help=("Input SPD file of NIR scan"))
    # p.add_argument("-s","--swirfile", dest="swirfile", default=None, help=("Input SPD file of SWIR scan"))
    
    p.add_argument("--maxheight", dest="maxheight", type=float, default=30.0, help=("Maximum height for vertical profiles (default = 50 m)"))
    p.add_argument("--minazimuth", dest="minazimuth", type=float, default=0.0, help=("Start azimuth bin of sector to use for vertical profiles (default = 0 deg)"))
    p.add_argument("--maxazimuth", dest="maxazimuth", type=float, default=360.0, help=("End azimuth bin of sector to use for vertical profiles (default = 360 deg)"))
    p.add_argument("--minzenith", dest="minzenith", type=float, default=10.0, help=("Minimum zenith angle bin to use for vertical profiles (default = 30 deg)"))
    p.add_argument("--maxzenith", dest="maxzenith", type=float, default=70.0, help=("Maximum zenith angle bin to use for vertical proiles (default = 70 deg)"))
    p.add_argument("--binsize", dest="binsize", type=float, default=5.0, help=("Zenith angle bin size (default = 5 degrees)"))
    p.add_argument("--heightbinsize", dest="heightbinsize", type=float, default=0.5, help=("Height bin size (default = 0.5 m)"))
    p.add_argument("--resfactor", dest="resfactor", type=int, default=1, help=("Factor to reduce resolution by. Default is 1 (no change), otherwise > 1")) 

    p.add_argument("--fwhm", dest="fwhm", type=float, default=None, nargs=2, help=("FWHMs of Gaussian pulse model to synthesize waveforms, unit: meter. Two values, first for NIR, second for SWIR. If none, use default values from NSF DWEL: [0.547, 0.547]"))
    p.add_argument("--leafrho", dest="leafrho", type=float, default=None, nargs=2, help=("Leaf diffuse reflectance. Two values, first for NIR, second for SWIR. Must be provided simultaneously with woodrho. If none, use default values from Harvard Forest hardwood site: [0.413, 0.284]"))
    p.add_argument("--woodrho", dest="woodrho", type=float, default=None, nargs=2, help=("Woody diffuse reflectance. Two values, first for NIR, second for SWIR. Must be provided simultaneously with leafrho. If none, use default values from Harvard Forest hardwood site: [0.541, 0.540]"))
    p.add_argument("--minIa", dest="minIa", type=float, default=None, nargs=2, help=("Lower boundary to scale I_a to get Pgap, i.e. hard threshold, any I_a lower than this value will have Pgap=0. Two values, first for WOOD, second for LEAF. If none, use default values: [0.6, 0.6]"))
    p.add_argument("--maxIa", dest="maxIa", type=float, default=None, nargs=2, help=("Upper boundary to scale I_a to get Pgap, i.e. soft threshold, any I_a higher than this value will have Pgap=1. Two values, first for WOOD, second for LEAF. If none, use default values: [0.95, 0.95]"))

    p.add_argument("-p","--plot", dest="plot", default=False, action="store_true", help=("Plot resulting vertical profile. Default False."))
    p.add_argument("--savetemp", dest="savetemp", default=False, action="store_true", help=("Save intermediate variables to a temporary numpy data file (npz) for next time faster processing. File names are automatically generated according to --outprefix option. Default False."))
    p.add_argument("--usetemp", dest="usetemp", default=False, action="store_true", help=("Read and use intermediate variables from a saved numpy data file (npz) for next time faster processing. File names are automatically generated according to --outprefix option. Default False."))
    p.add_argument("-g","--debug", dest="debug", default=False, action="store_true", help=("Plot linear fitting plots of PAI estimation for debugging data processing. A lot of plots to save and may take a while. Default False."))

    cmdargs = p.parse_args()
    
    if (cmdargs.nirfile is None) or (cmdargs.swirfile is None):
        p.print_help()
        print("Input SPD filenames must be set.")
        sys.exit()
    
    return cmdargs


def main(cmdargs):
    """
    Run the TLS foliage profile
    """
    print "Input NIR: {0:s}".format(cmdargs.nirfile)
    print "Input SWIR: {0:s}".format(cmdargs.swirfile)

    print("Initiating object of foliage profile ...")
    profileobj = spddwelprofile.dwelDualProfile(cmdargs.nirfile, cmdargs.swirfile, \
                                                    zenithbinsize=cmdargs.binsize, \
                                                    minzenith=cmdargs.minzenith, \
                                                    maxzenith=cmdargs.maxzenith, \
                                                    minazimuth=cmdargs.minazimuth, \
                                                    maxazimuth=cmdargs.maxazimuth, \
                                                    maxht=cmdargs.maxheight, \
                                                    htbinsize=cmdargs.heightbinsize, \
                                                    rgres=0.075, \
                                                    savevar=cmdargs.savetemp, \
                                                    tempprefix=cmdargs.outprefix)
    if cmdargs.fwhm is None:
        fwhm = None
    else:
        fwhm = np.array(cmdargs.fwhm)
    if cmdargs.woodrho is None or cmdargs.leafrho is None:
        rho_d = None
    else:
        rho_d = np.array([cmdargs.woodrho, cmdargs.leafrho])
    if cmdargs.minIa is None:
        min_Ia = None
    else:
        min_Ia = np.array([cmdargs.minIa, cmdargs.minIa]).T
    if cmdargs.maxIa is None:
        max_Ia = None
    else:
        max_Ia = np.array([cmdargs.maxIa, cmdargs.maxIa]).T

    if cmdargs.usetemp:
        print "Reading and will use 2D view of Pgap from previously saved npz file"
        npzfile = np.load((profileobj.tempprefix + "_Pgap2DView.npz"))
        PgapZenRgView = npzfile['PgapZenRgView'].item()
        PgapZenAzView = npzfile['PgapZenAzView'].item()
        sensorheight = npzfile['sensorheight'].item()
    else:
        print "Generating 2D view of Pgap via synthesizing waveforms from point cloud for leaves and woodies from both NIR and SWIR"
        PgapZenAzView, PgapZenRgView, sensorheight = profileobj.genWaveformPgap2DView(fwhm=fwhm, rho_d=rho_d, min_Ia=min_Ia, max_Ia=max_Ia)

    print "Getting Pgap profile along canopy height at different zenith angles ..."
    pgapprofiles = profileobj.getDualPgapProfile(PgapZenRgView, sensorheight)

    print "Calculating plant profile for leaves and woodies from both NIR and SWIR with linear fitting by Jupp et. al. 2009 ..."
    plantprofiles = profileobj.getLinearDualPlantProfile(pgapprofiles, plot=cmdargs.debug)

    print "Writing plant profile to a csv file ..."
    profileobj.writeDualPlantProfile(plantprofiles, profileobj.tempprefix + "_dualplantprofile.txt")
    print "Output written to "+profileobj.tempprefix + "_dualplantprofile.txt"

    if cmdargs.plot:
        print "Plotting all profiles ... "
        for i, name in enumerate(profileobj.pgapclassname):
            profileobj.plotPgapProfile(pgapprofiles, name, outfile=cmdargs.outprefix+"_pgapprofile_"+name+'.png')
        for i, name in enumerate(profileobj.pgapclassname):
            profileobj.plotPgapZenAzView(PgapZenAzView, name, outfile=cmdargs.outprefix+"_pgapzenazview_"+name+'.png')
        profileobj.plotPlantProfile(plantprofiles, outfile=cmdargs.outprefix+"_plantprofiles.png")


# Run the script
if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
