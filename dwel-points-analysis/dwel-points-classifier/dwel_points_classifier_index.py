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
import optparse

import numpy as np
import scipy.stats as spstats
import scipy.optimize as spopt
from sklearn import mixture
from sklearn.preprocessing import StandardScaler

import matplotlib as mpl
# mpl.use('TkAgg') # for interactive plotting
mpl.use('Agg') # for non-interactive plotting running in batch job
import matplotlib.pyplot as plt
from matplotlib import gridspec

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

def dwel_points_class_index(infile, outfile, idxname, thresh=None, \
                                clipI=True, verbose=True):
    """
    Classify points with dual-wavelength intensities by simple NDI thresholding

    Args:

        dualpoints (2D numpy array, [npts, 6]): each row,
        [d_I_nir, d_I_swir]

        par (list of floats): threshold of NDI. If none, a threshold will be
        automatically determined from the histogram of the NDI values.

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
    cind = {'x':0, 'y':1, 'z':2, 'd_I_nir':3, 'd_I_swir':4, 'shot_number':5, \
                'range':6, 'theta':7, 'phi':8, 'sample':9, 'line':10, \
                'fwhm_nir':11, 'fwhm_swir':12, 'multi_return':13}
    # scale of apparent reflectance
    i_scale = 1000.0

    print "Loading points"
    dualpoints = np.loadtxt(infile, dtype=np.float32, delimiter=',')

    if clipI:
        flag = np.greater(dualpoints[:, cind['d_I_nir']], 1*i_scale)
        dualpoints[flag, cind['d_I_nir']:cind['d_I_nir']+1] = 1*i_scale
        flag = np.greater(dualpoints[:, cind['d_I_swir']], 1*i_scale)
        dualpoints[flag, cind['d_I_swir']:cind['d_I_swir']+1] = 1*i_scale

    if verbose:
        # plot NIR and SWIR intensities on a scatter plot

        # # super slow not doable
        # # plot scatter points colored by the density of their points
        # xy = np.vstack([dualpoints[:, cind['d_I_nir']].squeeze(), \
        #                     dualpoints[:, cind['d_I_swir']].squeeze()])
        # z = spstats.gaussian_kde(xy)(xy)
        # sctfig, ax = plt.subplots()
        # ax.scatter(dualpoints[:, cind['d_I_nir']], \
        #              dualpoints[:, cind['d_I_swir']], \
        #              c=z, edgecolor="")
        # plt.show()
        nirplotrange = [-0.2*i_scale, 2*i_scale]
        swirplotrange = [-0.2*i_scale, 1.5*i_scale]

        # plot points with hexbin to see the density of points, much faster!
        hexbinfig = plt.figure(figsize=(11, 7.5))
        gs = gridspec.GridSpec(4, 4)
        gs.update(left=0.02, right=0.87)
        gs2 = gridspec.GridSpec(4, 1)
        gs2.update(left=0.88, right=0.98)

        axHexbin = plt.subplot(gs[0:3, 1:4])
        hb = plt.hexbin(dualpoints[:, cind['d_I_nir']], \
                      dualpoints[:, cind['d_I_swir']], \
                            extent=[nirplotrange[0], nirplotrange[1], \
                                        swirplotrange[0], nirplotrange[1]], \
                            mincnt=1)
        # plt.xlim(axHistNir.get_xlim())
        # plt.ylim(axHistSwir.get_ylim())
        plt.axis('equal')
        #plt.autoscale(tight=True)
        plt.title("Scatter plot with colored density"+ \
                      r" between NIR and SWIR $\rho_{app}$")
        axcb = plt.subplot(gs2[0:3, :])
        cb = plt.colorbar(hb, cax=axcb)
        cb.set_label("point counts")

        # plot histogram of NIR and SWIR separately
        axHistNir = plt.subplot(gs[3, 1:4], sharex=axHexbin)
        # bins = np.arange(np.nanmin(dualpoints[:, cind['d_I_nir']]), \
        #                      np.nanmax(dualpoints[:, cind['d_I_nir']]), \
        #                      0.01*i_scale)
        bins = np.arange(nirplotrange[0], nirplotrange[1], 0.01*i_scale)
        plt.hist(dualpoints[:, cind['d_I_nir']], bins, normed=True, \
                     label="NIR histogram", edgecolor='None')
        #axHistNir.set_xlim( axHexbin.get_xlim() )
        plt.xlabel(r"NIR $\rho_{app}$*"+"{0:g}".format(i_scale))
        axHistSwir = plt.subplot(gs[0:3, 0], sharey=axHexbin)
        # bins = np.arange(np.nanmin(dualpoints[:, cind['d_I_swir']]), \
        #                      np.nanmax(dualpoints[:, cind['d_I_swir']]), \
        #                      0.01*i_scale)
        bins = np.arange(swirplotrange[0], swirplotrange[1], 0.01*i_scale)
        plt.hist(dualpoints[:, cind['d_I_swir']], bins, normed=True, \
                     label="SWIR histogram", edgecolor='None', \
                     orientation='horizontal')
        #plt.ylim( axHexbin.get_ylim() )
        plt.ylabel(r"SWIR $\rho_{app}$*"+"{0:g}".format(i_scale))

        gs.tight_layout(hexbinfig, rect=[0, 0, 0.87, 1])
        gs2.tight_layout(hexbinfig, rect=[0.88, 0.1, 1, 0.9])
        plt.savefig(infile[:-4]+"_hexbin_nir_vs_swir_apprefl.png")
        plt.close(hexbinfig)

    if idxname.upper() == "NDI":
        sindex = (dualpoints[:, cind['d_I_nir']] - dualpoints[:, cind['d_I_swir']]).astype(float) \
            / (dualpoints[:, cind['d_I_nir']] + dualpoints[:, cind['d_I_swir']]).astype(float)
    elif idxname.upper() == "SR":
        sindex = (dualpoints[:, cind['d_I_nir']]).astype(float) \
            / (dualpoints[:, cind['d_I_swir']]).astype(float)
    else:
        # for future use
        return ()

    sindex = sindex.reshape((len(sindex), 1))

    # classification with user given or default threshold
    pointlabel = np.ones_like(sindex, dtype=np.int)
    flag = np.greater_equal(sindex, thresh)
    # leaves: label as 2
    pointlabel[flag] = 2
    # write classification results
    pointlabel = pointlabel.reshape(len(pointlabel), 1)
    sindex = sindex.reshape(len(sindex), 1)
    # generate RGB info
    rgb = np.zeros((len(pointlabel), 3))
    ind = np.where(pointlabel == 1)[0]
    rgb[ind, :]=[255, 0, 0]
    ind = np.where(pointlabel == 2)[0]
    rgb[ind, :]=[0, 255, 0]
    prefixstr = "[DWEL Dual-wavelength Point Cloud Classification " \
        + idxname.upper()+". Label, 1=others, 2=leaves] " \
        + "[Predefined threshold = "+"{0:.3f}".format(thresh)+"]\n" \
        + "Run made at: " + time.strftime("%c")+"\n"
    headerstr = prefixstr + "x,y,z,d_I_nir,d_I_swir,shot_number,range,theta," \
        +"phi,sample,line,fwhm_nir,fwhm_swir,multi-return,sindex,label,R,G,B"
    # write to file
    print "Saving classification by predefined threshold"
    fmtstr = "%.3f "*5 + "%d " + "%.3f "*3 + "%d "*2 + "%.3f "*2 + "%d " \
        + "%.3f " + "%d "*4
    fmtstr = fmtstr.strip().split(" ")
    np.savetxt(outfile[:-4]+"_"+idxname.upper() \
                   + "_thresh_"+"{0:.3f}".format(thresh)+".txt", \
                   np.hstack((dualpoints, sindex, pointlabel, rgb)), \
                   delimiter=',', \
                   fmt=fmtstr, \
                   header=headerstr.rstrip())

    # Not working, cannot fit to the actual histogram
    # # Use 1D Gaussian mixture model of two components to find a threshold
    # print "Fitting 1D Gaussian mixture model of two components to SINDEX values"
    # gmm_sindex = mixture.GMM(n_components=2, init_params='c', params='mwc', \
    #                           n_init=1, n_iter=1000)
    # gmm_sindex.means_ = np.array([[0.55], [0.65]])
    # gmm_sindex.weights_ = np.array([0.3, 0.7])
    # model_sindex = gmm_sindex.fit(sindex)
    # aic_sindex = gmm_sindex.aic(sindex)
    if verbose:
        # plot histogram and estimate a threshold from histogram
        if idxname.upper() == "NDI":
            bins = np.arange(-1.0, 1.0, 0.01)
        elif idxname.upper() == "SR":
            bins = np.arange(0, 10.0, 0.01)
        #bins = np.arange(np.nanmin(sindex), np.nanmax(sindex), 0.01)
        # # get the GMM fitting results.
        # logprob, respon = model_sindex.score_samples(bins)
        # pdf = np.exp(logprob)
        # pdf_isindexvidual = respon * pdf[:, np.newaxis]
        # plotting
        histfig = plt.figure()
        sindexhist = plt.hist(sindex, bins, normed=True, label="Histogram", edgecolor='None')
        sindexfreq = sindexhist[0]
        bins = sindexhist[1]
        bins = (bins[:-1] + bins[1:])/2.0
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
            # classification with estimate threshold from histogram
            pointlabel = np.ones_like(sindex, dtype=np.int)
            flag = np.greater_equal(sindex, estthresh)
            # leavs labeled as 2
            pointlabel[flag] = 2
            # write classification results
            pointlabel = pointlabel.reshape(len(pointlabel), 1)
            sindex = sindex.reshape(len(sindex), 1)
            # generate RGB info
            rgb = np.zeros((len(pointlabel), 3))
            ind = np.where(pointlabel == 1)[0]
            rgb[ind, :]=[255, 0, 0]
            ind = np.where(pointlabel == 2)[0]
            rgb[ind, :]=[0, 255, 0]
            prefixstr = "[DWEL Dual-wavelength Point Cloud Classification " \
                + idxname.upper()+". Label, 1=others, 2=leaves] " \
                + "[Estimate threshold = "+"{0:.3f}".format(estthresh)+"]\n" \
                + "Run made at: " + time.strftime("%c")+"\n"
            headerstr = prefixstr + "x,y,z,d_I_nir,d_I_swir,shot_number,range,theta," \
                +"phi,sample,line,fwhm_nir,fwhm_swir,multi-return,sindex,label,R,G,B"
            # write to file
            print "Saving classification by estimate threshold"
            fmtstr = "%.3f "*5 + "%d " + "%.3f "*3 + "%d "*2 + "%.3f "*2 + "%d " \
                + "%.3f " + "%d "*4
            fmtstr = fmtstr.strip().split(" ")
            np.savetxt(outfile[:-4]+"_"+idxname.upper() \
                           + "_estthresh_"+"{0:.3f}".format(estthresh)+".txt", \
                           np.hstack((dualpoints, sindex, pointlabel, rgb)), \
                           delimiter=',', \
                           fmt=fmtstr, \
                           header=headerstr.rstrip())
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
    # threshold
    thresh = cmdargs.thresh

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

    print "Input file: "+infile
    print "Output file: "+outfile
    print "Index for thresholding: "+idxname.upper()
    print "Index threshold: {0:.3f}".format(thresh)
    print "Clip apparent reflectance to one? " + ("Yes" if clipI else "No")
    print "Save intermediate files and figures? " + ("Yes" if verbose else "No")

    dwel_points_class_index(infile, outfile, idxname, thresh, clipI, verbose)

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()

        # p.add_option("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points.txt", help="Input dual-wavelength point cloud file")
        # p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_class.txt", help="Output classified point cloud file")

        p.add_option("-i", "--input", dest="infile", default=None, help="Input dual-wavelength point cloud file")
        p.add_option("-o", "--output", dest="outfile", default=None, help="Output classified point cloud file")


        p.add_option("-x", "--index", dest="index", default="NDI", help="Name of spectral index for thresholding, NDI, SR")
        p.add_option("-t", "--thresh", dest="thresh", default=None, type="float", help="Spectral index threshold for classification")

        p.add_option("-c", "--clipI", dest="clipI", default=False, action="store_true", help="Clip apparent reflectance values greater than 1 to one. Default: false (no clip)")
        p.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="Verbose. Save intermediate files and figures. Default: false.")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.infile is None) | (self.outfile is None):
            p.print_help()
            print "Both input and output file names are required."
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
