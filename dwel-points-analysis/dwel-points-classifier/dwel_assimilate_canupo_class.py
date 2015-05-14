#!/usr/bin/env python

import sys
import os
import argparse
import time

import numpy as np

def getCmdArgs():
    p = argparse.ArgumentParser(description='Assimilate classification of merged mix class using structure information with CANUPO alogrithm and generate a binary classification of a whole point cloud')

    p.add_argument('-m', '--mixclass', dest='mixclass', nargs='+', default=['/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_0.txt', '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_-2.txt'], help='One or multiple ASCII point cloud file of mix class')
    p.add_argument('-c', '--canupo', dest='canupo', nargs='+', default=['/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_0_canupo.txt', '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_-2_canupo.txt'], help='One or multiple ASCII point cloud file of CANUPO classification of mix class. Same number of files as files of mix class and same sequence of files')
    p.add_argument('-p', '--pureclasses', dest='pureclasses', nargs='+', default=['/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_-1.txt', '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_1.txt', '/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_class_2.txt'], help='One or multiple ASCII point cloud files of classes from labeled pure classes')
    p.add_argument('-o', '--outfile',dest='outfile', default='/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140421/spectral-points-by-union/HFHD20140421-dual-points-clustering/merging/HFHD_20140421_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt', help='Output ASCII point cloud file of classification by assimilating CANUPO classification to clustering classification')

    p.add_argument("--ncols", dest="ncols", type=int, default=1022, help="Number of columns (samples) in the AT projection where points are generated. [default: 1022]")
    p.add_argument("--nrows", dest="nrows", type=int, default=3142, help="Number of rows (lines) in the AT projection where points are generated. [default: 3142]")
    
    p.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Turn on verbosity')

    cmdargs = p.parse_args()

    if (cmdargs.mixclass is None) or (cmdargs.canupo is None) or (cmdargs.outfile is None):
        p.print_help()
        print "Mix class, CANUPO classification and output file are required"
        sys.exit()

    if (len(cmdargs.mixclass) != len(cmdargs.canupo)):
        p.print_help()
        print "Number of files of mix class must be the same as number of files of canupo classification."
        sys.exit()

    return cmdargs

class MergeMixPure:
    def __init__(self, nrows=3142, ncols=1022, verbose=False):
        
        self.canupocind = {'x':0, 'y':1, 'z':2, 'return_number':3, 'shot_number':4, 'class':5, 'confidence':6}
        self.cind = {'x':0,'y':1,'z':2,'d_I_nir':3,'d_I_swir':4,'return_number':5,'number_of_returns':6,'shot_number':7,'range':8,'theta':9,'phi':10,'sample':11,'line':12,'fwhm_nir':13,'fwhm_swir':14,'qa':15,'r':16,'g':17,'b':18,'ndi':19,'clabel':20,'class':21}

        self.nrows = nrows
        self.ncols = ncols
        self.verbose = verbose

    def assignCanupoClass(self, mixclsfile, canupoclsfile):
        """
        Assign CANUPO class label in canupoclsfile to corresponding point in
        mixclsfile.

        Returns:

            mixpoints (2D numpy array, float): one row is a point with two columns
            attached to columns in mixclassfile, CANUPO class and class label.
        """
        canupocind = self.canupocind
        cind = self.cind

        print "Reading mix point cloud from " + mixclsfile
        mixpoints = np.loadtxt(mixclsfile, skiprows=3, delimiter=',', comments=None)

        canupopoints = np.loadtxt(canupoclsfile, skiprows=1, delimiter=',', comments=None, usecols=(canupocind['return_number'], canupocind['shot_number'], canupocind['class']))

        # data check
        if mixpoints.shape[0] != canupopoints.shape[0]:
            raise RuntimeError( \
                ( \
                    'Mix point cloud and CANUPO point cloud have different numbers of points. Check your data!\n'+ \
                    'Mix point cloud file: {0:s}\n'+ \
                    'CANUPO point cloud file: {1:s}').format(mixclsfile, canupoclsfile))


        max_shot_number = max( np.max(canupopoints[:, 1]), np.max(mixpoints[:, cind['shot_number']]) )
        max_return_number = max( np.max(canupopoints[:, 0]), np.max(mixpoints[:, cind['return_number']]) )
        canupoind = (canupopoints[:, 0].astype(int)-1)*max_shot_number + canupopoints[:, 1].astype(int)-1
        mixind = (mixpoints[:, cind['return_number']].astype(int)-1)*max_shot_number + mixpoints[:, cind['shot_number']].astype(int)-1

        commonpoints = np.intersect1d(canupoind, mixind)
        # data check
        if (commonpoints.size != canupoind.size) or (commonpoints.size != mixind.size):
            raise RuntimeError( \
                ( \
                    'Mix point cloud and CANUPO point cloud have different points while they are expected to have the same points. Check your data!\n'+ \
                    'Mix point cloud file: {0:s}\n'+ \
                    'CANUPO point cloud file: {1:s}').format(mixclsfile, canupoclsfile))

        mixsortind = np.argsort(mixind)
        canuposortind = np.argsort(canupoind)
        mixpoints = np.hstack((mixpoints[mixsortind, :], canupopoints[canuposortind, 2:3], canupopoints[canuposortind, 2:3]))

        return mixpoints

    def getCanupoClass(self, mixclsfiles, canupoclsfiles):
        mixpointslist = [ self.assignCanupoClass(mf, cf) for mf, cf in zip(mixclsfiles, canupoclsfiles) ]
        mixpoints = np.vstack(tuple(mixpointslist))
        return mixpoints

    def getPureClass(self, pureclsfiles):
        cind = self.cind
        # read point clouds of pure classes
        purepointslist = [ np.loadtxt(f, skiprows=3, delimiter=',', comments=None) for f in list(pureclsfiles) ]
        purepoints = np.vstack(tuple(purepointslist))
        npure = purepoints.shape[0]
        purepoints = np.hstack((purepoints, np.zeros((npure, 1)), purepoints[:, cind['class']:cind['class']+1]))
        return purepoints

    def mergeCanupoMixPure(self, mixpoints, purepoints, outfile):
        cind = self.cind
        outpoints = np.vstack((mixpoints, purepoints))
        # # sort points
        # outind = np.zeros((outpoints.shape[0], 3), dtype=np.int)
        # outind[:, 0] = outpoints[:, cind['sample']]
        # outind[:, 1] = outpoints[:, cind['line']]
        # outind[:, 2] = outpoints[:, cind['return_number']]
        # outindview = outind.view([('sample', outind.dtype), ('line', outind.dtype), ('return_number', outind.dtype)])
        # sortind = np.argsort(outindview, order=('sample', 'line', 'return_number'), axis=0).squeeze()
        # outpoints = outpoints[sortind, :]

        # sort points AND check the number of returns and return numbers for
        # each pulse and correct them if necessary
        sortind, num_of_returns, return_num, shotind = \
            self.updateReturnNum(outpoints[:, [cind['range'], cind['sample'], cind['line']]].copy())
        outpoints = outpoints[sortind, :]
        outpoints[:, cind['return_number']] = return_num
        outpoints[:, cind['number_of_returns']] = num_of_returns
        outpoints[:, cind['shot_number']] = shotind

        # write points
        print "Writing merged points to " + outfile
        headerstr = "[DWEL Dual-wavelength Point Cloud Data by Union][Clustering by KMeans][Cluster merge by visual inspection][Mix reclassified by CANUPO][-1=gap, 1=wood, 2=leaf]\n"
        headerstr += "Run made at: " + time.strftime("%c") + "\n"
        headerstr += "x,y,z,d_I_nir,d_I_swir,return_number,number_of_returns,shot_number,range,theta,phi,sample,line,fwhm_nir,fwhm_swir,qa,r,g,b,ndi,clabel,cluster_class,canupo_class,class"
        fmtstr = '%.3f '*5 + '%d '*3 + '%.3f '*3 + '%d '*2 + '%.3f '*2 + '%d '*4 + \
            '%.3f ' + '%d '*4
        fmtstr = fmtstr.strip().split(' ')
        np.savetxt(outfile, outpoints, delimiter=',', fmt=fmtstr, header=headerstr.rstrip(), comments='')

    def updateReturnNum(self, points):
        """
        Count the number of returns and update return number of each point
        according to the shot location (line, column) and range.

        Args:

            points (2D numpy array, float): [npts, 3], range, sample, line

        Returns:

            sortind (1D numpy array, int): indices that will sort the shot indices.

            num_of_returns (1D numpy array, int)

            return_num (1D numpy array, int)

            shotind (1D numpy array, int)
        """
        shotind = (points[:, 1:2]-1)*self.nrows + points[:, 2:3]
        tmppts = np.hstack((shotind, points[:, 0:1]))
        ptsview = tmppts.view(dtype=np.dtype([('shotind', tmppts.dtype), ('range', tmppts.dtype)]))
        sortind = np.argsort(ptsview, order=('shotind', 'range'), axis=0).squeeze()
        ptsview = ptsview[sortind]

        ushotind, uinvind, ucount = np.unique(shotind.squeeze(), return_inverse=True, return_counts=True)
        num_of_returns = ucount[uinvind][sortind]
        return_num = np.zeros(len(ptsview), dtype=int)
        i = 0
        while i<len(ptsview):
            tmpcount = num_of_returns[i]
            return_num[i:i+tmpcount] = np.arange(tmpcount, dtype=int)+1
            i += tmpcount
        tmpflag = np.less(ptsview['range'], 1e-10).squeeze()
        num_of_returns[tmpflag] = 0
        return_num[tmpflag] = 0

        return sortind, num_of_returns, return_num, shotind.squeeze()[sortind]


def main(cmdargs):
    mixclsfiles = cmdargs.mixclass
    canupoclsfiles = cmdargs.canupo
    pureclsfiles = cmdargs.pureclasses
    outfile = cmdargs.outfile

    nrows = cmdargs.nrows
    ncols = cmdargs.ncols
    
    verbose = cmdargs.verbose

    mergeobj = MergeMixPure(nrows=nrows, ncols=ncols, verbose=verbose)
    mixpoints = mergeobj.getCanupoClass(mixclsfiles, canupoclsfiles)
    purepoints = mergeobj.getPureClass(pureclsfiles)
    mergeobj.mergeCanupoMixPure(mixpoints, purepoints, outfile)


if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
