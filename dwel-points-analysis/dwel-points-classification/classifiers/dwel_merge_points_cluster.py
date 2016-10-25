#!/usr/bin/env python

import sys
import os
import argparse
import time

import numpy as np

def getCmdArgs():
    p = argparse.ArgumentParser(description="Merge clusters to classes according to class assignment to clusters from visual inspection")

    p.add_argument('-i', '--inprefix', dest='inprefix', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_', help='Prefix of input point cluster files. Be sure to include full path in the prefix string, with underscore in the end')
    p.add_argument('--ndigits', dest='ndigits', type=int, default=2, help='Number of digits of cluster number in the file names of clusters')
    p.add_argument('--csv', dest='csv', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_merging.csv', help='CSV file giving the class assignment to clusters')
    p.add_argument('-o', '--outprefix', dest='outprefix', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_test_', help='Prefix of output merged point cloud of classes, with underscore in the end')

    p.add_argument('-t', '--thresh', dest='thresh', type=float, default=None, help="Clean point cloud by removing points with apparent reflectance at both wavelengths less than this threshold")

    p.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Turn on verbosity')

    cmdargs = p.parse_args()

    if (cmdargs.inprefix is None) or (cmdargs.outprefix is None) or (cmdargs.csv is None):
        p.print_help()
        print "Input and output prefix strings, and csv file of class assignment to clusters are required"
        sys.exit()

    return cmdargs

def mergeClusters(inprefix, clscsv, outprefix, ndigits=2, thresh=None, verbose=False):
    """
    Merge clusters according to class assignment to clusters.
    """
    if thresh is not None:
        print "Threshold of apparent reflectance to clean the point cloud = {0:.3f}".format(thresh)
        thresh = thresh*1e3 # conver to unit of 1e3
    cind = {'x':0, 'y':1, 'z':2, \
                'd_i_nir':3, 'd_i_swir':4, \
                'number_of_returns':6, 'sample':11, 'line':12, \
                'shot_number':7, 'theta':9, 'phi':10, \
                'ndi':19, 'clabel':20}

    class_names = {2:'leaf', 1:'wood', 0:'mix', -1:'gap', -2:'unsure'}
    cluster2class = np.loadtxt(clscsv, dtype=np.int, skiprows=2, usecols=(0, 1), delimiter=',', comments=None)

    ptsclass = np.unique(cluster2class[:, 1])
    cl_max = np.max(ptsclass)
    outnamefmtstr = "{0:0>"+str(len(str(cl_max)))+"d}.txt"
    outfobjs = {cl : open(outprefix+outnamefmtstr.format(cl), 'w') for cl in ptsclass}

    innamefmtstr = "{0:0>"+str(ndigits)+"d}.txt"
    # get header string
    headerstr = ""
    noiseheaderstr = ""
    with open(inprefix+innamefmtstr.format(cluster2class[0, 0]), 'r') as infobj:
        tmpline = infobj.readline()
        headerstr += tmpline.rstrip('\n')+"[{0:d}={1:s} from cluster merge by visual inspection]\n"
        noiseheaderstr += tmpline.rstrip('\n')+"[noise points from cluster merge by threshold of rho_app = {0:.3f}]\n"
        infobj.readline()
        headerstr += "Run made at: "+time.strftime("%c")+"\n"
        noiseheaderstr += "Run made at: "+time.strftime("%c")+"\n"
        tmpline = infobj.readline()
        headerstr += tmpline.rstrip('\n')+",class\n"
        noiseheaderstr += tmpline.rstrip('\n')+",class\n"
    junk = [ outfobjs[cls].write(headerstr.format(cls, class_names[cls])) for cls in ptsclass ]
    nclusters = cluster2class.shape[0]

    # write noise data if threshold is given and verbose mode is on
    if (thresh is not None) and verbose:
        outnoisefname = outprefix+'noise.txt'
        sys.stdout.write("Writing noise points to: \n{0:s}\n".format(outnoisefname))
        outnoisefobj = open(outnoisefname, 'w')
        outnoisefobj.write(noiseheaderstr.format(thresh))
    for n, cl in enumerate(cluster2class[:, 0]):
        if verbose:
            sys.stdout.write("Merging cluster file {0:d} / {1:d}      \r".format(n+1, nclusters))
            sys.stdout.flush()
        with open(inprefix+innamefmtstr.format(cl), 'r') as infobj:
            sampleind = 0
            lineind = 0
            for i, line in enumerate(infobj):
                if i>2:
                    if thresh is None:
                        outline = line.rstrip('\n')+",{0:d}\n".format(cluster2class[n, 1])
                        outfobjs[cluster2class[n, 1]].write(outline)
                    else:
                        linetokens = line.rstrip('\r\n').split(',')
                        if (int(linetokens[cind['sample']]) != sampleind) or (int(linetokens[cind['line']]) != lineind):
                            sampleind = int(linetokens[cind['sample']])
                            lineind = int(linetokens[cind['line']])
                            remain_nhits = int(linetokens[cind['number_of_returns']])

                        if (int(linetokens[cind['number_of_returns']]) == 0):
                            outline = line.rstrip('\n')+",{0:d}\n".format(cluster2class[n, 1])
                            outfobjs[cluster2class[n, 1]].write(outline)
                        else:
                            if (float(linetokens[cind['d_i_nir']]) > thresh) \
                                     or (float(linetokens[cind['d_i_swir']]) > thresh):
                                outline = line.rstrip('\n')+",{0:d}\n".format(cluster2class[n, 1])
                                outfobjs[cluster2class[n, 1]].write(outline)
                            else:
                                # if this point is a single return from a pulse,
                                # when we remove this point, we add a no-hit
                                # point record (gap class, -1) to the point
                                # cloud for no-hit pulse for Pgap calculation
                                # later.
                                remain_nhits -= 1
                                if (remain_nhits==0):
                                    newlinetokens = ['0' for n in range(len(linetokens))]
                                    newlinetokens[cind['shot_number']] = linetokens[cind['shot_number']]
                                    newlinetokens[cind['theta']] = linetokens[cind['theta']]
                                    newlinetokens[cind['phi']] = linetokens[cind['phi']]
                                    newlinetokens[cind['sample']] = linetokens[cind['sample']]
                                    newlinetokens[cind['line']] = linetokens[cind['line']]
                                    newlinetokens[cind['ndi']] = linetokens[cind['ndi']]
                                    newlinetokens[cind['clabel']] = linetokens[cind['clabel']]
                                    outline = ",".join(newlinetokens)+",{0:d}\n".format(-1)
                                    outfobjs[-1].write(outline)
                                if verbose:
                                    outline = line.rstrip('\n')+",{0:d}\n".format(cluster2class[n, 1])
                                    outnoisefobj.write(outline)

    junk = [ fobj.close() for fobj in outfobjs.values() ]
    if (thresh is not None) and verbose:
        outnoisefobj.close()

def main(cmdargs):
    inprefix = cmdargs.inprefix
    clscsv = cmdargs.csv
    outprefix = cmdargs.outprefix
    ndigits = cmdargs.ndigits
    verbose = cmdargs.verbose

    thresh = cmdargs.thresh

    mergeClusters(inprefix, clscsv, outprefix, ndigits, thresh=thresh, verbose=verbose)

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
