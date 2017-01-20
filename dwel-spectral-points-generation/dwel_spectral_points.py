import sys
import time
import warnings

import numpy as np

from osgeo import gdal
gdal.AllRegister()

class DWELSpectralPoints:
    """
    Methods to generate spectral point cloud from two point clouds at the two
    wavelength from a DWEL scan.

    AUTHORS:

        Zhan Li, zhanli86@bu.edu
    """

    def __init__(self, nirptsfile, swirptsfile, rdiff_thresh, \
                     nrows=3142, ncols=1022, \
                     verbose=False):

        self.nirfile = nirptsfile
        self.swirfile = swirptsfile
        self.rdiff_thresh = rdiff_thresh
        self.nrows = nrows
        self.ncols = ncols

        self.verbose = verbose

        # ------------------------------------------------------------
        # Set some parameters according to your own input point
        # clouds.
        # scale factor of your point intensity
        self.i_scale = 1000.0
        # string to indicate start of a comment line
        self.comments = "//"
        # ind_label lists column name labels that will be read from
        # your point cloud. Convert all the names to LOWER case.
        #
        # You must include ten mandatory columns: x, y, z, d_I, shot_number, range,
        # theta, phi, sample, line.
        # 
        # Mandatory columns MUST be BEFORE optional columns in the
        # following list. 
        self.ind_label = ('x', 'y', 'z', 'd_i', 'shot_number', 'range', \
                          'theta', 'phi', 'sample', 'line', \
                          'd0')
        # ------------------------------------------------------------

        self.headerlines = 0
        self.man_col = 10
        self.tot_col = len(self.ind_label)
        self.arr_dtype = np.float32

    def inferColDataType(self):
        # infer the data type of columns in the ASCII data file
        with open(self.nirfile, 'r') as nirptsfobj:
            for i in range(self.headerlines):
                nirptsfobj.readline()
            line_cnt = 0
            for nir_line in nirptsfobj:
                if nir_line.lstrip().find(self.comments) == 0:
                    continue
                else:
                    line_cnt = line_cnt + 1
                if line_cnt >= 2:
                    nir_col_str = nir_line.split(',')
                    nir_col_dtype = [ self._inferDataType(ncs.strip()) for ncs in nir_col_str ]
                    break

        with open(self.swirfile, 'r') as swirptsfobj:
            for i in range(self.headerlines):
                swirptsfobj.readline()
            line_cnt = 0
            for swir_line in swirptsfobj:
                if swir_line.lstrip().find(self.comments) == 0:
                    continue
                else:
                    line_cnt = line_cnt + 1
                if line_cnt >= 2:
                    swir_col_str = swir_line.split(',')
                    swir_col_dtype = [ self._inferDataType(ncs.strip()) for ncs in swir_col_str ]
                    break

        for ncd, scd in zip(nir_col_dtype, swir_col_dtype):
            if ncd != scd:
                warning_msg = "Detected different data types between NIR and SWIR in the columns of ASCII point cloud files\n" \
                              + "Use detected data types of the columns in NIR ASCII point cloud file"
                warnings.warn(warning_msg, RuntimeWarning)

        testpoints = np.genfromtxt(self.nirfile, \
                                   delimiter=',', skip_header=self.headerlines, \
                                   filling_values=np.nan, usemask=False, \
                                   names=True, case_sensitive="lower", comments=self.comments, \
                                   max_rows=1)
        ind = np.zeros(len(self.ind_label), dtype=int)
        for i, nm in enumerate(self.ind_label):
            ind[i] = np.where(np.in1d(testpoints.dtype.names, nm))[0][0]

        return {nm:nir_col_dtype[i] for nm, i in zip(self.ind_label, ind)}
                

    def _inferDataType(self, num_str):
        num_str = num_str.strip()
        dot_pos = num_str.find('.')
        if dot_pos == -1:
            return "%d"
        else:
            n_sig = len(num_str) - dot_pos - 1
            return "%.{0:d}f".format(n_sig)
                
        
    def generateSpectralPoints(self, outfile, union=False, ndiimgfile=None):
        """
        Main function to generate spectral points
        """

        if union and (ndiimgfile is None):
            raise RuntimeError("You must provdie a gap-filled NDI image to generation spectral points from the union of two point clouds")
        self.union = union
        self.ndiimgfile = ndiimgfile

        # get inputs from command line or defaults
        nirfile = self.nirfile
        swirfile = self.swirfile
        rdiff_thresh = float(self.rdiff_thresh)
        nrows = int(self.nrows)
        ncols = int(self.ncols)

        print "Input NIR point cloud: \n\t"+nirfile
        print "Input SWIR point cloud: \n\t"+swirfile
        print "Output merged point cloud: \n\t"+outfile
        print "Range difference threshold: {0:.3f}".format(rdiff_thresh)
        print "Info for converting sample and line to shot number: \n" \
            + "\tnumber of rows: {0:d}, number of columns: {1:d}".format(nrows, ncols)

        # read points from text file
        print "Loading points"
        nirpoints = np.genfromtxt(nirfile, dtype=self.arr_dtype, usecols=self.ind_label, \
                                  delimiter=',', skip_header=self.headerlines, \
                                  filling_values=np.nan, usemask=False, \
                                  names=True, case_sensitive="lower", comments=self.comments)
        swirpoints = np.genfromtxt(swirfile, dtype=self.arr_dtype, usecols=self.ind_label, \
                                   delimiter=',', skip_header=self.headerlines, \
                                   filling_values=np.nan, usemask=False, \
                                   names=True, case_sensitive="lower", comments=self.comments)
        nirpoints = nirpoints.view(self.arr_dtype).reshape(nirpoints.shape+(-1,))
        swirpoints = swirpoints.view(self.arr_dtype).reshape(swirpoints.shape+(-1,))


        # update column index in loaded array
        cind = { il:i for i, il in enumerate(self.ind_label) }
        
        # index the columns that are used in searching common points
        ind = [cind['range'], cind['sample'], cind['line']]

        print "Generating spectral points ..."
        intersectout = self.intersectPointClouds(nirpoints[:,ind], swirpoints[:,ind])
        nir_ind = intersectout[0]
        swir_ind = intersectout[1]
        return_type = intersectout[2]
        nu_shotnum = intersectout[3]
        num_of_returns = intersectout[4]
        return_num = intersectout[5]

        # return_type now gives QA flag QA flag is a three-bit integer, from MSB
        # to LSB, each bit tells if NDI, NIR or SWIR is measured value (0) or
        # synthetic value (1)
        return_type[:] = int('000', 2)
        # calculate the mean point location
        ind = [cind['x'], cind['y'], cind['z'], cind['shot_number'], cind['range'], cind['theta'], \
                   cind['phi'], cind['sample'], cind['line']]
        nreturn = len(return_type)
        meanpoints = (nirpoints[np.ix_(nir_ind, ind)] + swirpoints[np.ix_(swir_ind, ind)])/2.0
        if self.man_col < self.tot_col:
            outpoints = np.hstack((meanpoints[:, 0:3], \
                                   nirpoints[nir_ind, cind['d_i']:cind['d_i']+1], \
                                   swirpoints[swir_ind, cind['d_i']:cind['d_i']+1], \
                                   return_num.reshape((nreturn, 1)), \
                                   num_of_returns.reshape((nreturn, 1)), \
                                   nu_shotnum.reshape((nreturn, 1)), \
                                   meanpoints[:, 4:9], \
                                   nirpoints[nir_ind, cind[self.ind_label[self.man_col]]:cind[self.ind_label[self.tot_col-1]]+1], \
                                   swirpoints[swir_ind, cind[self.ind_label[self.man_col]]:cind[self.ind_label[self.tot_col-1]]+1], \
                                   return_type.reshape((nreturn, 1)) \
            ))
        else:
            outpoints = np.hstack((meanpoints[:, 0:3], \
                                   nirpoints[nir_ind, cind['d_i']:cind['d_i']+1], \
                                   swirpoints[swir_ind, cind['d_i']:cind['d_i']+1], \
                                   return_num.reshape((nreturn, 1)), \
                                   num_of_returns.reshape((nreturn, 1)), \
                                   nu_shotnum.reshape((nreturn, 1)), \
                                   meanpoints[:, 4:9], \
                                   return_type.reshape((nreturn, 1)) \
            ))            
        
        headerstr = "x,y,z,d_I_nir,d_I_swir,return_number,number_of_returns,shot_number,range,theta,phi,sample,line," \
                    + ",".join([ il+"_nir" for il in self.ind_label[self.man_col:self.tot_col] ]) + "," \
                    + ",".join([ il+"_swir" for il in self.ind_label[self.man_col:self.tot_col] ]) + "," \
                    + "qa,r,g,b\n" \
                    + "{0:s} [DWEL Dual-wavelength Point Cloud Data by {1:s}]\n".format(self.comments, "Union" if self.union else "Intersect") \
                    + "{0:s} Run made at: {1:s} using NIR ({2:s}) + SWIR ({3:s})\n".format(self.comments, time.strftime("%c"), nirfile, swirfile)
        # format string
        if self.man_col < self.tot_col:
            col_dtype = self.inferColDataType()
            fmtstr = "%.3f "*5 + "%d "*3 + "%.3f "*3 + "%d "*2 \
                     + " ".join([ col_dtype[ci] for ci in self.ind_label[self.man_col:self.tot_col] ]) + " " \
                     + " ".join([ col_dtype[ci] for ci in self.ind_label[self.man_col:self.tot_col] ]) + " " \
                     + "%d "*4
        else:
            col_dtype = self.inferColDataType()
            fmtstr = "%.3f "*5 + "%d "*3 + "%.3f "*3 + "%d "*2 \
                     + "%d "*4            
        fmtstr = fmtstr.strip().split(" ")
        
        if not(self.union):
            # spectral points by intersect
            # exclude zero-hit points from rgb generation
            rgbpoints = np.zeros((outpoints.shape[0], 3))
            hitmask = outpoints[:, 6].astype(int) > 0
            # fix extremely large reflectance values
            bound = np.percentile(outpoints[:, 3:5][hitmask, :], 98, axis=0)
            bound[bound<self.i_scale] = self.i_scale
            outpoints[outpoints[:, 3]>bound[0], 3] = bound[0]
            outpoints[outpoints[:, 4]>bound[1], 4] = bound[1]
            # generate pseudo-color composite
            rgbpoints[hitmask, :] = self.colorComposite(np.hstack((outpoints[:, 4:5][hitmask, :], \
                                                           outpoints[:, 3:4][hitmask, :], \
                                                           np.zeros_like(outpoints[:, 3:4][hitmask, :]) \
                                                           )))
            outpoints = np.hstack((outpoints, rgbpoints))

            print "Saving dual-wavelength points: "+str(nir_ind.size)

            np.savetxt(outfile, outpoints, delimiter=',', fmt=fmtstr, \
                header=headerstr.rstrip(), comments='')            

        else:
            # spectral points by union
            nir_unpind = intersectout[6]
            swir_unpind = intersectout[7]
            nir_unp_nu_shotnum = intersectout[8]
            swir_unp_nu_shotnum = intersectout[9]
            ind = [cind['d_i'], cind['sample'], cind['line']]
            print "\tMatching more point pairs between NIR and SWIR for union approach"
            unionout = self.unionPointClouds(nirpoints[np.ix_(nir_unpind, ind)], \
                                                 swirpoints[np.ix_(swir_unpind, ind)], \
                                                 ndiimgfile)
            nir2swir_amp = unionout[0]
            nir2swir_qa = unionout[1]
            swir2nir_amp = unionout[2]
            swir2nir_qa = unionout[3]
            
            tmpflag = np.equal(nir2swir_qa, int('111', 2))
            if np.greater(nirpoints[nir_unpind[tmpflag], cind['d_i']], 1e-10).any():
                warnings.warn("Some no-return shots give non-zero NIR reflectance", RuntimeWarning)
                nirpoints[nir_unpind[tmpflag], cind['d_i']] = 0.0
            tmpflag = np.equal(swir2nir_qa, int('111', 2))
            if np.greater(swirpoints[swir_unpind[tmpflag], cind['d_i']], 1e-10).any():
                warnings.warn("Some no-return shots give non-zero SWIR reflectance", RuntimeWarning)
                swirpoints[swir_unpind[tmpflag], cind['d_i']] = 0.0

            if self.man_col < self.tot_col:
                nir2swir_points = np.hstack(( nirpoints[nir_unpind, 0:3], \
                                              nirpoints[nir_unpind, cind['d_i']:cind['d_i']+1], \
                                              nir2swir_amp.reshape((len(nir2swir_amp), 1)), \
                                              np.zeros((len(nir2swir_amp), 3)), \
                                              nirpoints[nir_unpind, :][:, 5:10], \
                                              nirpoints[nir_unpind, cind[self.ind_label[self.man_col]]:cind[self.ind_label[self.tot_col-1]]+1], \
                                              np.zeros((len(nir2swir_amp), self.tot_col-self.man_col)), \
                                              nir2swir_qa.reshape((len(nir2swir_qa), 1)) \
                ))
                swir2nir_points = np.hstack(( swirpoints[swir_unpind, 0:3], \
                                              swir2nir_amp.reshape((len(swir2nir_amp), 1)), \
                                              swirpoints[swir_unpind, cind['d_i']:cind['d_i']+1], \
                                              np.zeros((len(swir2nir_amp), 3)), \
                                              swirpoints[swir_unpind, :][:, 5:10], \
                                              np.zeros((len(swir2nir_amp), self.tot_col-self.man_col)), \
                                              swirpoints[swir_unpind, cind[self.ind_label[self.man_col]]:cind[self.ind_label[self.tot_col-1]]+1], \
                                              swir2nir_qa.reshape((len(swir2nir_qa), 1)) \
                ))
            else:
                nir2swir_points = np.hstack(( nirpoints[nir_unpind, 0:3], \
                                              nirpoints[nir_unpind, cind['d_i']:cind['d_i']+1], \
                                              nir2swir_amp.reshape((len(nir2swir_amp), 1)), \
                                              np.zeros((len(nir2swir_amp), 3)), \
                                              nirpoints[nir_unpind, :][:, 5:10], \
                                              nir2swir_qa.reshape((len(nir2swir_qa), 1)) \
                ))
                swir2nir_points = np.hstack(( swirpoints[swir_unpind, 0:3], \
                                              swir2nir_amp.reshape((len(swir2nir_amp), 1)), \
                                              swirpoints[swir_unpind, cind['d_i']:cind['d_i']+1], \
                                              np.zeros((len(swir2nir_amp), 3)), \
                                              swirpoints[swir_unpind, :][:, 5:10], \
                                              swir2nir_qa.reshape((len(swir2nir_qa), 1)) \
                ))

            unionoutpoints = np.vstack(( outpoints, nir2swir_points, swir2nir_points ))
            sortind, num_of_returns, return_num, shotind = \
                self.updateReturnNum(unionoutpoints[:, [8, 11, 12]].copy())
            unionoutpoints = unionoutpoints[sortind, :]
            unionoutpoints[:, 5] = return_num
            unionoutpoints[:, 6] = num_of_returns
            unionoutpoints[:, 7] = shotind

            # exclude zero-hit points from rgb generation
            rgbpoints = np.zeros((unionoutpoints.shape[0], 3))
            hitmask = unionoutpoints[:, 6].astype(int) > 0
            # fix extremely large reflectance values
            bound = np.percentile(unionoutpoints[:, 3:5][hitmask, :], 98, axis=0)
            bound[bound<self.i_scale] = self.i_scale
            unionoutpoints[unionoutpoints[:, 3]>bound[0], 3] = bound[0]
            unionoutpoints[unionoutpoints[:, 4]>bound[1], 4] = bound[1]
            # generate pseudo-color composite
            rgbpoints[hitmask, :] = self.colorComposite(np.hstack((unionoutpoints[:, 4:5][hitmask, :], \
                                                           unionoutpoints[:, 3:4][hitmask, :], \
                                                           np.zeros_like(unionoutpoints[:, 3:4][hitmask, :]) \
                                                           )))
            unionoutpoints = np.hstack((unionoutpoints, rgbpoints))
            
            print "Saving dual-wavelength points: "+str(len(unionoutpoints))

            np.savetxt(outfile, unionoutpoints, delimiter=',', fmt=fmtstr, \
                header=headerstr.rstrip(), comments='')
            

    def colorComposite(self, specpoints):
        """
        Generate pseudo-color composite from three spectral bands of input
        points.

        Args:

            specpoints (2D numpy array, float): [npts, 3], band_for_R,
            band_for_G, band_for_B

        Returns:

            rgbpoints (2D numpy array, int): [npts, 3], R, G, B from 0 to 255
        """

        bound = np.percentile(specpoints, (2, 98), axis=0)
        # avoid all zeros in one band
        validbandmask = (bound>1e-10).any(axis=0)
        rgbpoints = np.zeros_like(specpoints, dtype=int)

        rgbpoints[:, validbandmask] = 255 * (specpoints[:, validbandmask] - np.tile(bound[0, validbandmask], (specpoints.shape[0], 1)))/np.tile(bound[1, validbandmask]-bound[0, validbandmask], (specpoints.shape[0], 1))
        rgbpoints = rgbpoints.astype(int)
        rgbpoints[rgbpoints<0] = 0
        rgbpoints[rgbpoints>255] = 255
        return rgbpoints
        
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


    def intersectPointClouds(self, nirpoints, swirpoints):
        """
        Find the intersect of two point clouds and return the indicies of common
        points in the original two point clouds.
        
        Args:

            nirpoints (2D numpy array, [npts, nrecs]): points of NIR band from DWEL
            scans. npts points (rows), nrecs records (columns). The records are:
            [range, sample, line]

            swirpoints (2D numpy array, [npts, nrecs]): points of SWIR band from
            DWEL scans. npts points (rows), nrecs records (columns). The records
            are: [range, sample, line]. Number of points can be different from that
            of NIR points.

        """
        # Check if there are zero-hit points. If yes, change their range values to
        # negative rdiff_thresh so that they cannot be paired with any other point.
        tmpind = np.where(nirpoints[:, 0] < 1e-10)[0]
        nirpoints[tmpind, 0] = -2*self.rdiff_thresh
        tmpind = np.where(swirpoints[:, 0] < 1e-10)[0]
        swirpoints[tmpind, 0] = -2*self.rdiff_thresh

        # convert samples and lines to one-dimensional indices
        # samples and lines starts from 1. calculated 1D indices starts from 1.
        nir_shotind = (nirpoints[:, 1]-1)*self.nrows + nirpoints[:, 2]
        swir_shotind = (swirpoints[:, 1]-1)*self.nrows + swirpoints[:, 2]
        # store the original shot indices here for use in the end
        old_nir_shotind = np.copy(nir_shotind)
        old_swir_shotind = np.copy(swir_shotind)

        # find out the points with common (sample, line)
        print "\tSearching points with common (sample, line), i.e. same laser shot"
        commonpts = np.intersect1d(nir_shotind, swir_shotind)
        nir_in = np.in1d(nir_shotind, commonpts)
        swir_in = np.in1d(swir_shotind, commonpts)

        # get points without counterparts, unpaired points
        nir_unpind = np.where(np.invert(nir_in))[0]
        swir_unpind = np.where(np.invert(swir_in))[0]
        
        # get those common points and keep tracking their indices in the original
        # vector b/c this is what we need to return
        nir_rg = nirpoints[nir_in, 0]
        swir_rg = swirpoints[swir_in, 0]
        nir_shotind = nir_shotind[nir_in]
        swir_shotind = swir_shotind[swir_in]
        # store the indices of common points in original vector. This is the UNIQUE
        # indices to each point.
        nir_trackind = np.where(nir_in)[0]
        swir_trackind = np.where(swir_in)[0]

        # find out locations of common points that have duplicates in select nir and
        # swir points, and the indices of their occurrences in the select nir and
        # swir points.
        print "\tSearching duplicate points from the same laser shot due to multi-returns"
        nir_u, nir_ind, nir_invind, nir_ucount= np.unique(nir_shotind, return_index=True, return_inverse=True, return_counts=True)
        swir_u, swir_ind, swir_invind, swir_ucount= np.unique(swir_shotind, return_index=True, return_inverse=True, return_counts=True)
        # because we already searched common points earlier, the nir_u and swir_u
        # here should be the same. check if they are the same.
        if ( np.fix(np.sum(nir_u-swir_u)) != 0):
            print "common point searching may be wrong!"
            return None
        # get indices in unique vector, of unique values that have duplicates
        nir_dupflag = np.greater(nir_ucount, 1)
        swir_dupflag = np.greater(swir_ucount, 1)
        dupflag = np.logical_or(nir_dupflag, swir_dupflag)
        dupind = np.where(dupflag)[0]
        # now in the non-unique vector (the vector that is input into np.unique),
        # where are those points with duplicated in either NIR or SWIR
        nir_dupflag = np.in1d(nir_invind, dupind)
        swir_dupflag = np.in1d(swir_invind, dupind)
        # now generate a vector of the same length with nir_shotind/swir_shotind, it
        # gives each shotind the number of its duplicates in the
        # nir_shotind/swir_shotind
        nir_all_ucount = nir_ucount[nir_invind]
        swir_all_ucount = swir_ucount[swir_invind]

        # now easy job first, tackle those points that are both unique in NIR and
        # SWIR, i.e. one-to-one corresponding relationship. double check if the
        # sorted vector from np.unique are the same for NIR and SWIR.
        uflag = np.logical_not(dupflag)
        if ( np.fix(np.sum(nir_u[uflag]-swir_u[uflag])) ):
            print "Unqiue shotind for both NIR and SWIR from np.unique are not in the same order. Consider using np.intersect1d again!"
            return None
        nir_uind = nir_ind[uflag]
        swir_uind = swir_ind[uflag]
        # select those points with range difference less than threshold
        tmpflag = np.less_equal(np.fabs(nir_rg[nir_uind]-swir_rg[swir_uind]), self.rdiff_thresh)
        # get the tracking indices of these points, i.e. the indices in original NIR
        # and SWIR points.
        nir_outind = nir_trackind[nir_uind[tmpflag]]
        swir_outind = swir_trackind[swir_uind[tmpflag]]
        # get unpaired points
        nir_unpind = np.hstack((nir_unpind, nir_trackind[nir_uind[np.invert(tmpflag)]]))
        swir_unpind = np.hstack((swir_unpind, swir_trackind[swir_uind[np.invert(tmpflag)]]))

        num_of_returns = np.ones_like(nir_outind)
        return_num = np.ones_like(nir_outind)
        # find zero-hit points and assign number_of_returns with zero
        tmpind = np.where(nir_rg[nir_uind[tmpflag]]<0)[0]
        num_of_returns[tmpind] = 0
        return_num[tmpind] = 0
        # an extra check
        if np.sum(tmpind - np.where(swir_rg[swir_uind[tmpflag]]<0)[0]):
            print "Indices to zero hit points in NIR and SWIR are not consistent!"

        # now difficult job, duplicates!!! Tackle them!
        # point pairs are either n-to-one, one-to-m, or n-to-m
        # now create a [N, 5] array, N is number of points including all
        # duplicates from both NIR and SWIR. [:, 0] is shotind, [:, 1] use 1 to
        # indicate NIR and 2 to indicate SWIR, [:, 2] is range, [:, 3] is indices in
        # original vector, [:, 4] is the number of duplicates of a shotind
        nir_ndup = np.sum(nir_dupflag)
        swir_ndup = np.sum(swir_dupflag)
        ncombined = nir_ndup + swir_ndup
        arr_combined = np.zeros((ncombined, 5))
        arr_combined[:nir_ndup, 0] = nir_shotind[nir_dupflag]
        arr_combined[:nir_ndup, 1] = 1064
        arr_combined[:nir_ndup, 2] = nir_rg[nir_dupflag]
        arr_combined[:nir_ndup, 3] = nir_trackind[nir_dupflag]
        arr_combined[:nir_ndup, 4] = nir_all_ucount[nir_dupflag]
        arr_combined[nir_ndup:ncombined, 0] = swir_shotind[swir_dupflag]
        arr_combined[nir_ndup:ncombined, 1] = 1548
        arr_combined[nir_ndup:ncombined, 2] = swir_rg[swir_dupflag]
        arr_combined[nir_ndup:ncombined, 3] = swir_trackind[swir_dupflag]
        arr_combined[nir_ndup:ncombined, 4] = swir_all_ucount[swir_dupflag]
        # now sort this combined array, first order (shotind), second order
        # (wavelength label)
        arr_combined_view = arr_combined.view(dtype=np.dtype( \
                [('shotind',arr_combined.dtype), \
                     ('wl', arr_combined.dtype), \
                     ('rg', arr_combined.dtype), \
                     ('trackind', arr_combined.dtype), \
                     ('ucount', arr_combined.dtype)] ) )
        arr_combined_sort = np.sort(arr_combined_view, order=['shotind', 'wl', 'rg'], axis=0)
        arr_combined_sort = arr_combined_sort.view(arr_combined.dtype).reshape(-1, arr_combined.shape[1])
        # now go through this sorted array sequentially to find point pairs with
        # range difference less than the given threshold
        local_closest_points = self.closest_points2
        local_len = len
        n_moreoutind = nir_ndup if nir_ndup<swir_ndup else swir_ndup
        nir_moreoutind = np.zeros(n_moreoutind, dtype=int)-1
        swir_moreoutind = np.zeros(n_moreoutind, dtype=int)-1
        more_num_of_returns = np.zeros(n_moreoutind, dtype=int)-1
        more_return_num = np.zeros(n_moreoutind, dtype=int)-1

        nir_moreout_count = 0
        swir_moreout_count = 0

        # unpaired points
        nir_moreunpind = np.zeros(nir_ndup, dtype=int)-1
        swir_moreunpind = np.zeros(swir_ndup, dtype=int)-1
        nir_moreunpind_count = 0
        swir_moreunpind_count = 0

        i = 0
        while i < ncombined:
            tmpnirrg = arr_combined_sort[i:i+np.int(arr_combined_sort[i, 4]), 2]
            tmpnirtrackind = arr_combined_sort[i:i+np.int(arr_combined_sort[i, 4]), 3]
            tmpind = np.int(i+arr_combined_sort[i, 4]+arr_combined_sort[i+np.int(arr_combined_sort[i, 4]), 4])
     #       print arr_combined_sort[i+np.int(arr_combined_sort[i, 4]), 1], tmpind
     #       print arr_combined_sort[i:i+np.int(arr_combined_sort[i, 4]), 1], arr_combined_sort[i+np.int(arr_combined_sort[i, 4]):tmpind, 1]

            tmpswirrg = arr_combined_sort[i+np.int(arr_combined_sort[i, 4]):tmpind, 2]
            tmpswirtrackind = arr_combined_sort[i+np.int(arr_combined_sort[i, 4]):tmpind, 3]
            if (self.verbose) and (i%1000 == 0):
                sys.stdout.write("Searching point pairs in (%i)      \r" % (i))
                sys.stdout.flush()
            ind = local_closest_points(tmpnirtrackind, tmpswirtrackind, tmpnirrg, tmpswirrg, self.rdiff_thresh)
            nunpind1 = local_len(ind[2])
            nunpind2 = local_len(ind[3])
            nir_moreunpind[nir_moreunpind_count:nir_moreunpind_count+nunpind1] = ind[2]
            swir_moreunpind[swir_moreunpind_count:swir_moreunpind_count+nunpind2] = ind[3]
            nir_moreunpind_count += nunpind1
            swir_moreunpind_count += nunpind2
            
            i = tmpind

            if len(ind[0])==0 or len(ind[1])==0:
                continue
            nind1 = local_len(ind[0])
            nind2 = local_len(ind[1])
            nir_moreoutind[nir_moreout_count:nir_moreout_count+nind1] = ind[0]
            swir_moreoutind[swir_moreout_count:swir_moreout_count+nind2] = ind[1]
            more_num_of_returns[nir_moreout_count:nir_moreout_count+nind1] = nind1
            more_return_num[nir_moreout_count:nir_moreout_count+nind1] = np.arange(nind1)+1
            nir_moreout_count += nind1
            swir_moreout_count += nind2

        nir_moreoutind = nir_moreoutind[:nir_moreout_count]
        swir_moreoutind = swir_moreoutind[:swir_moreout_count]
        more_num_of_returns = more_num_of_returns[:nir_moreout_count]
        more_return_num = more_return_num[:nir_moreout_count]

        nir_moreunpind = nir_moreunpind[0:nir_moreunpind_count]
        swir_moreunpind = swir_moreunpind[0:swir_moreunpind_count]
        nir_unpind = np.hstack((nir_unpind, nir_moreunpind))
        swir_unpind = np.hstack((swir_unpind, swir_moreunpind))

        # last but not least, let's put a label on whether it is a multi-return in
        # either wavelengths or not.
        nir_outind = nir_outind.squeeze()
        swir_outind = swir_outind.squeeze()
        nir_moreoutind = nir_moreoutind.squeeze()
        swir_moreoutind = swir_moreoutind.squeeze()
        return_type = np.hstack((np.zeros_like(nir_outind, dtype=np.bool_), \
                                     np.ones_like(swir_moreoutind, dtype=np.bool_)))

        nir_alloutind = np.hstack((nir_outind, nir_moreoutind)).astype(int)
        swir_alloutind = np.hstack((swir_outind, swir_moreoutind)).astype(int)

        all_num_of_returns = np.hstack((num_of_returns, more_num_of_returns)).astype(int)
        all_return_num = np.hstack((return_num, more_return_num)).astype(int)

        # check shotind of nir and swir, they should be the same!
        nu_nir_shotind = old_nir_shotind[nir_alloutind]
        nu_swir_shotind = old_swir_shotind[swir_alloutind]
        if np.sum(np.fabs(nu_nir_shotind-nu_swir_shotind)) > 1e-10:
            raise RuntimeError("Error: calculated shot number after point cloud merge went wrong!")

        # sort new shotind in ascending order such that the output point cloud will
        # be in such an ascending order, image line number ascending first, then
        # image sample number ascending second.
        # arr_combined = np.hstack((nu_nir_shotind, all_return_num))
        arr_combined = np.zeros((len(nu_nir_shotind), 2))
        arr_combined[:, 0] = nu_nir_shotind
        arr_combined[:, 1] = all_return_num
        arr_combined_view = arr_combined.view(dtype=np.dtype( \
                [('shotind', arr_combined.dtype), ('return_num', arr_combined.dtype)]))
        sortind = np.argsort(arr_combined_view, order=['shotind', 'return_num'], axis=0)
        sortind = sortind.squeeze()
        nir_alloutind = nir_alloutind[sortind]
        swir_alloutind = swir_alloutind[sortind]
        return_type = return_type[sortind]
        nu_nir_shotind = nu_nir_shotind[sortind]
        all_num_of_returns = all_num_of_returns[sortind]
        all_return_num = all_return_num[sortind]

        return nir_alloutind, swir_alloutind, return_type, \
            nu_nir_shotind, all_num_of_returns, all_return_num, \
            nir_unpind, swir_unpind, \
            old_nir_shotind[nir_unpind], old_swir_shotind[swir_unpind]

    def cp(self, value1, value2, thresh):
        """
        Utility function used by closest_points
        """
        v1, v2 = np.meshgrid(value1, value2, indexing='ij')
        vdiff = np.fabs(v1-v2)
        i1, i2 = np.where(vdiff <= thresh)
        if len(i1) <= 0:
            return None, None, None
        vdiff = vdiff[i1, i2]
        return i1, i2, vdiff

    def closest_points2(self, ind1, ind2, value1, value2, thresh):
        """
        A second version of point pairing. Aims to be more accurate, maybe slower.

        Find a point pair that has value difference less than thresh, if one point
        has more than one corresponding point, choose the closest one.

        value1 and value2 have to be sorted in ascending sequence.
        """
        # preserve original ind1 and ind2 for some usage in the end
        oldind1 = ind1.copy().astype(int)
        oldind2 = ind2.copy().astype(int)
        # Find the closest point pair. Check if their difference in values are
        # smaller than given threshold. If not, stop and return. If yes, this is a
        # point pair we need. Store them and remove them from the original
        # lists. Repeat this procedure until stop and return.
        npair = max(len(value1), len(value2))
        pairind = np.zeros((npair, 2), dtype=int)
        pairvalue = np.zeros((npair, 2), dtype=float)
        paircnt = 0
        while ( (len(value1)>0) and (len(value2)>0) ):
            i1, i2, vdiff = self.cp(value1, value2, thresh)
            if i1 is None:
                break
            if len(vdiff)>1:
                sortind = np.argsort(vdiff)
                i1 = i1[sortind]
                i2 = i2[sortind]
                vdiff = vdiff[sortind]
            foundflag = False
            for ti1, ti2, tvdiff in zip(i1, i2, vdiff):
                pairind[paircnt, :] = [ind1[ti1], ind2[ti2]]
                pairvalue[paircnt, :] = [value1[ti1], value2[ti2]]
                # sort the two value lists and make sure value1 and value2 in point
                # pairs have the same order. The value1 and value2 in new point pair
                # have to be on the same side of existing point pair, that is value1 and
                # value2 should beeither both larger than existing point pair or both
                # smaller, cannot be one is larger and the other is smaller.
                sortind1 = np.argsort(pairvalue[0:paircnt+1, 0])
                sortind2 = np.argsort(pairvalue[0:paircnt+1, 1])
                if np.sum(sortind1 - sortind2) == 0:
                    # only if this point pair qualifies, we record it in the point pair
                    # by incrementing point pair counter
                    paircnt += 1
                    tmpmask = np.ones_like(ind1, dtype=np.bool_)
                    tmpmask[ti1] = False
                    ind1 = ind1[tmpmask]
                    value1 = value1[tmpmask]
                    tmpmask = np.ones_like(ind2, dtype=np.bool_)
                    tmpmask[ti2] = False
                    ind2 = ind2[tmpmask]
                    value2 = value2[tmpmask]
                    foundflag = True
                    break
            if not foundflag:
                break

        if paircnt>0:
            pairind = pairind[0:paircnt, :]
            pairvalue = pairvalue[0:paircnt, :]
            sortind1 = np.argsort(pairvalue[:, 0])
            sortind2 = np.argsort(pairvalue[:, 1])
            # final check
            if np.sum(sortind1 - sortind2) != 0:
                raise RuntimeError("Points from closest point pair searching do not have the same order of range values")
            pairind = pairind[sortind1, :]
            # find unpaired points
            if paircnt<len(oldind1):
                outmask = np.in1d(oldind1, pairind[:, 0], invert=True)
                unp_ind1 = oldind1[outmask]
            else:
                unp_ind1 = np.array([], dtype=int)
            if paircnt<len(oldind2):
                outmask = np.in1d(oldind2, pairind[:, 1], invert=True)
                unp_ind2 = oldind2[outmask]
            else:
                unp_ind2 = np.array([], dtype=int)
            return pairind[:, 0], pairind[:, 1], unp_ind1, unp_ind2
        else:
            return np.array([]), np.array([]), oldind1, oldind2
    

    def unionPointClouds(self, nirpts, swirpts, ndiimgfile):
        """
        Synthesize point intensities from NIR/SWIR points that do not have
        counterparts at the other wavelength.

        Args:

            nirpts (2D numpy array, float): NIR points without SWIR couterparts, [npts,
            3], rho_app, sample, line

            ndiimgfile (string): file name of NDI image with a mask band. Mask
            band meaning: 0, invalid shot if both NIR and SWIR claim invalid; 1,
            measured NDI; 2: filled NDI; 3: no-return but valid shots

        Returns:

            nir2swir_amp (1D numpy array, float): rho_app at SWIR from NIR
            
            nir2swir_qa (1D numpy array, int): QA of points synthesized from NIR to SWIR
            
            swir2nir_amp (1D numpy array, float): rho_app at NIR from SWIR

            swir2nir_qa (1D numpy array, int): QA of points synthesized from SWIR to NIR
        """
        ndib = 1
        maskb = 2

        imgds = gdal.Open(ndiimgfile, gdal.GA_ReadOnly)
        ndiband = imgds.GetRasterBand(ndib)
        maskband = imgds.GetRasterBand(maskb)

        ndi = ndiband.ReadAsArray(0, 0, ndiband.XSize, ndiband.YSize)
        mask = maskband.ReadAsArray(0, 0, maskband.XSize, maskband.YSize)

        tmpndi = ndi[nirpts[:, 2].astype(int)-1, nirpts[:, 1].astype(int)-1]
        tmpflag = np.greater(mask[nirpts[:, 2].astype(int)-1, nirpts[:, 1].astype(int)-1], 0)
        # an extra check
        if not(tmpflag.all()):
            print "sample/column no.:"
            print nirpts[np.invert(tmpflag), 1]
            print "line/row no.:"
            print nirpts[np.invert(tmpflag), 2]
            raise RuntimeError("These NIR points are from invalid shots. Check NIR point cloud")
        nir2swir_qa = np.zeros_like(tmpndi, dtype=int)
        tmpflag1 = np.equal(mask[nirpts[:, 2].astype(int)-1, nirpts[:, 1].astype(int)-1], 1)
        nir2swir_qa[tmpflag1] = int('001', 2)
        tmpflag2 = np.equal(mask[nirpts[:, 2].astype(int)-1, nirpts[:, 1].astype(int)-1], 2)
        nir2swir_qa[tmpflag2] = int('101', 2)
        tmpflag = np.logical_or(tmpflag1, tmpflag2)
        nir2swir_qa[np.invert(tmpflag)] = int('111', 2)
        nir2swir_amp = np.zeros_like(tmpndi)
        nir2swir_amp[tmpflag] = (1-tmpndi[tmpflag])/(1+tmpndi[tmpflag])*nirpts[:, 0][tmpflag]
        # # prevent synthetic reflectance values to be too large
        # np.greater(nir2swir_amp, self.i_scale)

        tmpndi = ndi[swirpts[:, 2].astype(int)-1, swirpts[:, 1].astype(int)-1]
        tmpflag = np.greater(mask[swirpts[:, 2].astype(int)-1, swirpts[:, 1].astype(int)-1], 0)
        # an extra check
        if not(tmpflag.all()):
            print "sample/column no.:"
            print swirpts[np.invert(tmpflag), 1]
            print "line/row no.:"
            print swirpts[np.invert(tmpflag), 2]
            raise RuntimeError("These SWIR points are from invalid shots. Check SWIR point cloud")
        swir2nir_qa = np.zeros_like(tmpndi, dtype=int)
        tmpflag1 = np.equal(mask[swirpts[:, 2].astype(int)-1, swirpts[:, 1].astype(int)-1], 1)
        swir2nir_qa[tmpflag1] = int('010', 2)
        tmpflag2 = np.equal(mask[swirpts[:, 2].astype(int)-1, swirpts[:, 1].astype(int)-1], 2)
        swir2nir_qa[tmpflag2] = int('110', 2)
        tmpflag = np.logical_or(tmpflag1, tmpflag2)
        swir2nir_qa[np.invert(tmpflag)] = int('111', 2)
        swir2nir_amp = np.zeros_like(tmpndi)
        swir2nir_amp[tmpflag] = (1+tmpndi[tmpflag])/(1-tmpndi[tmpflag])*swirpts[:, 0][tmpflag]
        
        return nir2swir_amp, nir2swir_qa, swir2nir_amp, swir2nir_qa
