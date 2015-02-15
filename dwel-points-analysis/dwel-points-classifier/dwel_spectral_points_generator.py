#!/usr/bin/env python
"""
Generate a dual-wavelength spectral point cloud from two point clouds at the two
wavelengths out of DWEL scans. It searches the common points between the two
point clouds and write a single point cloud with dual-wavelength intensities.

USAGE:

    dwel_spectral_points_generator.py --nir <string> --swir <string> -o <string>
    [-r <float>]

OPTIONS:

    --nir <string>
    (required) name of input point cloud file of NIR band.

    --swir <string>
    (required) name of input point cloud file of SWIR band.

    -o <string>, --output <string>
    (required) name of output dual-wavelength point cloud file

    -r <float>, --rdiff <float>
    a threshold of range difference between the two wavelengths to determine if
    two points are common points from the same target. [default: 0.75 m]

EXAMPLES:

AUTHORS:

    Zhan Li, zhanli86@bu.edu

"""

import sys
import time
import optparse
import numpy as np

def search_duplicate_row2(arr):
    """
    search duplicate rows in 2D numpy array, arr.

    Args:

        arr (2D numpy array): NOTE, arr cannot be from slicing or indexing of an
        array, instead make a copy to the input.

    Returns:
    
    """

    # potentially a faster version than using numpy's in1d
    order = np.lexsort(arr.T)
    s_arr = arr[order]
    diff = np.diff(s_arr, axis=0)
    uniqueflag = np.ones(s_arr.shape[0], dtype=np.bool_)
    uniqueflag[1:] = (diff != 0).any(axis=1)
    u_arr = s_arr[uniqueflag]
    nunique = u_arr.shape[0]
    dupmask = np.zeros(nunique, dtype=np.bool_)
    indices = np.empty(nunique, dtype = np.object_)
    ui = 0
    for i in range(s_arr.shape[0]-1):
        if uniqueflag[i] and uniqueflag[i+1]:
            indices[ui] = [order[i]]
            ui += 1
        if uniqueflag[i] and not uniqueflag[i+1]:
            tmplist = [order[i]]
        if not uniqueflag[i] and uniqueflag[i+1]:
            tmplist.append(order[i])
            indices[ui] = tmplist
            dupmask[ui] = True
            ui += 1
        if not uniqueflag[i] and not uniqueflag[i+1]:
            tmplist.append(order[i])

    i += 1
    if uniqueflag[i]:
        indices[ui] = [order[i]]
    else:
        tmplist.append(order[i])
        indices[ui] = tmplist
        dupmask[ui] = True

    return dupmask, indices, u_arr

def search_duplicate_row(arr):
    """
    search duplicate rows in 2D numpy array, arr.

    Args:

        arr (2D numpy array): NOTE, arr cannot be from slicing or indexing of an
        array, instead make a copy to the input.

    Returns:
    
    """

    # create a new view of arr, each row is a single element in this view.
    arr_view = arr.view([('',arr.dtype)]*arr.shape[1])
    # use numpy unique function to find unique elements (row of arr)
    u_arr, u_arr_ind = np.unique(arr_view, return_inverse=True)
    # the indices of all occurrences of unique values in the original array. For
    # duplicates, the element of the list indices gives multiple indices of
    # the occurrences of a unique value in the original array.
    indices = [ np.where(u_arr_ind==x)[0] for x in range(u_arr.shape[0]) ]
    # find out where are the unique values that have duplicates in original
    # array.
    dup_mask = np.greater(map(len, indices), 1)
    return dup_mask, indices, u_arr.view(arr.dtype).reshape(-1, arr.shape[1])

def intersect_nd(arr1, arr2):
    """
    Utility function to do set inetersection of 2D numpy arrays. 

    Args:

        arr1, arr2 (2D numpy arrays): NOTE, arr1 and arr2 cannot be from slicing
        or indexing of an array, instead make a copy to the input.

    Returns:
    
    """

    arr1_view = arr1.view([('',arr1.dtype)]*arr1.shape[1])
    arr2_view = arr2.view([('',arr2.dtype)]*arr2.shape[1])
    intersected = np.intersect1d(arr1_view, arr2_view)

    arr1_in = np.in1d(arr1_view, intersected)
    arr2_in = np.in1d(arr2_view, intersected)
    return arr1_in, arr2_in, \
        intersected.view(arr1.dtype).reshape(-1, arr1.shape[1])

def intersect_1d(arr1, arr2):
    """
    Utility function to do set inetersection of 1D numpy arrays. 

    Args:

        arr1, arr2 (2D numpy arrays): NOTE, arr1 and arr2 cannot be from slicing
        or indexing of an array, instead make a copy to the input.

    Returns:
    
    """

    intersected = np.intersect1d(arr1, arr2)

    arr1_in = np.in1d(arr1_view, intersected)
    arr2_in = np.in1d(arr2_view, intersected)
    return arr1_in, arr2_in, \
        intersected.view(arr1.dtype).reshape(-1, arr1.shape[1])

def closest_points(ind1, ind2, value1, value2, thresh):
    """
    Find a point pair that has value difference less than thresh, if one point
    has more than one corresponding point, choose the closest one.
    
    value1 and value2 have to be sorted in ascending sequence.
    """

    v1, v2 = np.meshgrid(value1, value2, indexing='ij')
    vdiff = np.fabs(v1-v2)
    vflag = vdiff<=thresh
    c_ind = (vflag).nonzero()
    if c_ind[0].size == 0:
        return ()

    vdiff = vdiff[vflag]
    c_ind1 = c_ind[0]
    c_ind2 = c_ind[1]
    min_ind = np.argmin(vdiff)
    flag = np.logical_and(c_ind1 != c_ind1[min_ind], c_ind2 != c_ind2[min_ind])
    min_ind1 = ind1[c_ind1[min_ind]]
    min_ind2 = ind2[c_ind2[min_ind]]
    min_value1 = value1[c_ind1[min_ind]]
    min_value2 = value2[c_ind2[min_ind]]
    shift_value = min_value1 - min_value2
    if np.count_nonzero(flag) == 0:
        return  [min_ind1], [min_ind2]

    # check the remaining points and align them
    c_ind1 = np.unique(c_ind1[flag])
    c_ind2 = np.unique(c_ind2[flag])
    ind1 = ind1[c_ind1]
    ind2 = ind2[c_ind2]
    value1 = value1[c_ind1]
    value2 = value2[c_ind2] + shift_value
    new_thresh = thresh - np.fabs(shift_value)
    # check each left point's neighboring range, see if we can find a point pair
    # for it
    # check left side of closest point pair
    flag1 = value1 < min_value1
    flag2 = value2 < min_value2
    n1 = np.count_nonzero(flag1)
    n2 = np.count_nonzero(flag2)
    leftind1 = [ min_ind1 ]
    leftind2 = [ min_ind2 ]
    if n1 and n2:
        i2 = 0
        for i1 in range(n1):
            if i2 >= n2:
                break
            x = value1[flag1][i1]
            tmpvdiff = np.fabs(value2[flag2][i2:n2] - x)
            tmpind = np.argmin(tmpvdiff)
            if tmpvdiff[tmpind] < new_thresh:
                leftind1.append(ind1[flag1][i1])
                leftind2.append(ind2[flag2][i2:n2][tmpind])
                i2 += 1
    # check right side of closest point pair
    flag1 = value1 > min_value1
    flag2 = value2 > min_value2
    n1 = np.count_nonzero(flag1)
    n2 = np.count_nonzero(flag2)
    rightind1 = []
    rightind2 = []
    if n1 and n2:
        i2 = 0
        for i1 in range(n1):
            if i2 >= n2:
                break
            x = value1[flag1][i1]
            tmpvdiff = np.fabs(value2[flag2][i2:n2] - x)
            tmpind = np.argmin(tmpvdiff)
            if tmpvdiff[tmpind] < new_thresh:
                leftind1.append(ind1[flag1][i1])
                leftind2.append(ind2[flag2][i2:n2][tmpind])
                i2 += 1
    return leftind1+rightind1, leftind2+rightind2


def generate_spectral_points(nirpoints, swirpoints, rdiff_thresh=0.96, nr=3142, nc=1022):
    """
    Search common points between two point clouds at the two wavelengths and
    generate a single dual-wavelength point cloud.

    Args:
    
        nirpoints (2D numpy array, [npts, nrecs]): points of NIR band from DWEL
        scans. npts points (rows), nrecs records (columns). The records are:
        [range, sample, line]

        swirpoints (2D numpy array, [npts, nrecs]): points of SWIR band from
        DWEL scans. npts points (rows), nrecs records (columns). The records
        are: [range, sample, line]. Number of points can be different from that
        of NIR points.

        rdiff_thresh (float): a threshold of range difference between the two
        wavelengths to determine if two points are common points from the same
        target. [default: 0.75 m]

    Returns:

        nir_ind (1D numpy array), indices of found common points in nirpoints
        swir_ind (1D numpy array), indices of found common points in swirpoints
    
    """

    # convert samples and lines to one-dimensional indices
    # samples and lines starts from 1. calculated 1D indices starts from 1.
    nir_shotind = (nirpoints[:, 2]-1)*nc + nirpoints[:, 1]
    swir_shotind = (swirpoints[:, 2]-1)*nc + swirpoints[:, 1]
    # store the original shot indices here for use in the end
    old_nir_shotind = np.copy(nir_shotind)
    old_swir_shotind = np.copy(swir_shotind)

    # # sort shotind first and record the indices that would sort the original
    # # vector.
    # nir_shotind_order = np.argsort(nir_shotind, kind='mergesort')
    # swir_shotind_order = np.argsort(swir_shotind, kind='mergesort')
    
    # find out the points with common (sample, line)
    print "Searching common points"
    commonpts = np.intersect1d(nir_shotind, swir_shotind)
    nir_in = np.in1d(nir_shotind, commonpts)
    swir_in = np.in1d(swir_shotind, commonpts)

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
    print "Searching duplicate points"
    nir_u, nir_ind, nir_invind, nir_ucount= np.unique(nir_shotind, return_index=True, return_inverse=True, return_counts=True)
    swir_u, swir_ind, swir_invind, swir_ucount= np.unique(swir_shotind, return_index=True, return_inverse=True, return_counts=True)
    # because we already searched common points earlier, the nir_u and swir_u
    # here should be the same. check if they are the same.
    if ( np.fix(np.sum(nir_u-swir_u)) != 0):
        print "common point searching may be wrong!"
        return []
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
        return []
    nir_uind = nir_ind[uflag]
    swir_uind = swir_ind[uflag]
    # select those points with range difference less than threshold
    tmpflag = np.less_equal(np.fabs(nir_rg[nir_uind]-swir_rg[swir_uind]), rdiff_thresh)
    # get the tracking indices of these points, i.e. the indices in original NIR
    # and SWIR points.
    nir_outind = nir_trackind[nir_uind[tmpflag]]
    swir_outind = swir_trackind[swir_uind[tmpflag]]

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
    local_closest_points = closest_points
    local_len = len
    n_moreoutind = nir_ndup if nir_ndup<swir_ndup else swir_ndup
    nir_moreoutind = np.zeros(n_moreoutind)-1
    swir_moreoutind = np.zeros(n_moreoutind)-1
    nir_moreout_count = 0
    swir_moreout_count = 0

    i = 0
    while i < ncombined:
  #      print i, arr_combined_sort[i, 1], arr_combined_sort[i, 4]
        tmpnirrg = arr_combined_sort[i:i+np.int(arr_combined_sort[i, 4]), 2]
        tmpnirtrackind = arr_combined_sort[i:i+np.int(arr_combined_sort[i, 4]), 3]
        tmpind = np.int(i+arr_combined_sort[i, 4]+arr_combined_sort[i+np.int(arr_combined_sort[i, 4]), 4])
 #       print arr_combined_sort[i+np.int(arr_combined_sort[i, 4]), 1], tmpind
 #       print arr_combined_sort[i:i+np.int(arr_combined_sort[i, 4]), 1], arr_combined_sort[i+np.int(arr_combined_sort[i, 4]):tmpind, 1]

        tmpswirrg = arr_combined_sort[i+np.int(arr_combined_sort[i, 4]):tmpind, 2]
        tmpswirtrackind = arr_combined_sort[i+np.int(arr_combined_sort[i, 4]):tmpind, 3]
        ind = local_closest_points(tmpnirtrackind, tmpswirtrackind, tmpnirrg, tmpswirrg, rdiff_thresh)

        i = tmpind

        if not ind:
            continue
        nind1 = local_len(ind[0])
        nind2 = local_len(ind[1])
        nir_moreoutind[nir_moreout_count:nir_moreout_count+nind1] = ind[0]
        swir_moreoutind[swir_moreout_count:swir_moreout_count+nind2] = ind[1]
        nir_moreout_count += nind1
        swir_moreout_count += nind2

    nir_moreoutind = nir_moreoutind[:nir_moreout_count]
    swir_moreoutind = swir_moreoutind[:swir_moreout_count]

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

    # check shotind of nir and swir, they should be the same!
    nu_nir_shotind = old_nir_shotind[nir_alloutind]
    nu_swir_shotind = old_swir_shotind[swir_alloutind]
    if np.sum(np.fabs(nu_nir_shotind-nu_swir_shotind)) > 1e-10:
        print "Error: calculated shot number after point cloud merge went wrong!"
    
    return nir_alloutind, swir_alloutind, return_type, \
        nu_nir_shotind

def main(cmdargs):
    """
    Main function to take in inputs from command line and pass them to the
    correct functions.
    """

    # set some parameters
    headerlines = 3
    # column indices for some records used here, with 0 as the first.
    cind = {'range':8, 'sample':12, 'line':13, 'x':0, 'y':1, 'z':2, 'd_I':3, \
                'shot_number':6, 'theta':9, 'phi':10, 'fwhm':16}
    ind = [cind['x'], cind['y'], cind['z'], cind['d_I'], cind['shot_number'], cind['range'], cind['theta'], \
               cind['phi'], cind['sample'], cind['line'], cind['fwhm']]
    
    # get inputs from command line or defaults
    nirfile = cmdargs.nirfile
    swirfile = cmdargs.swirfile
    outfile = cmdargs.outfile
    rdiff_thresh = float(cmdargs.rdiff_thresh)
    nrows = int(cmdargs.nrows)
    ncols = int(cmdargs.ncols)

    print "Input NIR point cloud: "+nirfile
    print "Input SWIR point cloud: "+swirfile
    print "Output merged point cloud: "+outfile
    print "Range difference threshold: {0:.3f}".format(rdiff_thresh)
    print "Info for converting sample and line to shot number: \n" \
        + "number of rows: {0:d}, number of columns: {1:d}".format(nrows, ncols)
    
    # read points from text file
    print "Loading points"
    nirpoints = np.genfromtxt(nirfile, dtype=np.float32, usecols=ind, \
                                  delimiter=',', skiprows=headerlines, \
                                  filling_values=np.nan, usemask=False)
    swirpoints = np.genfromtxt(swirfile, dtype=np.float32, usecols=ind, \
                                  delimiter=',', skiprows=headerlines, \
                                  filling_values=np.nan, usemask=False)
#    nirpoints = np.loadtxt(nirfile, dtype=np.float32, usecols=ind, delimiter=',', skiprows=headerlines)
#    swirpoints = np.loadtxt(swirfile, dtype=np.float32, usecols=ind, delimiter=',', skiprows=headerlines)

    # update column index in loaded array
    cind = {'x':0, 'y':1, 'z':2, 'd_I':3, 'shot_number':4, 'range':5, \
                'theta':6, 'phi':7, 'sample':8, 'line':9, 'fwhm':10}

    # index the columns that are used in searching common points
    ind = [cind['range'], cind['sample'], cind['line']]

    # ==========================================================================
    # snippet to test functions
    # test_arr1 = np.array([[1, 0, 2],
    #                       [0, 1, 3],
    #                       [0, 4, 5],
    #                       [3, 0, 2],
    #                       [2, 1, 3]], dtype=np.float_)

    # test_arr2 = np.array([[0, 1, 2],
    #                       [0.5, 0, 2],
    #                       [0, 3, 1],
    #                       [10, 1, 3],
    #                       [1.8, 1, 3]], dtype=np.float_)
    # generate_spectral_points(test_arr1, test_arr2, rdiff_thresh)
    # import pdb; pdb.set_trace()

    # ind1 = np.array([8, 19, 23])
    # ind2 = np.array([10, 25, 40, 45, 46])
    # value1 = np.fabs(np.array([ -9.38148429,  -0.7846738 ,  2.37783463]))
    # value1.sort()
    # value2 = np.fabs(np.array([ 28.5317877 , -10.36982583,  -9.53640246,   2.63467859,   3.78260151]))
    # value2.sort()
    # print value1
    # print value2
    # import pdb; pdb.set_trace()
    # sind1, sind2 = closest_points(ind1, ind2, value1, value2, 10)
    # import pdb; pdb.set_trace()
    # ==========================================================================
    

    # call function of generating spectral points
    print "Enter spectral points generator"
    nir_ind, swir_ind, return_type, nu_shotnum, \
        = generate_spectral_points(nirpoints[:,ind], swirpoints[:,ind], \
                                       rdiff_thresh, nr=nrows, nc=ncols)

    # calculate the mean point location
    ind = [cind['x'], cind['y'], cind['z'], cind['shot_number'], cind['range'], cind['theta'], \
               cind['phi'], cind['sample'], cind['line']]

    nreturn = len(return_type)
    meanpoints = (nirpoints[np.ix_(nir_ind, ind)] + swirpoints[np.ix_(swir_ind, ind)])/2.0
    outpoints = np.hstack((meanpoints[:, 0:3], \
                               nirpoints[nir_ind, cind['d_I']:cind['d_I']+1], \
                               swirpoints[swir_ind, cind['d_I']:cind['d_I']+1], \
                               nu_shotnum.reshape((nreturn, 1)), \
                               meanpoints[:, 4:9], \
                               nirpoints[nir_ind, cind['fwhm']:cind['fwhm']+1], \
                               swirpoints[swir_ind, cind['fwhm']:cind['fwhm']+1], \
                               return_type.reshape((nreturn, 1))))
    
    prefixstr = "[DWEL Dual-wavelength Point Cloud Data]\nRun made at: "+time.strftime("%c")+"\n"
    headerstr = prefixstr + "x,y,z,d_I_nir,d_I_swir,shot_number,range,theta,phi,sample,line,fwhm_nir,fwhm_swir,multi-return"
    # write to file
    print "Saving dual-wavelength points: "+str(nir_ind.size)
    fmtstr = "%.3f "*5 + "%d " + "%.3f "*3 + "%d "*2 + "%.3f "*2 + "%d "
    fmtstr = fmtstr.strip().split(" ")
    np.savetxt(outfile, outpoints, delimiter=',', fmt=fmtstr, \
        header=headerstr.rstrip())

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()

        p.add_option("-n", "--nir", dest="nirfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp2_ptcl_points.txt", help="Input point cloud file of NIR band")
        p.add_option("-s", "--swir", dest="swirfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1548_cube_bsfix_pxc_update_atp2_ptcl_points.txt", help="Input point cloud file of SWIR band")
        p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt", help="Output dual-wavelength point cloud file")


        # p.add_option("-n", "--nir", dest="nirfile", default=None, help="Input point cloud file of NIR band")
        # p.add_option("-s", "--swir", dest="swirfile", default=None, help="Input point cloud file of SWIR band")
        # p.add_option("-o", "--output", dest="outfile", default=None, help="Output dual-wavelength point cloud file")

        p.add_option("-R", "--rdiff", dest="rdiff_thresh", default="0.96", help="a threshold of range difference between the two wavelengths to determine if two points are common points from the same target. [default: 0.96 m]")
        p.add_option("-c", "--cols", dest="ncols", default="1022", help="Number of columns (samples) in the AT projection where points are generated. [default: 1022]")
        p.add_option("-r", "--rows", dest="nrows", default="3142", help="Number of rows (lines) in the AT projection where points are generated. [default: 3142]")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.nirfile is None) | (self.swirfile is None) | (self.outfile is None):
            p.print_help()
            print "Both input and output file names are required."
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
