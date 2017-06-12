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

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
# plt.ion()

# from spdtlstools import spdtlsground
# from spdtlstools import spdtlsprofile

import spddwelprofile

def getCmdArgs():
    """
    Get command line arguments
    """

    p = argparse.ArgumentParser(description=("Generate foliage/woody profiles from a DWEL scan in SPD files."))

    p.add_argument("-n","--nirfile", dest="nirfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed_nir.spd", help=("Input SPD file of NIR scan"))
    p.add_argument("-s","--swirfile", dest="swirfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_nohitfixed_swir.spd", help=("Input SPD file of SWIR scan"))
    p.add_argument("-o","--outprefix", dest="outprefix", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering-profiles/pgap-by-scaling/hfhd_20140503_c_dual", help=("Prefix including a full path to a directory for writing multiple output files, WITHOUT underscore in the end"))
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

    p.add_argument("--fwhm", action="append", dest="fwhm", type=float, default=[0.547, 0.547], nargs=2, metavar=("FWHM_NIR", "FWHM_SWIR"), help=("FWHMs of Gaussian pulse model to synthesize waveforms, unit: meter. Two values, first for NIR, second for SWIR. If none, use default values from NSF DWEL: %(default)s"))

    p.add_argument("--leafrho", dest="leafrho", type=float, default=[0.413, 0.284], nargs=2, metavar=("leafrho_NIR", "leafrho_SWIR"), help=("Leaf diffuse reflectance. Two values, first for NIR, second for SWIR. Must be provided simultaneously with woodrho. If none, use default values from Harvard Forest hardwood site: %(default)s"))
    p.add_argument("--woodrho", dest="woodrho", type=float, default=[0.541, 0.540], nargs=2, metavar=("woodrho_NIR", "woodrho_SWIR"), help=("Woody diffuse reflectance. Two values, first for NIR, second for SWIR. Must be provided simultaneously with leafrho. If none, use default values from Harvard Forest hardwood site: %(default)s"))
    p.add_argument("--plantrho", dest="plantrho", type=float, default=[None, None], nargs=2, metavar=("plantrho_NIR, plantrho_SWIR"), help=("'mean' diffuse reflectance of all foliage elements including both leaves and woodies. Could be a 'mean' reflectance of leaf and wood weighted by their areas. Two values, first for NIR, second for SWIR. If none, no plant profile (both leaves and woodies) will be generated from direct Pgap of all leaves and woodies"))
    p.add_argument("--pai", dest="pai", type=float, default=None, help="PAI from other approaches, including both leaves and woody materials. Default: none")

    pgapscaling = p.add_argument_group(title="Pgap by scaling (default method)", description="Estimate Pgap from apparent reflectance by scaling with given hard and soft thresholds.")
    pgapscaling.add_argument("--leafIalim", dest="leafIalim", type=float, default=[0.85, 0.99], nargs=2, metavar=("minIa(hard)", "maxIa(soft)"), help=("Lower and upper boundary to scale I_a to Pgap for leaves, i.e. hard and soft threshold, any I_a smaller than lower boundary will have Pgap=0 while any I_a larger than upper boundary will have Pgap=1. Two values, first for lower, second for upper. If none, use default values: %(default)s"))
    pgapscaling.add_argument("--woodIalim", dest="woodIalim", type=float, default=[0.85, 0.99], nargs=2, metavar=("minIa(hard)", "maxIa(soft)"), help=("Lower and upper boundary to scale I_a to Pgap for woodies, i.e. hard and soft threshold, any I_a smaller than lower boundary will have Pgap=0 while any I_a larger than upper boundary will have Pgap=1. Two values, first for lower, second for upper. If none, use default values: %(default)s"))
    pgapscaling.add_argument("--plantIalim", dest="plantIalim", type=float, default=[0.85, 0.99], nargs=2, metavar=("minIa(hard)", "maxIa(soft)"), help=("Lower and upper boundary to scale I_a to Pgap for all foliage elements (leaves and woodies together), i.e. hard and soft threshold, any I_a smaller than lower boundary will have Pgap=0 while any I_a larger than upper boundary will have Pgap=1. Two values, first for lower, second for upper. If none, use default values: %(default)s"))

    pgapnorm = p.add_argument_group(title="Pgap by normalization", description="Estimate Pgap from apparent reflectance by normalizing integral of apparent reflectance to 0-1")
    pgapnorm.add_argument("--normpgap", dest="normpgap", default=False, action="store_true", help=("Estimate Pgap by normalizing integral of apparent reflectance to 0-1. If you set --normpgap option to use normalization to estimate Pgap, default scaling method and its thresholds will be ignored. Default: false."))

    ptscls = p.add_argument_group(title="Point classification Information", description="Information about point classification, such as accuracy for adjustment of Pgap estimates")
    ptscls.add_argument("--errorAdjustedPgap", dest="err_adj_pgap", default=False, action="store_true", help="If set, adjust Pgap according to point classification errors given by user's and producer's accuracies.")
    ptscls.add_argument("--leafU", dest="leafU", type=float, nargs="+", metavar="User's accuracy for leaves", help="User's accuracy for leaf points. If one value given, the same accuracy is assigned to both NIR and SWIR point classification accuracy. If two values given, first for NIR points and the second for SWIR.")
    ptscls.add_argument("--leafP", dest="leafP", type=float, nargs="+", metavar="Producer's accuracy for leaves", help="Producer's accuracy for leaf points. If one value given, the same accuracy is assigned to both NIR and SWIR point classification accuracy. If two values given, first for NIR points and the second for SWIR.")
    ptscls.add_argument("--woodU", dest="woodU", type=float, nargs="+", metavar="User's accuracy for woody materials", help="User's accuracy for wood points. If one value given, the same accuracy is assigned to both NIR and SWIR point classification accuracy. If two values given, first for NIR points and the second for SWIR.")
    ptscls.add_argument("--woodP", dest="woodP", type=float, nargs="+", metavar="Producer's accuracy for woody materials", help="Producer's accuracy for wood points. If one value given, the same accuracy is assigned to both NIR and SWIR point classification accuracy. If two values given, first for NIR points and the second for SWIR.")

    p.add_argument("-p","--plot", dest="plot", default=False, action="store_true", help=("Plot resulting vertical profile. Default False."))
    p.add_argument("--savetemp", dest="savetemp", default=False, action="store_true", help=("Save intermediate variables to a temporary numpy data file (npz) for next time faster processing. File names are automatically generated according to --outprefix option. Default False."))
    p.add_argument("--usetemp", dest="usetemp", default=False, action="store_true", help=("Read and use intermediate variables from a saved numpy data file (npz) for next time faster processing. File names are automatically generated according to --outprefix option. Default False."))
    p.add_argument("-g","--debug", dest="debug", default=False, action="store_true", help=("Plot linear fitting plots of PAI estimation for debugging data processing. A lot of plots to save and may take a while. Default False."))

    p.add_argument("--pgap2dmaxrg", dest="pgap2dmaxrg", type=float, default=None, help="Maximum range up to which the Pgap 2D Zenith-Azimuth view is saved. Default: None and will use the range limit of the input data.")
    
    p.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Turn on verbosity')
    
    cmdargs = p.parse_args()
    
    if (cmdargs.nirfile is None) or (cmdargs.swirfile is None):
        p.print_help()
        print("Input SPD filenames must be set.")
        sys.exit()

    if (cmdargs.err_adj_pgap) and ((cmdargs.leafU is None) or (cmdargs.leafP is None) or (cmdargs.woodU is None) or (cmdargs.woodP is None)):
        p.print_help()
        print("User's and producer's accuracies for both leaf and woody point classification are needed to adjust Pgap according to classification errors!")
        sys.exit()
    
    return cmdargs

def plotDualPlantProfileClass(nirplantprofileclass, swirplantprofileclass, outfile=None):
    fig = plt.figure(figsize=(8, 5))
    ax1 = plt.subplot2grid((6, 2), (0, 0), rowspan=5)
    ax2 = plt.subplot2grid((6, 2), (0, 1), rowspan=5, sharey=ax1)
    ax3 = plt.subplot2grid((6, 2), (5, 0), colspan=2)
    ax1.hold(True)
    ax2.hold(True)
    lineplots = []
    markerstr = {'leaf_nir':'-g', 'wood_nir':'-r', 'total_nir':'-k', 'plant_nir':'-m', \
                     'leaf_swir':'--g', 'wood_swir':'--r', 'total_swir':'--k'}
    for i, name in enumerate(nirplantprofileclass['classname']):
        lineplots.append(ax1.plot(nirplantprofileclass[name].PAI, nirplantprofileclass['height'], markerstr[name], label=name.replace('_', '\_'))[0])
        ax2.plot(nirplantprofileclass[name].PAVD, nirplantprofileclass['height'], markerstr[name], label=name.replace('_', '\_'))

    for i, name in enumerate(swirplantprofileclass['classname']):
        lineplots.append(ax1.plot(swirplantprofileclass[name].PAI, swirplantprofileclass['height'], markerstr[name], label=name.replace('_', '\_'))[0])
        ax2.plot(swirplantprofileclass[name].PAVD, swirplantprofileclass['height'], markerstr[name], label=name.replace('_', '\_'))

    ax1.set_xlim((0.0, ax1.get_xlim()[1]))
    ax2.set_xlim((0.0, ax2.get_xlim()[1]))
    ax1.set_title("PAI")
    ax2.set_title("PAVD")
    ax1.set_xlabel("PAI")
    ax1.set_ylabel("height (m)")
    ax2.set_xlabel("PAVD")
    ax2.set_ylabel("height (m)")

    plt.sca(ax3)
    plt.axis('off')
    legendstr = [ name.replace('_', '\_') for name in nirplantprofileclass['classname'] ]
    legendstr = legendstr + [ name.replace('_', '\_') for name in swirplantprofileclass['classname'] ]
    ax3.legend(lineplots, legendstr, bbox_to_anchor=(0., 0., 1, 0.1), loc='lower left', \
                   ncol=5, mode="expand", borderaxespad=0.)
    fig.tight_layout()

    if outfile is not None:
        plt.savefig(outfile, bbox_inches='tight')
    else:
        plt.show()

def writeMeta(cmdargs, clsU=None, clsP=None):
    """
    Write input parameters for pgap and plant profile calculation to a text
    file.
    """
    metafile = cmdargs.outprefix + "_pgap_foliage_profile_meta.txt"
    with open(metafile, 'w') as mf:
        mf.write("Meta data for calculating Pgap and foliage profile from a classified point cloud\n")
        mf.write("================================================================================\n")
        mf.write("\n")
        mf.write("Input NIR file = {0:s}\n".format(cmdargs.nirfile))
        mf.write("Input SWIR file = {0:s}\n".format(cmdargs.swirfile))
        mf.write("Output prefix = {0:s}\n".format(cmdargs.outprefix))
        mf.write("Height, meter (min, max, bin size) = {0:.3f}, {1:.3f}, {2:.3f}\n".format(0, cmdargs.maxheight, cmdargs.heightbinsize))
        mf.write("Zenith, degree  (min, max, bin size) = {0:.3f}, {1:.3f}, {2:.3f}\n".format(cmdargs.minzenith, cmdargs.maxzenith, cmdargs.binsize))
        mf.write("FWHM, meter (NIR, SWIR) = {0:.3f}, {1:.3f}\n".format(cmdargs.fwhm[0], cmdargs.fwhm[1]))
        mf.write("Leaf reflectance (NIR, SWIR) = {0:.3f}, {1:.3f}\n".format(cmdargs.leafrho[0], cmdargs.leafrho[1]))
        mf.write("Wood reflectance (NIR, SWIR) = {0:.3f}, {1:.3f}\n".format(cmdargs.woodrho[0], cmdargs.woodrho[1]))
        if cmdargs.plantrho[0] is None or cmdargs.plantrho[1] is None:
            mf.write("Plant reflectance, leaf and wood together (NIR, SWIR) = None, None\n")
        else:
            mf.write("Plant reflectance, leaf and wood together (NIR, SWIR) = {0:.3f}, {1:.3f}\n".format(cmdargs.leafrho[0], cmdargs.leafrho[1]))
        mf.write("\n")
        if cmdargs.normpgap:
            mf.write("Pgap by Normalization\n")
        else:
            mf.write("Pgap by Scaling\n")
            mf.write("Ia_lim of leaves (min, max) = {0:.3f}, {1:.3f}\n".format(cmdargs.leafIalim[0], cmdargs.leafIalim[1]))
            mf.write("Ia_lim of woodies (min, max) = {0:.3f}, {1:.3f}\n".format(cmdargs.woodIalim[0], cmdargs.woodIalim[1]))
            if cmdargs.plantrho[0] is None or cmdargs.plantrho[1] is None:
                mf.write("Ia_lim of plants, leaf and wood together (min, max) = None, None\n")
            else:
                mf.write("Ia_lim of plants, leaf and wood together (min, max) = {0:.3f}, {1:.3f}\n".format(cmdargs.plantIalim[0], cmdargs.plantIalim[1]))
        mf.write("\n")
        if cmdargs.savetemp:
            mf.write("2D view of Pgap will be generated via synthesizing waveforms from point cloud for leaves and woodies\n")
        if cmdargs.usetemp:
            mf.write("2D view of Pgap will be read and used from previously saved npz file\n")
        mf.write("\n")
        if cmdargs.err_adj_pgap:
            mf.write("Pgap profiles will be adjusted according to point classification error\n")
            mf.write("NIR,U,P\n")
            mf.write("Wood,{0:.3f},{1:.3f}\n".format(clsU["wood_nir"], clsP["wood_nir"]))
            mf.write("Leaf,{0:.3f},{1:.3f}\n".format(clsU["leaf_nir"], clsP["leaf_nir"]))
            mf.write("SWIR,U,P\n")
            mf.write("Wood,{0:.3f},{1:.3f}\n".format(clsU["wood_swir"], clsP["wood_swir"]))
            mf.write("Leaf,{0:.3f},{1:.3f}\n".format(clsU["leaf_swir"], clsP["leaf_swir"]))


def main(cmdargs):
    """
    Run the TLS foliage profile
    """
    
    print "Input NIR: {0:s}".format(cmdargs.nirfile)
    print "Input SWIR: {0:s}".format(cmdargs.swirfile)
    print "Pgap estimate method: {0:s}".format("Normalization" if cmdargs.normpgap else "Scaling")
    print "Save Pgap 2D view data? {0:s}".format("Yes" if cmdargs.savetemp else "No")

    if cmdargs.normpgap:
        leafIalim = None
        woodIalim = None
        plantIalim = None
    else:
        leafIalim = cmdargs.leafIalim
        woodIalim = cmdargs.woodIalim
        plantIalim = cmdargs.plantIalim

    clsU=None
    clsP=None
    if cmdargs.err_adj_pgap:
        clsU = dict()
        clsP = dict()
        if len(cmdargs.leafU) == 1:
            clsU["leaf_nir"] = cmdargs.leafU[0]
            clsU["leaf_swir"] = cmdargs.leafU[0]
        elif len(cmdargs.leafU) == 2:
            clsU["leaf_nir"] = cmdargs.leafU[0]
            clsU["leaf_swir"] = cmdargs.leafU[1]
        else:
            raise RuntimeError("Only up to 2 values accepted for the option --leafU")
        if len(cmdargs.leafP) == 1:
            clsP["leaf_nir"] = cmdargs.leafP[0]
            clsP["leaf_swir"] = cmdargs.leafP[0]
        elif len(cmdargs.leafP) == 2:
            clsP["leaf_nir"] = cmdargs.leafP[0]
            clsP["leaf_swir"] = cmdargs.leafP[1]
        else:
            raise RuntimeError("Only up to 2 values accepted for the option --leafP")
        if len(cmdargs.woodU) == 1:
            clsU["wood_nir"] = cmdargs.woodU[0]
            clsU["wood_swir"] = cmdargs.woodU[0]
        elif len(cmdargs.woodU) == 2:
            clsU["wood_nir"] = cmdargs.woodU[0]
            clsU["wood_swir"] = cmdargs.woodU[1]
        else:
            raise RuntimeError("Only up to 2 values accepted for the option --woodU")
        if len(cmdargs.woodP) == 1:
            clsP["wood_nir"] = cmdargs.woodP[0]
            clsP["wood_swir"] = cmdargs.woodP[0]
        elif len(cmdargs.woodP) == 2:
            clsP["wood_nir"] = cmdargs.woodP[0]
            clsP["wood_swir"] = cmdargs.woodP[1]
        else:
            raise RuntimeError("Only up to 2 values accepted for the option --woodP")

    # write meta data
    writeMeta(cmdargs, clsU=clsU, clsP=clsP)

    print("Initiating object of foliage profile ...")
    nirprofileobj = spddwelprofile.DWELClassProfile(cmdargs.nirfile, 'NIR', \
                                                    zenithbinsize=cmdargs.binsize, \
                                                    minzenith=cmdargs.minzenith, \
                                                    maxzenith=cmdargs.maxzenith, \
                                                    minazimuth=cmdargs.minazimuth, \
                                                    maxazimuth=cmdargs.maxazimuth, \
                                                    maxht=cmdargs.maxheight, \
                                                    htbinsize=cmdargs.heightbinsize, \
                                                    rgres=0.075, \
                                                    savevar=cmdargs.savetemp, \
                                                    tempprefix=cmdargs.outprefix, \
                                                    pgap2dmaxrg=cmdargs.pgap2dmaxrg, \
                                                    verbose=cmdargs.verbose)
    swirprofileobj = spddwelprofile.DWELClassProfile(cmdargs.swirfile, 'SWIR', \
                                                    zenithbinsize=cmdargs.binsize, \
                                                    minzenith=cmdargs.minzenith, \
                                                    maxzenith=cmdargs.maxzenith, \
                                                    minazimuth=cmdargs.minazimuth, \
                                                    maxazimuth=cmdargs.maxazimuth, \
                                                    maxht=cmdargs.maxheight, \
                                                    htbinsize=cmdargs.heightbinsize, \
                                                    rgres=0.075, \
                                                    savevar=cmdargs.savetemp, \
                                                    tempprefix=cmdargs.outprefix, \
                                                    pgap2dmaxrg=cmdargs.pgap2dmaxrg, \
                                                    verbose=cmdargs.verbose)

    if cmdargs.usetemp:
        print "Reading and will use 2D view of Pgap from previously saved npz file"
        nirnpzfile = np.load((nirprofileobj.tempprefix+"_"+nirprofileobj.bandlabel.lower()+"_Pgap2DView.npz"))
        nirPgapZenRgView = nirnpzfile['PgapZenRgView'].item()
        nirPgapZenAzView = nirnpzfile['PgapZenAzView'].item()
        nirsensorheight = nirnpzfile['sensorheight'].item()

        swirnpzfile = np.load((swirprofileobj.tempprefix+"_"+swirprofileobj.bandlabel.lower()+"_Pgap2DView.npz"))
        swirPgapZenRgView = swirnpzfile['PgapZenRgView'].item()
        swirPgapZenAzView = swirnpzfile['PgapZenAzView'].item()
        swirsensorheight = swirnpzfile['sensorheight'].item()

    else:
        print "Generating 2D view of Pgap via synthesizing waveforms from point cloud for leaves and woodies"
        nirPgapZenAzView, nirPgapZenRgView, nirsensorheight = \
            nirprofileobj.genWaveformPgap2DView(cmdargs.fwhm[0], \
                                                    cmdargs.leafrho[0], leafIalim, \
                                                    cmdargs.woodrho[0], woodIalim, \
                                                    cmdargs.plantrho[0], plantIalim)

        swirPgapZenAzView, swirPgapZenRgView, swirsensorheight = \
            swirprofileobj.genWaveformPgap2DView(cmdargs.fwhm[1], \
                                                    cmdargs.leafrho[1], leafIalim, \
                                                    cmdargs.woodrho[1], woodIalim, \
                                                    None, None)

    print "Getting Pgap profile along canopy height at different zenith angles ..."
    nirpgapprofiles = nirprofileobj.getPgapProfileClass(nirPgapZenRgView, nirsensorheight)
    swirpgapprofiles = swirprofileobj.getPgapProfileClass(swirPgapZenRgView, swirsensorheight)

    if cmdargs.err_adj_pgap:
        print "Adjusting Pgap profiles along canopy height according to point classification error ..."
        nirpgapprofiles = nirprofileobj.adjustPgapProfileClass(nirpgapprofiles, clsU, clsP)
        swirpgapprofiles = swirprofileobj.adjustPgapProfileClass(swirpgapprofiles, clsU, clsP)

    # print "Testing height profile of wood to leaf ratio at different zenith angles ..."
    # nirwood2leaf, zeniths, heights = nirprofileobj.getWoodToLeafProfile(nirpgapprofiles)
    # nirprofileobj.plotWoodToLeafProfile(nirwood2leaf, zeniths, heights, \
    #                                         outfile=cmdargs.outprefix+"_wood2leaf_profile_nir.png")
    # swirwood2leaf, zeniths, heights = swirprofileobj.getWoodToLeafProfile(swirpgapprofiles)
    # swirprofileobj.plotWoodToLeafProfile(swirwood2leaf, zeniths, heights, \
    #                                          outfile=cmdargs.outprefix+"_wood2leaf_profile_swir.png")
    
    print "Calculating plant profile for leaves and woodies with linear fitting by Jupp et. al. 2009 ..."
    nirplantprofiles = nirprofileobj.getLinearPlantProfileClass(nirpgapprofiles, plot=cmdargs.debug)
    swirplantprofiles = swirprofileobj.getLinearPlantProfileClass(swirpgapprofiles, plot=cmdargs.debug)

    print "Calculating relative plant profile for leaves and woodies with solid-angle-weighted average by Jupp et al. 2009 ..."
    saw_nirplantprofiles = nirprofileobj.getSolidAnglePlantProfileClass(nirpgapprofiles, PAI=cmdargs.pai)
    saw_swirplantprofiles = swirprofileobj.getSolidAnglePlantProfileClass(swirpgapprofiles, PAI=cmdargs.pai)
    
    print "Writing plant profile to a csv file ..."
    nirprofileobj.writePlantProfileClass(nirplantprofiles, nirprofileobj.tempprefix+"_"+nirprofileobj.bandlabel.lower()+"_plantprofileclass.txt")
    print "Output written to "+nirprofileobj.tempprefix+"_"+nirprofileobj.bandlabel.lower()+"_plantprofileclass.txt"
    swirprofileobj.writePlantProfileClass(swirplantprofiles, swirprofileobj.tempprefix+"_"+swirprofileobj.bandlabel.lower()+"_plantprofileclass.txt")
    print "Output written to "+swirprofileobj.tempprefix+"_"+swirprofileobj.bandlabel.lower()+"_plantprofileclass.txt"

    nirprofileobj.writePlantProfileClass(saw_nirplantprofiles, nirprofileobj.tempprefix+"_"+nirprofileobj.bandlabel.lower()+"_saw_plantprofileclass.txt")
    print "Output written to "+nirprofileobj.tempprefix+"_"+nirprofileobj.bandlabel.lower()+"_saw_plantprofileclass.txt"
    swirprofileobj.writePlantProfileClass(saw_swirplantprofiles, swirprofileobj.tempprefix+"_"+swirprofileobj.bandlabel.lower()+"_saw_plantprofileclass.txt")
    print "Output written to "+swirprofileobj.tempprefix+"_"+swirprofileobj.bandlabel.lower()+"_saw_plantprofileclass.txt"

    if cmdargs.plot:
        print "Plotting all profiles ... "
        for i, name in enumerate(nirpgapprofiles['classname']):
            nirprofileobj.plotPgapProfile(nirpgapprofiles[name], nirpgapprofiles['zenith'], \
                                              nirpgapprofiles['height'], name, \
                                              outfile=cmdargs.outprefix+"_pgapprofile_"+name+'.png')
        for i, name in enumerate(nirPgapZenAzView['classname']):
            nirprofileobj.plotPgapZenAzView(nirPgapZenAzView[name], nirPgapZenAzView['zenith'], \
                                                nirPgapZenAzView['azimuth'], name, \
                                                outfile=cmdargs.outprefix+"_pgapzenazview_"+name+'.png')
        for i, name in enumerate(nirPgapZenRgView['classname']):
            nirprofileobj.plotPgapZenRgView(nirPgapZenRgView[name], nirPgapZenRgView['zenith'], \
                                                nirPgapZenRgView['range'], name, \
                                                outfile=cmdargs.outprefix+"_pgapzenrgview_"+name+'.png')
        nirprofileobj.plotPlantProfileClass(nirplantprofiles, outfile=cmdargs.outprefix+"_plantprofiles_"+nirprofileobj.bandlabel.lower()+".png")
        nirprofileobj.plotPlantProfileClass(saw_nirplantprofiles, outfile=cmdargs.outprefix+"_saw_plantprofiles_"+nirprofileobj.bandlabel.lower()+".png")

        for i, name in enumerate(swirpgapprofiles['classname']):
            swirprofileobj.plotPgapProfile(swirpgapprofiles[name], swirpgapprofiles['zenith'], \
                                              swirpgapprofiles['height'], name, \
                                              outfile=cmdargs.outprefix+"_pgapprofile_"+name+'.png')
        for i, name in enumerate(swirPgapZenAzView['classname']):
            swirprofileobj.plotPgapZenAzView(swirPgapZenAzView[name], swirPgapZenAzView['zenith'], \
                                                swirPgapZenAzView['azimuth'], name, \
                                                outfile=cmdargs.outprefix+"_pgapzenazview_"+name+'.png')
        for i, name in enumerate(swirPgapZenRgView['classname']):
            swirprofileobj.plotPgapZenRgView(swirPgapZenRgView[name], swirPgapZenRgView['zenith'], \
                                                swirPgapZenRgView['range'], name, \
                                                outfile=cmdargs.outprefix+"_pgapzenrgview_"+name+'.png')
        swirprofileobj.plotPlantProfileClass(swirplantprofiles, outfile=cmdargs.outprefix+"_plantprofiles_"+swirprofileobj.bandlabel.lower()+".png")
        swirprofileobj.plotPlantProfileClass(saw_swirplantprofiles, outfile=cmdargs.outprefix+"_saw_plantprofiles_"+swirprofileobj.bandlabel.lower()+".png")

        # plot plant profiles from NIR and SWIR together
        plotDualPlantProfileClass(nirplantprofiles, swirplantprofiles, outfile=cmdargs.outprefix+"_plantprofiles_dual.png")
        plotDualPlantProfileClass(saw_nirplantprofiles, saw_swirplantprofiles, outfile=cmdargs.outprefix+"_saw_plantprofiles_dual.png")

        # plot Pgap zenith-azimuth view of band average
        nirprefix = [ cls.split('_')[0] for cls in nirPgapZenAzView['classname']]
        swirprefix = [ cls.split('_')[0] for cls in swirPgapZenAzView['classname']]
        for nirname, nirp in zip(nirPgapZenAzView['classname'], nirprefix):
            if nirp in swirprefix:
                swirname = swirPgapZenAzView['classname'][swirprefix.index(nirp)]
                name = nirp + "_band_average"
                swirprofileobj.plotPgapZenAzView((nirPgapZenAzView[nirname]+swirPgapZenAzView[swirname])*0.5, \
                                                     swirPgapZenAzView['zenith'], \
                                                     swirPgapZenAzView['azimuth'], name, \
                                                     outfile=cmdargs.outprefix+"_pgapzenazview_"+name+'.png')

# Run the script
if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
