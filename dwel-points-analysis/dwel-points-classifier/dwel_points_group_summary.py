#!/usr/bin/env python
"""
Summarize all spectral index values from multiple scans, usually in the same
campaign. The files of spectral index of multiple scans are given in an ascii
file of file name list.

USAGE:

OPTIONS:

EXAMPLES:

AUTHORS:

    Zhan Li, zhanli86@bu.edu
"""

import sys
import os
import argparse
import time

import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

import seaborn as sns

def main(cmdargs):
    i_scale=1e3
    
    listfile = cmdargs.filelist
    nirampcol = cmdargs.niramp-1
    swirampcol = cmdargs.swiramp-1
    rangecol = cmdargs.range-1
    outprefix = cmdargs.outprefix

    rmin = cmdargs.rmin
    rmax = cmdargs.rmax
    rstep = cmdargs.rstep
    rbreak = cmdargs.rbreak
    
    ind = (rangecol, nirampcol, swirampcol)

    filelist = np.loadtxt(listfile, dtype='string')

    indexdata = []
    for f in filelist:
        print "Reading file, " + f
        tmpdata = np.loadtxt(f, dtype='float', delimiter=',', usecols=ind, \
                                 skiprows=3, comments=None)
        # remove data of zero hits
        indexdata.append(tmpdata[tmpdata[:, 0]>1e-10])

    indexdata = tuple(indexdata)
    indexdata = np.vstack(indexdata)

    # get range for plotting and regression
    if rmin is None:
        rmin = np.min(indexdata[:, 0])
    if rmax is None:
        rmax = np.max(indexdata[:, 0])

    # get the breakpoints along range for piecewise stats.
    if rbreak is None:
        pwflag = False
    else:
        rbreak = np.array(rbreak)
        print "rbreak = " + ",".join([str(r) for r in rbreak])
        pwflag = True

    if pwflag:
        # resolve conflicts between rmin, rmax and rbreak
        tmpind = np.where(np.less(rbreak, rmin))[0]
        if len(tmpind)>0:
            if tmpind[-1]==len(rbreak)-1:
                print "Error, breakpoints are all less than given minimum range"
                return
            else:
                rbreak = rbreak[tmpind[-1]+1:]
        tmpind = np.where(np.greater(rbreak, rmax))[0]
        if len(tmpind)>0:
            if tmpind[0]==0:
                print "Error, no breakpoints in between given minimum and maximum range"
                return
            else:
                rbreak = rbreak[:tmpind[0]]

        print "rbreak = " + ",".join([str(r) for r in rbreak])

        rbreak = np.hstack((rmin, rbreak, rmax))
    else:
        rbreak = np.array([rmin, rmax])
    
    ptsweights = indexdata[:, 0]**2

    # plot NIR and SWIR intensities on a scatter plot
    nirplotrange = (-0*i_scale, 1*i_scale)
    swirplotrange = (-0*i_scale, 1*i_scale)

    # plot points with hexbin to see the density of points, much faster!
    with sns.axes_style("white"):
        jointgrid = sns.jointplot(indexdata[:, 1].squeeze(), \
                          indexdata[:, 2].squeeze(), kind="hex", size=11, \
                          ylim=swirplotrange, xlim=nirplotrange, \
                          marginal_kws={"norm_hist":True, \
                                            "hist_kws":{"weights":ptsweights, \
                                                            "edgecolor":'None'}}, \
                          joint_kws={"C":ptsweights, \
                                         "reduce_C_function":np.sum});
        jointgrid.set_axis_labels(r"$\rho_{appNIR}$", r"$\rho_{appSWIR}$")
        plt.savefig(outprefix+"_hexbin_nir_vs_swir.png", bbox_inches="tight")
    
    histbins = np.arange(-1.0, 1.0, 0.01)

    # calculate NDI
    ndi = (indexdata[:, 1] - indexdata[:, 2])/(indexdata[:, 1] + indexdata[:, 2])

    # calculate pdf of spectral index
    sindexhist = np.histogram(ndi, bins=histbins, density=True, weights=ptsweights)
    sindexfreq = sindexhist[0]
    # plot histogram of spectral index in different range divisions
    pwndifreq = np.zeros((len(histbins)-1, len(rbreak)-1))
    for r in range(len(rbreak)-1):
        tmpmask = np.logical_and(np.greater_equal(indexdata[:, 0],rbreak[r]), np.less(indexdata[:, 0],rbreak[r+1]))
        if tmpmask.any():
            tmphist = np.histogram(ndi[tmpmask], bins=histbins, density=True, weights=ptsweights[tmpmask])
            pwndifreq[:, r] = tmphist[0]

    bins = (histbins[:-1] + histbins[1:])/2.0
    binsize = histbins[1:] - histbins[:-1]
    print "Plotting NDI histogram"
    histfig = plt.figure()
    ax = plt.subplot(111)
    plt.hold(True)
    plt.plot(bins, sindexfreq*binsize, label="All")
    for r in range(len(rbreak)-1):
        plt.plot(bins, pwndifreq[:, r]*binsize, label="{0:.3f} m to {1:.3f} m".format(rbreak[r], rbreak[r+1]))
    plt.minorticks_on()
    plt.grid(b=True, which='both')
    plt.xlabel('NDI')
    plt.ylabel('probability mass function')
    plt.legend(bbox_to_anchor=(0, -0.202, 1, 0.2), loc='lower left', ncol=3, mode='expand', borderaxespad=0.)
    plt.savefig(outprefix+"_ndi_hist.png", bbox_inches="tight")

    # write histogram data to a file
    tmpout = np.hstack(( bins.reshape(len(bins), 1), \
                             sindexfreq.reshape(len(sindexfreq), 1), \
                             pwndifreq))
    headerstr = "Histogram of NDI\n"+ \
        "from a list of files in: \n"+ \
        listfile+"\n"+ \
        "Run made at: "+time.strftime("%c")+"\n"+ \
        "bin_center,hist_all"
    for r in range(len(rbreak)-1):
        headerstr = headerstr + ",hist_{0:.3f}-{1:.3f}".format(rbreak[r], rbreak[r+1])
    np.savetxt(outprefix+"_ndi_hist.txt", tmpout, \
                   delimiter=',', header=headerstr.rstrip(), \
                   fmt="%.3f")

    # plot range against ndi
    print "Plotting NDI vs range"
    with sns.axes_style("white"):
        sns.jointplot(indexdata[:, 0].squeeze(), \
                          ndi.squeeze(), kind="hex", size=11, \
                          ylim=(-1.0, 1.0), xlim=(rmin, rmax), \
                          marginal_kws={"norm_hist":True, \
                                            "hist_kws":{"weights":ptsweights, \
                                                            "edgecolor":'None'}}, \
                          joint_kws={"C":ptsweights, \
                                         "reduce_C_function":np.sum});
        plt.savefig(outprefix+"_hexbin_range_vs_ndi.png")

    # compress information in original data points to mean of points at each
    # range interval. Too many points for regression.
    rglow = np.arange(np.fix((rmax-rmin)/rstep)) * rstep + rmin
    rgup = (np.arange(np.fix((rmax-rmin)/rstep))+1) * rstep + rmin
    rg = (rglow + rgup)*.5

    nrg = len(rg)
    totalweights = np.zeros(nrg)
    totalindex = np.zeros(nrg)
    print "Compressing data points to mean values"
    for p in range(indexdata.shape[0]):
        tmpind = np.fix((indexdata[p, 0]-rmin)/rstep).astype(int)
        if tmpind >= 0 and tmpind < nrg:
            # totalweights[tmpind] = totalweights[tmpind] + indexdata[p, 0]**2
            # totalindex[tmpind] = totalindex[tmpind] + indexdata[p, 0]**2*indexdata[p, 1]
            totalweights[tmpind] = totalweights[tmpind] + 1
            totalindex[tmpind] = totalindex[tmpind] + ndi[p]

    # remove ranges without points
    tmpind = np.where(totalweights!=0)[0]
    totalweights = totalweights[tmpind]
    totalindex = totalindex[tmpind]
    rg = rg[tmpind]
    meanindex = totalindex/totalweights

    # write mean index and range to a text file
    outmat = np.hstack((rg.reshape(len(rg), 1), meanindex.reshape(len(meanindex), 1)))
    headerstr = "range, r^2_weighted_mean_index"
    np.savetxt(outprefix+"_range_vs_ndi.txt", outmat, fmt="%.3f", \
                   delimiter=",", header=headerstr)

    # plot a regression line between range and ndi
    print "Plotting ndi against range"
    with sns.axes_style("darkgrid"):
        # first order, linear regression
        plt.figure()
        plt.subplot(111)
        plt.plot(rg, meanindex, '.')
        plt.savefig(outprefix+"_range_vs_ndi.png")
        # for r in range(len(rbreak)-1):
        #     tmpflag = np.logical_and(np.greater_equal(rg,rbreak[r]), np.less(rg,rbreak[r+1]))
        #     regax = sns.regplot(rg[tmpflag], meanindex[tmpflag], ci=68, order=1, robust=True)
        #     regax.set_xlim([rmin, rmax])
        #     regax.set_ylim([np.min(meanindex), np.max(meanindex)])
        #     plt.hold(True)
        # regax.get_xaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
        # regax.get_yaxis().set_minor_locator(mpl.ticker.AutoMinorLocator())
        # regax.grid(b=True, which='major', color='w', linewidth=1.0)
        # regax.grid(b=True, which='minor', color='w', linewidth=0.5)
        # plt.savefig(outprefix+"_pwreg1st_range_vs_ndi.png")

    # # estimate piecewise linear function
    # allpolyp = np.zeros((len(rbreak)-1, 2))
    # for r in range(len(rbreak)-1):
    #     tmpflag = np.logical_and(np.greater_equal(rg,rbreak[r]), np.less(rg,rbreak[r+1]))
    #     polyp = np.polyfit(rg[tmpflag], meanindex[tmpflag], 1)
    #     allpolyp[r, :] = polyp
    # # write piecewise linear function parameters to a text file
    # outmat = np.hstack((rbreak[0:-1].reshape(len(rbreak)-1, 1), \
    #                         rbreak[1:].reshape(len(rbreak)-1, 1), \
    #                         allpolyp))
    # headerstr = "rlow, rhigh, p_0, p_1"
    # np.savetxt(outprefix+"_pwreg1st_range_vs_ndi.txt", outmat, fmt="%.3f", \
    #                delimiter=",", header=headerstr)

def getCmdArgs():
    p = argparse.ArgumentParser(description=("Generate stats summary of multiple spectral point cloud files together."))

    p.add_argument("-l", "--list", dest="filelist", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/tmpfilelist.txt", help="ASCII file containing a list of spectral point cloud file names. Each line in the list file is a full path to a spectral point cloud file.")
    p.add_argument("-o", "--outprefix", dest="outprefix", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/tmp_points_group_summary", help="Prefix of output summary files. Be sure to include correct directory name in the prefix.")

    p.add_argument("--niramp", dest="niramp", default=4, type=int, help="Column index of NIR amplitude in input files, with first column being 1. Default: 4")
    p.add_argument("--swiramp", dest="swiramp", default=5, type=int, help="Column index of SWIR amplitude in input files, with first column being 1. Default: 5")
    p.add_argument("--range", dest="range", default=9, type=int, help="Column index of range in input files, with first column being 1. Default: 9")

    p.add_argument("--rmin", dest="rmin", default=None, type=float, help="Minimum range for plotting and regression. If none, minimum range of input data is used. Default: none")
    p.add_argument("--rmax", dest="rmax", default=None, type=float, help="Maximum range for plotting and regression. If none, maximum range of input data is used. Default: none")
    p.add_argument("--rstep", dest="rstep", default=0.1, type=float, help="Range interval to average data points. Default: 0.1 unit_of_input")

    p.add_argument("--rbreak", dest="rbreak", type=float, default=None, nargs='+', metavar=("rbreak_1", "rbreak_2"), help="Breakpoints along range for piecewise stats. If none, no piecewise stats will be performed. Default: none")

    cmdargs = p.parse_args()

    if (cmdargs.filelist is None) or (cmdargs.outprefix is None):
        p.print_help()
        print("Input file list and output prefix must be set.")
        sys.exit()
    return cmdargs

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)

