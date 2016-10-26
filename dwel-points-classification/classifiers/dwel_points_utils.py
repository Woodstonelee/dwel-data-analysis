import sys
import warnings

import numpy as np

import canupo

_dwel_points_ascii_scheme = {'x':0, 'y':1, 'z':2, 'd_I_nir':3, 'd_I_swir':4, \
                             'return_number':5, 'number_of_returns':6, 'shot_number':7, \
                             'range':8, 'theta':9, 'phi':10, 'sample':11, 'line':12, \
                             'd0_nir':13, 'd0_swir':14, 'qa':15, 'grd_label':19, \
                             'skip_header':3}

def loadPoints(inptsfile, usecols=['x', 'y', 'z', \
                                   'd_I_nir', 'd_I_swir', 'range']):
    """
    Read data from input file and prep data for clustering
    """

    ind = [_dwel_points_ascii_scheme[uc] for uc in usecols]
    
    # ind = (_dwel_points_ascii_scheme['d_I_nir'], \
    #        _dwel_points_ascii_scheme['d_I_swir'], \
    #        _dwel_points_ascii_scheme['range'], \
    #        _dwel_points_ascii_scheme['d0_nir'], \
    #        _dwel_points_ascii_scheme['d0_swir'])

    data = np.genfromtxt(inptsfile, usecols=ind, comments=None, delimiter=',', \
                          skip_header=_dwel_points_ascii_scheme['skip_header'])

    return data

def openMSC(mscfile):
    """
    Open an MSC file and set up some attributes for the class
    """
    return MSCFile(mscfile)


class MSCFile:
    def __init__(self, mscfile):
        self.mscfile = mscfile
        self._mscfobj = canupo.MSCFile(mscfile)
        self.header = self._mscfobj.get_header()
        self.next_pt_idx = 0

    def read(self, npts=None, start=None, use_scales=None):
        """Read data from MSC file, one batch at one time, number of points
        to read on every call, self.birch.pf_npts

        Parameters: **npts**, *int*

        Returns: **mscdata**, *2D numpy array*
                   (npts, nscales*2+1), *npts* is the number of points
                   being read out, either given by the parameter
                   *npts* or all the points in the MSC file; *nscales*
                   is the number of scales being read out, either
                   given by the paramter *use_scales* or all the
                   scales in the MSC file. Each scale has two values,
                   *a* as the 1D component and *b* as the 2D
                   component. The first *nscales* columns are *a* and
                   the second *nscales* columns are *b*. The extra
                   last column is the line number of each point in its
                   original ASCII point cloud that has generated this
                   MSC file.
        """
        mscheader = self.header

        if npts is None:
            npts = mscheader[0]
        
        nscales = len(mscheader[1])        
        # ncols = 2*nscales + 1
        tmp = mscheader[0] - self._mscfobj.next_pt_idx
        if tmp < npts:
            npts = tmp

        if use_scales is None:
            use_scales = np.arange(nscales)
        else:
            if np.any(use_scales >= nscales):
                sys.stderr.write("Indices to scales out of bound, {0:d} scales in input MSC\n".format(nscales))
                return None
            if np.any(use_scales < 0):
                sys.stderr.write("Indices to scales out of bound, negative indices found")
                return None

        n_use_scales = len(use_scales)
        mscdata = np.zeros((int(npts), int(2*n_use_scales+1)))

        if start is None:
            start = self.next_pt_idx            
            
        tmp = self._mscfobj.read_point(npts, start)
        mscdata[:, 0:n_use_scales] = np.array(tmp[1]).reshape(npts, nscales)[:, use_scales]
        mscdata[:, n_use_scales:2*n_use_scales] = np.array(tmp[2]).reshape(npts, nscales)[:, use_scales]
        mscdata[:, -1] = np.array(tmp[0]).reshape(npts, mscheader[-1])[:, -1]

        self.next_pt_idx = self._mscfobj.next_pt_idx
        return mscdata

    def close(self):
        del self._mscfobj
