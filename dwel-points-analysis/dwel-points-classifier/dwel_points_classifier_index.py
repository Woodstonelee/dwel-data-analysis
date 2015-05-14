#!/usr/bin/env python
"""
Classify DWEL's dual-wavelength point cloud with dual-wavelength intensities.
Threshoding spectral index

USAGE:

    dwel_points_classifier_spectral.py

OPTIONS:

EXAMPLES:

AUTHORS:

"""

import sys
import time
import argparse

import numpy as np
import scipy as sp
import scipy.stats as spstats
import scipy.optimize as spopt
from sklearn import mixture
from sklearn.preprocessing import StandardScaler

import matplotlib as mpl
# mpl.use('TkAgg') # for interactive plotting
mpl.use('Agg') # for non-interactive plotting running in batch job
import matplotlib.pyplot as plt
from matplotlib import gridspec

import seaborn as sns

def gauss2(x, *p):
    """
    Utility function for two-Gaussian curve fitting

    Args:

        x (1D numpy array [ndata,]):

        *p (list of parameters for Gaussians):

    Returns:
    """
    A1, mu1, sigma1, A2, mu2, sigma2 = p
    y = A1*np.exp( -(x-mu1)**2/(2.0*sigma1**2) )
    y = y + A2*np.exp( -(x-mu2)**2/(2.0*sigma2**2) )
    return y

def dwel_points_class_index(infile, outfile, idxname, \
                                rbreak=None, thresh=None, \
                                clipI=True, verbose=True):
    """
    Classify points with dual-wavelength intensities by simple NDI thresholding

    Args:

    Returns:

    """

    # first check the index name and threshold
    if (idxname.upper() != "NDI") and (idxname.upper() != "SR"):
        print "Name of spectral index can only be: \n" + \
            "'NDI': normalized difference index\n" + \
            "'SR': simple ratio\n"
        return ()

    if (thresh is None):
        if idxname.upper() == "NDI":
            thresh = 0.55
        elif idxname.upper() == "SR":
            thresh = 3.7
        else:
            print "Name of spectral index can only be: \n" + \
                "'NDI': normalized difference index\n" + \
                "'SR': simple ratio\n"
            return ()

    # set some parameters
    headerlines = 0
    # column indices for some records used here, with 0 as the first.
    cind = {'x':0, 'y':1, 'z':2, 'd_I_nir':3, 'd_I_swir':4, \
                'return_num':5, 'number_of_returns':6, \
                'shot_number':7, \
                'range':8, 'theta':9, 'phi':10, 'sample':11, 'line':12, \
                'fwhm_nir':13, 'fwhm_swir':14, 'multi_return':15}
    # scale of apparent reflectance
    i_scale = 1000.0

    print "Loading points"
    olddualpoints = np.loadtxt(infile, dtype=np.float32, delimiter=',')
    npts = olddualpoints.shape[0]
    oldpointlabel = np.zeros(npts, dtype=np.int)
    oldrgb = np.zeros((npts, 3), dtype=np.int)
    oldsindex = np.zeros(npts)
    # find zero-hit points
    hitind = np.where(olddualpoints[:, cind['number_of_returns']] != 0)[0]
    dualpoints = olddualpoints[hitind, :]

    # get range and set up rbreak for piecewise thresholding
    rmin = np.min(dualpoints[:, cind['range']])
    rmax = np.max(dualpoints[:, cind['range']])
    if rbreak is None:
        rbreak = np.array([rmin, rmax])
    else:
        rbreak = np.array(rbreak)
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
        rbreak = np.hstack((rmin, rbreak, rmax))

    print "rbreak including range minimum and maximum = " + ", ".join(["{0:.3f}".format(r) for r in rbreak])

    if clipI:
        flag = np.greater(dualpoints[:, cind['d_I_nir']], 1*i_scale)
        dualpoints[flag, cind['d_I_nir']:cind['d_I_nir']+1] = 1*i_scale
        flag = np.greater(dualpoints[:, cind['d_I_swir']], 1*i_scale)
        dualpoints[flag, cind['d_I_swir']:cind['d_I_swir']+1] = 1*i_scale

    ptsweights = (dualpoints[:, cind['range']]**2)
    
    if verbose:
        # plot NIR and SWIR intensities on a scatter plot
        nirplotrange = (-0*i_scale, 1*i_scale)
        swirplotrange = (-0*i_scale, 1*i_scale)

        # plot points with hexbin to see the density of points, much faster!
        with sns.axes_style("white"):
            jointgrid = sns.jointplot(dualpoints[:, cind['d_I_nir']].squeeze(), \
                              dualpoints[:, cind['d_I_swir']].squeeze(), kind="hex", size=11, \
                              ylim=swirplotrange, xlim=nirplotrange, \
                              marginal_kws={"norm_hist":True, \
                                                "hist_kws":{"weights":ptsweights, \
                                                                "edgecolor":'None'}}, \
                              joint_kws={"C":ptsweights, \
                                             "reduce_C_function":np.sum});
            jointgrid.set_axis_labels("$\rho_{appNIR}$", "$\rho_{appSWIR}$")

        # hexbinfig = plt.figure(figsize=(11, 7.5))
        # gs = gridspec.GridSpec(4, 4)
        # gs.update(left=0.02, right=0.87)
        # gs2 = gridspec.GridSpec(4, 1)
        # gs2.update(left=0.88, right=0.98)
        # axHexbin = plt.subplot(gs[0:3, 1:4])
        # hb = plt.hexbin(dualpoints[:, cind['d_I_nir']], \
        #               dualpoints[:, cind['d_I_swir']], \
        #                     C=ptsweights, \
        #                     reduce_C_function=np.sum, \
        #                     extent=[nirplotrange[0], nirplotrange[1], \
        #                                 swirplotrange[0], nirplotrange[1]], \
        #                     mincnt=1, \
        #                     vmin=1e2, vmax=1e6)
        # # plt.xlim(axHistNir.get_xlim())
        # # plt.ylim(axHistSwir.get_ylim())
        # plt.axis('equal')
        # #plt.autoscale(tight=True)
        # plt.title("Scatter plot with colored density"+ \
        #               r" between NIR and SWIR $\rho_{app}$")
        # axcb = plt.subplot(gs2[0:3, :])
        # cb = plt.colorbar(hb, cax=axcb)
        # cb.set_label("point counts")
        # # plot histogram of NIR and SWIR separately
        # axHistNir = plt.subplot(gs[3, 1:4], sharex=axHexbin)
        # # bins = np.arange(np.nanmin(dualpoints[:, cind['d_I_nir']]), \
        # #                      np.nanmax(dualpoints[:, cind['d_I_nir']]), \
        # #                      0.01*i_scale)
        # bins = np.arange(nirplotrange[0], nirplotrange[1], 0.01*i_scale)
        # plt.hist(dualpoints[:, cind['d_I_nir']], bins, normed=True, \
        #              label="NIR histogram", edgecolor='None', weights=ptsweights)
        # #axHistNir.set_xlim( axHexbin.get_xlim() )
        # plt.xlabel(r"NIR $\rho_{app}$*"+"{0:g}".format(i_scale))
        # axHistSwir = plt.subplot(gs[0:3, 0], sharey=axHexbin)
        # # bins = np.arange(np.nanmin(dualpoints[:, cind['d_I_swir']]), \
        # #                      np.nanmax(dualpoints[:, cind['d_I_swir']]), \
        # #                      0.01*i_scale)
        # bins = np.arange(swirplotrange[0], swirplotrange[1], 0.01*i_scale)
        # plt.hist(dualpoints[:, cind['d_I_swir']], bins, normed=True, \
        #              label="SWIR histogram", edgecolor='None', \
        #              orientation='horizontal', weights=ptsweights)
        # #plt.ylim( axHexbin.get_ylim() )
        # plt.ylabel(r"SWIR $\rho_{app}$*"+"{0:g}".format(i_scale))
        # gs.tight_layout(hexbinfig, rect=[0, 0, 0.87, 1])
        # gs2.tight_layout(hexbinfig, rect=[0.88, 0.1, 1, 0.9])

        plt.savefig(infile[:-4]+"_hexbin_nir_vs_swir_apprefl.png")

    if idxname.upper() == "NDI":
        sindex = (dualpoints[:, cind['d_I_nir']] - dualpoints[:, cind['d_I_swir']]).astype(float) \
            / (dualpoints[:, cind['d_I_nir']] + dualpoints[:, cind['d_I_swir']]).astype(float)
    elif idxname.upper() == "SR":
        sindex = (dualpoints[:, cind['d_I_nir']]).astype(float) \
            / (dualpoints[:, cind['d_I_swir']]).astype(float)
    else:
        # for future use
        return ()

#    sindex = sindex.reshape((len(sindex), 1))

    # classification with user given threshold
    pointlabel = np.ones_like(sindex, dtype=np.int)
    for r in range(len(rbreak)-1):
        tmpind = np.where(np.logical_and(np.greater_equal(dualpoints[:, cind['range']], rbreak[r]), \
                                     np.less(dualpoints[:, cind['range']], rbreak[r+1])))[0]
        if len(tmpind)>0:
            flag = np.greater_equal(sindex[tmpind], thresh[r])
            # leaves: label as 2
            pointlabel[tmpind[flag]] = 2

    # write classification results
    oldpointlabel[hitind] = pointlabel
    oldpointlabel = oldpointlabel.reshape(len(oldpointlabel), 1)
    oldsindex[hitind] = sindex
    oldsindex = oldsindex.reshape(len(oldsindex), 1)
    # generate RGB info
    rgb = np.zeros((len(pointlabel), 3), dtype=np.int)
    ind = np.where(pointlabel == 1)[0]
    rgb[ind, :]=[255, 0, 0]
    ind = np.where(pointlabel == 2)[0]
    rgb[ind, :]=[0, 255, 0]
    oldrgb[hitind, :] = rgb
    prefixstr = "[DWEL Dual-wavelength Point Cloud Classification " \
        + idxname.upper()+". Label, 1=others, 2=leaves]\n" \
        + "Run made at: " + time.strftime("%c") \
        + "[range_lb (thresh) = " \
        + ", ".join(["{0:.3f} ({1:.3f})".format(r, t) for r, t in zip(rbreak[0:-1], thresh)])+"]\n"
    headerstr = prefixstr + "x,y,z,d_I_nir,d_I_swir,return_number,number_of_returns,shot_number,range,theta," \
        +"phi,sample,line,fwhm_nir,fwhm_swir,multi-return,sindex,label,R,G,B"
    # write to file
    print "Saving classification by predefined threshold"
    fmtstr = "%.3f "*5 + "%d "*3 + "%.3f "*3 + "%d "*2 + "%.3f "*2 + "%d " \
        + "%.3f " + "%d "*4
    fmtstr = fmtstr.strip().split(" ")
    np.savetxt(outfile[:-4]+"_"+idxname.upper()+".txt", \
                   np.hstack((olddualpoints, oldsindex, oldpointlabel, oldrgb)), \
                   delimiter=',', \
                   fmt=fmtstr, \
                   header=headerstr.rstrip())

    if verbose:
        # plt.gcf().set_size_inches((11, 7.5))
        # plot histogram and estimate a threshold from histogram
        if idxname.upper() == "NDI":
            bins = np.arange(-1.0, 1.0, 0.01)
            snsylim = (-1.0, 1.0)
        elif idxname.upper() == "SR":
            bins = np.arange(0, 10.0, 0.01)
            snsylim = (0, 10.0)
        # plot hexbin of spectral index against range to observe any range
        # dependence.
        with sns.axes_style("white"):
            jointgrid = sns.jointplot(dualpoints[:, cind['range']].squeeze(), \
                              sindex.squeeze(), kind="hex", size=11, \
                              ylim=snsylim, xlim=(0, 60), \
                              marginal_kws={"norm_hist":True, \
                                                "hist_kws":{"weights":ptsweights}}, \
                              joint_kws={"C":ptsweights, \
                                             "reduce_C_function":np.sum});
            jointgrid.set_axis_labels("range", idxname.upper())
            plt.savefig(infile[:-4]+"_hexbin_range_vs_"+idxname.lower()+".png")

        # plot cumulative curve and find the minimum of second
        # derivative. This follows Xiaoyuan's method to classify points with
        # pulse shapes.
        histfig = plt.figure()
        ax = plt.subplot(111)
        sindexhist = plt.hist(sindex, bins, normed=True, label="Cumulative histogram", \
                                  edgecolor='None', weights=ptsweights, cumulative=True)
        sindexfreq = sindexhist[0]
        bins = sindexhist[1]
        bins = (bins[:-1] + bins[1:])/2.0
        # find the 5% and 95% percentile
        interpfunc = sp.interpolate.interp1d(sindexfreq, bins)
        lpercentile = interpfunc(0.05)
        rpercentile = interpfunc(0.95)
        lpercentile = np.asscalar(lpercentile)
        rpercentile = np.asscalar(rpercentile)
        # calculate second derivative
        # first smooth the cumulative curve
        smwidth = 5
        smwindow = np.ones(smwidth)/float(smwidth)
        tmppad = np.hstack((np.ones(smwidth/2)*np.mean(sindexfreq[0:smwidth]), \
                      sindexfreq, \
                      np.ones(smwidth/2)*np.mean(sindexfreq[-1*smwidth:-1])))
        smsindexfreq = np.convolve(tmppad, smwindow, 'same')
        smsindexfreq = smsindexfreq[(smwidth/2):-1*(smwidth/2)]

        padbins = np.hstack((bins, bins[-1]+bins[1]-bins[0], \
                                 bins[-1]+2*(bins[1]-bins[0])))
        padsmsindexfreq = np.hstack((smsindexfreq, smsindexfreq[-1], smsindexfreq[-1]))
        deriv1d = np.diff(padsmsindexfreq)/np.diff(padbins)
        deriv2d = np.diff(deriv1d)/np.diff(padbins[:-1])
        mind2ind = np.argmin(deriv2d)
        mind2pos = bins[mind2ind]
        # draw a line
        plt.plot([mind2pos, mind2pos], ax.get_ylim(), 'k-')
        ax.annotate("min. 2nd derivative: {0:.3f}".format(mind2pos), \
                        xy=(mind2pos, sindexfreq[mind2ind]), \
                        xytext=(mind2pos, sindexfreq[mind2ind]))
        plt.title("Cumulative histogram of "+idxname.upper()+" from apparent reflectance")
        plt.xlabel(idxname.upper())
        plt.ylabel("Cumulative normalized frequency")
        plt.legend(prop={'size':8}, loc='best')
        plt.savefig(infile[:-4]+"_"+idxname.upper()+"_cumuhist.png")
        plt.close(histfig)

        histfig = plt.figure()
        ax = plt.subplot(111)
        sindexhist = plt.hist(sindex, bins, normed=True, label="Histogram", \
                                  edgecolor='None', weights=ptsweights)
        sindexfreq = sindexhist[0]
        bins = sindexhist[1]
        bins = (bins[:-1] + bins[1:])/2.0

        # draw a line
        plt.plot([mind2pos, mind2pos], ax.get_ylim(), 'k-')
        ax.annotate("min. 2nd derivative: {0:.3f}".format(mind2pos), \
                        xy=(mind2pos, sindexfreq[mind2ind]), \
                        xytext=(mind2pos, sindexfreq[mind2ind]))

        plt.title("Histogram of "+idxname.upper()+" from apparent reflectance")
        plt.xlabel(idxname.upper())
        plt.ylabel("Normalized frequency")

        # simply fit a curve of two-Gaussians to the probability density
        tmpind = np.argmax(sindexfreq)
        tmpind2 = tmpind - 10
        p0 = [sindexfreq[tmpind], bins[tmpind], 10*(bins[1]-bins[0]), \
                  sindexfreq[tmpind2], bins[tmpind2], 10*(bins[1]-bins[0])]
        try:
            gpars, gvars = spopt.curve_fit(gauss2, bins, sindexfreq, p0=p0)
        except RuntimeError:
            print "Gaussian fitting to histogram failed! No estimate " \
                + "threshold to classify points."
            plt.legend(prop={'size':8}, loc='best')
            plt.savefig(infile[:-4]+"_"+idxname.upper()+"_hist.png")
            plt.close(histfig)
            y = np.zeros_like(bins)
            estthresh = np.nan
        else:
            # plot the curve
            print "Gaussian fitting to histogram has returned an estimate!"
            y = gauss2(bins, *gpars)
            y1 = gpars[0] * np.exp( -(bins-gpars[1])**2/(2.0*gpars[2]**2) )
            y2 = gpars[3] * np.exp( -(bins-gpars[4])**2/(2.0*gpars[5]**2) )
            plt.plot(bins, y, '-r', label="Fitted probability density")
            plt.plot(bins, y1, '--r', label="Decomposed component")
            plt.plot(bins, y2, '--r', label="Decomposed component")
            plt.legend(prop={'size':8}, loc='best')
            plt.savefig(infile[:-4]+"_"+idxname.upper()+"_hist.png")
            plt.close(histfig)
            # solve the intersection of the two Gaussians
            func = lambda x: gpars[0] * np.exp( -(x-gpars[1])**2/(2.0*gpars[2]**2) ) - \
                gpars[3] * np.exp( -(x-gpars[4])**2/(2.0*gpars[5]**2) )
            estthresh = spopt.fsolve(func, (gpars[1]+gpars[4])/2.0)
            estthresh = estthresh[0]
            print "Estimate index threshold from data: "+"{0:.3f}".format(estthresh)
        finally:
            # write histogram and fitted pdf to a file if Gaussian fitting
            # failed, then the column for fitting is all zeros.
            tmpout = np.hstack(( bins.reshape(len(bins), 1), \
                                     sindexfreq.reshape(len(sindexfreq), 1), \
                                     y.reshape(len(y), 1)))
            headerstr = "Histogram of "+idxname.upper()+"\n"+ \
                "Input dual-wavelength point cloud: "+infile+"\n"+ \
                "Run made at: "+time.strftime("%c")+"\n"+ \
                "Estimate threshold from fitted histogram curve = "+ \
                "{0:.3f}".format(estthresh)+"\n"+ \
                "5% percentile = {0:.3f}\n".format(lpercentile) + \
                "95% percentile = {0:.3f}\n".format(rpercentile) + \
                "bin_center,hist_data,hist_fit"
            np.savetxt(infile[:-4]+"_"+idxname.upper()+"_hist.txt", tmpout, \
                           delimiter=',', header=headerstr.rstrip(), \
                           fmt="%.3f")

    return ()

def main(cmdargs):
    """
    Take inputs from command line and pass the inputs to the classifier chosen
    by user.
    """
    # get inputs from command line or defaults
    infile = cmdargs.infile
    outfile = cmdargs.outfile
    idxname = cmdargs.index
    verbose = cmdargs.verbose
    # clip apparent reflectance > 1 to one?
    clipI = cmdargs.clipI
    thresh = cmdargs.thresh
    rbreak = cmdargs.rbreak

    print "Input file: "+infile
    print "Output file: "+outfile
    print "Index for thresholding: "+idxname.upper()
    print "Break points of range divisions: "+", ".join(["{0:.3f}".format(r) for r in rbreak])
    print "Index threshold at each range division: "+", ".join(["{0:.3f}".format(t) for t in thresh])
    print "Clip apparent reflectance to one? " + ("Yes" if clipI else "No")
    print "Save intermediate files and figures? " + ("Yes" if verbose else "No")

    dwel_points_class_index(infile, outfile, idxname, rbreak, thresh, clipI, verbose)

def getCmdArgs():
    p = argparse.ArgumentParser(description=("Classify dual-wavelength points with spectral index thresholding"))

    p.add_argument("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt", help="Input dual-wavelength point cloud file")
    p.add_argument("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_class.txt", help="Output classified point cloud file")

    # p.add_argument("-i", "--input", dest="infile", default=None, help="Input dual-wavelength point cloud file")
    # p.add_argument("-o", "--output", dest="outfile", default=None, help="Output classified point cloud file")

    p.add_argument("-x", "--index", dest="index", default="NDI", help="Name of spectral index for thresholding, NDI, SR")
    p.add_argument("--rbreak", dest="rbreak", type=float, default=None, nargs='+', metavar=("rbreak_1", "rbreak_2"), help="Breakpoints along range for piecewise thresholding. Range division is: [minimum_range, rbreak1), [rbreak1, rbreak2) ... If none, threshoding on the whole range. Default: none")
    p.add_argument("--thresh", dest="thresh", type=float, default=None, nargs='+', metavar=("thresh_1", "thresh_2"), help="Spectral index threshold for each range division. NOTE: N+1 thresh for N rbreak. thresh_1 for [minimum_range, rbreak1), thresh_2 for [rbreak1, rbreak2) ... thresh_{n+1} for [rbreak_n, maximum_range)")

    p.add_argument("-c", "--clipI", dest="clipI", default=False, action="store_true", help="Clip apparent reflectance values greater than 1 to one. Default: false (no clip)")
    p.add_argument("-v", "--verbose", dest="verbose", default=False, action="store_true", help="Verbose. Save intermediate files and figures. Default: false.")

    cmdargs = p.parse_args()
    if (cmdargs.infile is None) | (cmdargs.outfile is None):
        p.print_help()
        print "Both input and output file names are required."
        sys.exit()

    if cmdargs.thresh is None:
        p.print_help()
        print("thresh must be set.")
        sys.exit()
    if cmdargs.rbreak is None:
        nrbreak = 0
    else:
        nrbreak = len(cmdargs.rbreak)
    if len(cmdargs.thresh)-nrbreak != 1:
        p.print_help()
        print("Number of thresh arguments must only be ONE larger than number of rbreak argument")
        sys.exit()

    return cmdargs

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
