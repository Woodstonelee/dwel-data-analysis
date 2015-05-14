#!/usr/bin/env python
"""
Accuracy assessment of DWEL point cloud classification from comparison of
hemiphotos and hemi-projection of point cloud.

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

import itertools

from osgeo import gdal
gdal.AllRegister()

import numpy as np
import pandas as pd

def getCmdArgs():
    p = argparse.ArgumentParser(description="Accuracy assessment of DWEL point cloud classification")

    # p.add_argument("--csv", dest="csv", nargs='+', default=("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples_validation.csv", "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/hsproj-random-samples/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples_validation.csv"), help="CSV files of 'ground truth' data from hemiphotos and visual interpretation")
    # p.add_argument("--img", dest="img", nargs='+', default=("/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2_extrainfo.img", "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_E_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class_hsp2_extrainfo.img"), help="ENVI image files of extra information for accuracy assessment, e.g. number of points per projection bin in the hemispherical image")
    # p.add_argument("-o", "--outfile", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/hfhd20140503-points-classification-accuracy-assessment/error-matrices/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_hsp2_random_samples_validation_errmat.txt", help="Output file of accuracy assessment summary")

    p.add_argument("--csv", dest="csv", nargs='+', default=None, help="CSV files of 'ground truth' data from hemiphotos and visual interpretation")
    p.add_argument("--img", dest="img", nargs='+', default=None, help="ENVI image files of extra information for accuracy assessment, e.g. number of points per projection bin in the hemispherical image")
    p.add_argument("-o", "--outfile", dest="outfile", default=None, help="Output file of accuracy assessment summary")

    p.add_argument("--inptsB", dest="inptsB", type=int, default=3, help="In the ENVI image file, the band index of the number of points included in generation of pixel values of hemispherical projection from DWEL point cloud, with first band being 1. Default: 3")
    p.add_argument("--outptsB", dest="outptsB", type=int, default=4, help="In the ENVI image file, the band index of the number of points NOT included in generation of pixel values of hemispherical projection from DWEL point cloud, with first band being 1. Default: 4")

    p.add_argument("--zerozen", dest='zerozen', type=int, nargs=2, metavar=('zerozen_row', 'zerozen_col'), default=(1022, 1022), help='Location of zero zenith in the hemispherical image')
    p.add_argument("--inres", dest="inres", type=float, default=2.0, help="Resolution of input hemispherical image. Unit: mrad. Default: 2.0 mrad")

    cmdargs = p.parse_args()

    if (cmdargs.csv is None) or (cmdargs.outfile is None):
        p.print_help()
        print "Both csv of 'ground truth' and output file names must be given."
        sys.exit()

    return cmdargs

def main(cmdargs):
    csvfiles = cmdargs.csv
    imgfiles = cmdargs.img
    outfile = cmdargs.outfile
    inresolution = cmdargs.inres*1e-3

    zerozen = cmdargs.zerozen

    inptsB = None
    outptsB = None
    nfiles = len(csvfiles)
    if imgfiles is not None:
        if len(imgfiles) != nfiles:
            raise RuntimeError("Number of CSV files of ground truth must be the same as the number of ENVI image files of extra information if you give the ENVI image files")
        inptsB = cmdargs.inptsB
        outptsB = cmdargs.outptsB

    # read CSV file
    groundtruth_list = [ np.loadtxt(csv, delimiter=',', skiprows=1) for csv in csvfiles ]
#    groundtruth = np.loadtxt(csvfile, delimiter=',', skiprows=1)
    # error matrix by number of pixels
    class_label_list = [ gt[:, 2] for gt in groundtruth_list ]
    primary_label_list = [ gt[:, 3] for gt in groundtruth_list ]
    secondary_label_list = [ gt[:, 4] for gt in groundtruth_list ]
    # class_label = groundtruth[:, 2]
    # primary_label = groundtruth[:, 3]
    # secondary_label = groundtruth[:, 4]

    pixel_row_list = [ (gt[:, 1] + 0.5)*-1 for gt in groundtruth_list ]
    pixel_col_list = [ gt[:, 0] - 0.5 for gt in groundtruth_list ]

    pixel_zen = np.sqrt((np.hstack(pixel_row_list)-zerozen[0])**2+(np.hstack(pixel_col_list)-zerozen[1])**2)*inresolution
    weights = np.sin(pixel_zen)

    primary_errmat_pixel_counts = calcErrorMatrix( \
        np.hstack(class_label_list).astype(np.int), \
            np.hstack(primary_label_list).astype(np.int))

    primary_errmat_pixel_area = calcErrorMatrix( \
        np.hstack(class_label_list).astype(np.int), \
            np.hstack(primary_label_list).astype(np.int), \
            weights=weights)

    secondary_errmat_pixel_counts = calcErrorMatrix( \
        np.hstack(class_label_list).astype(np.int), \
            np.hstack(secondary_label_list).astype(np.int))

    secondary_errmat_pixel_area = calcErrorMatrix( \
        np.hstack(class_label_list).astype(np.int), \
            np.hstack(secondary_label_list).astype(np.int), \
            weights=weights)

    mean_errmat_pixel_counts = (primary_errmat_pixel_counts + secondary_errmat_pixel_counts)*0.5
    mean_errmat_pixel_area = (primary_errmat_pixel_area + secondary_errmat_pixel_area)*0.5

    classcode = np.array(primary_errmat_pixel_counts.index)
    if imgfiles is not None:
        npts_list = [ getSampleNumPts(imgf, prow, pcol, inptsB=inptsB, outptsB=outptsB) for imgf, prow, pcol in itertools.izip(imgfiles, pixel_row_list, pixel_col_list) ]
        class_npts_list, nonclass_npts_list = zip(*npts_list)
        primary_errmat_point_counts = \
            estErrorMatrix_Pixel2Points(np.hstack(class_label_list).astype(np.int), \
                                            np.hstack(primary_label_list).astype(np.int), \
                                            np.hstack(class_npts_list).astype(np.int), \
                                            np.hstack(nonclass_npts_list).astype(np.int))

        secondary_errmat_point_counts = \
            estErrorMatrix_Pixel2Points(np.hstack(class_label_list).astype(np.int), \
                                            np.hstack(secondary_label_list).astype(np.int), \
                                            np.hstack(class_npts_list).astype(np.int), \
                                            np.hstack(nonclass_npts_list).astype(np.int))

        mean_errmat_point_counts = (primary_errmat_point_counts + secondary_errmat_point_counts)*0.5

        tmp = [ getTotalNumPts(imgf, classcode, countpixel=True, inptsB=inptsB, outptsB=outptsB) for imgf in imgfiles ]
        total_npts_list, npixel_list = zip(*tmp)
        total_npts = np.sum(np.array(total_npts_list), axis=0)
        total_npixel = np.sum(np.array(npixel_list), axis=0).astype(np.float)

        primary_errmat_pixel_counts = ErrorMatrixSummary(primary_errmat_pixel_counts, total_npixel)
        secondary_errmat_pixel_counts = ErrorMatrixSummary(secondary_errmat_pixel_counts, total_npixel)
        mean_errmat_pixel_counts = ErrorMatrixSummary(mean_errmat_pixel_counts, total_npixel)

        primary_errmat_point_counts = ErrorMatrixSummary(primary_errmat_point_counts, total_npts)
        secondary_errmat_point_counts = ErrorMatrixSummary(secondary_errmat_point_counts, total_npts)
        mean_errmat_point_counts = ErrorMatrixSummary(mean_errmat_point_counts, total_npts)

    with open(outfile, 'w') as outfobj:
        outfobj.write("Report on Classification Accuracy Assessment of DWEL point cloud\n")
        outfobj.write("Run made at: "+time.strftime("%c")+"\n")
        outfobj.write("\n")
        outfobj.write("# Primary ground truth labels\n")
        outfobj.write("=============================\n")
        outfobj.write("\n")
        outfobj.write("## pixel counts\n")
        primary_errmat_pixel_counts.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        outfobj.write("## pixel area\n")
        primary_errmat_pixel_area.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        if imgfiles is not None:
            outfobj.write("## point counts\n")
            primary_errmat_point_counts.to_csv(outfobj, mode="a", float_format="%.3f")
            outfobj.write("\n")

        outfobj.write("# Secondary ground truth labels\n")
        outfobj.write("===============================\n")
        outfobj.write("\n")
        outfobj.write("## pixel counts\n")
        secondary_errmat_pixel_counts.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        outfobj.write("## pixel area\n")
        secondary_errmat_pixel_area.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        if imgfiles is not None:
            outfobj.write("## point counts\n")
            secondary_errmat_point_counts.to_csv(outfobj, mode="a", float_format="%.3f")
            outfobj.write("\n")

        outfobj.write("# Mean of primary and secondary ground truth labels\n")
        outfobj.write("===================================================\n")
        outfobj.write("\n")
        outfobj.write("## pixel counts\n")
        mean_errmat_pixel_counts.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        outfobj.write("## pixel area\n")
        mean_errmat_pixel_area.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        if imgfiles is not None:
            outfobj.write("## point counts\n")
            mean_errmat_point_counts.to_csv(outfobj, mode="a", float_format="%.3f")
            outfobj.write("\n")


def ErrorMatrixSummary(errmat, Ni):
    """
    Ni: total number of classified points in each class
    """
    errmat_summary = errmat.copy()
    Ni = Ni.astype(np.float)
    errmat_summary['Ui'] = np.zeros(errmat_summary.shape[0])
    errmat_summary['S(Ui)'] = np.zeros(errmat_summary.shape[0])
    tmpdf = pd.DataFrame([np.zeros(errmat_summary.shape[1]), np.zeros(errmat_summary.shape[1])], columns=errmat_summary.columns)
    errmat_summary = errmat_summary.append(tmpdf, ignore_index=True)
    newindex = errmat.index.tolist()
    newindex.append('Pj')
    newindex.append('S(Pj)')
    errmat_summary['index'] = newindex
    errmat_summary = errmat_summary.set_index('index')
    errmat_summary.index.names = [None]

    # user's accuracy and its variance
    for cls in errmat.index:
        ni = np.sum(errmat_summary.loc[cls, errmat.columns])
        errmat_summary.loc[cls, 'Ui'] = errmat_summary.loc[cls, cls]/ni
        errmat_summary.loc[cls, 'S(Ui)'] = np.sqrt(errmat_summary.loc[cls, 'Ui']*(1-errmat_summary.loc[cls, 'Ui'])/(ni-1))

    # producer's accuracy and its variance
    ni = np.sum(errmat, axis=1)
    nj = np.sum(errmat, axis=0)
    nij_to_ni = errmat/np.tile(ni, (2, 1)).T
    Nj = nij_to_ni * np.tile(Ni, (2, 1)).T
    Nj = np.sum(Nj, axis=0)
    for truth in errmat.columns:
        errmat_summary.loc['Pj', truth] = errmat_summary.loc[truth, truth]/np.sum(errmat_summary.loc[errmat.index, truth])

        tmpbool = errmat.index!=truth
        tmp_nij_to_ni = nij_to_ni.loc[tmpbool, truth]
        VPj = Ni[tmpbool]**2*tmp_nij_to_ni*(1-tmp_nij_to_ni)/(ni[tmpbool]-1)
        VPj = np.sum(VPj)
        VPj = VPj * errmat_summary.loc['Pj', truth]**2

        leftVPj = Nj.loc[truth]**2*(1-errmat_summary.loc['Pj', truth])**2
        leftVPj = leftVPj*errmat_summary.loc[truth, 'Ui']*(1-errmat_summary.loc[truth, 'Ui'])
        leftVPj = leftVPj/(nj.loc[truth]-1)
        VPj = (VPj + leftVPj)/Nj.loc[truth]**2

        errmat_summary.loc['S(Pj)', truth] = np.sqrt(VPj)

    # overall accuracy and its variance
    errmat_summary.loc['Pj', 'Ui'] = np.sum(np.diagonal(errmat))/np.sum(errmat.as_matrix())
    Wi = Ni/np.sum(Ni)
    VO = Wi**2*errmat_summary.loc[errmat.index, 'Ui']*(1-errmat_summary.loc[errmat.index, 'Ui'])/(ni-1)
    VO = np.sum(VO)
    errmat_summary.loc['S(Pj)', 'S(Ui)'] = np.sqrt(VO)
    return errmat_summary

def getTotalNumPts(imgfile, classcode, countpixel=False, classB=1, maskB=2, inptsB=3, outptsB=4):
    """
    ONLY works for TWO-class scenario

    countpixel (boolean): if return counts of pixels for each class
    """
    imgds = gdal.Open(imgfile, gdal.GA_ReadOnly)
    classband = imgds.GetRasterBand(classB)
    maskband = imgds.GetRasterBand(maskB)
    inptsband = imgds.GetRasterBand(inptsB)
    outptsband = imgds.GetRasterBand(outptsB)

    classimg = classband.ReadAsArray(0, 0, classband.XSize, classband.YSize)
    maskimg = maskband.ReadAsArray(0, 0, maskband.XSize, maskband.YSize)
    inptsimg = inptsband.ReadAsArray(0, 0, inptsband.XSize, inptsband.YSize)
    outptsimg = outptsband.ReadAsArray(0, 0, outptsband.XSize, outptsband.YSize)

    maskimg = maskimg.astype(np.bool)
    selectclass = classimg[maskimg]
    selectinpts = inptsimg[maskimg]
    selectoutpts = outptsimg[maskimg]
#    classcode = np.unique(selectclass)
    inpts_total = np.array([ np.sum(selectinpts[selectclass==cls]) for cls in classcode ])
    outpts_total = np.array([ np.sum(selectoutpts[selectclass==cls]) for cls in classcode ])

    if countpixel:
        pixel_count = np.array([ np.sum(selectclass==cls) for cls in classcode ])

    imgds = None
    return inpts_total + outpts_total[::-1], pixel_count


def getSampleNumPts(imgfile, pixel_row, pixel_col, inptsB=3, outptsB=4):
    pixel_row = pixel_row.astype(np.int)
    pixel_col = pixel_col.astype(np.int)
    imgds = gdal.Open(imgfile, gdal.GA_ReadOnly)
    inptsband = imgds.GetRasterBand(inptsB)
    outptsband = imgds.GetRasterBand(outptsB)
    inptsimg = inptsband.ReadAsArray(0, 0, inptsband.XSize, inptsband.YSize)
    outptsimg = outptsband.ReadAsArray(0, 0, outptsband.XSize, outptsband.YSize)

    class_npts = inptsimg[pixel_row, pixel_col]
    nonclass_npts = outptsimg[pixel_row, pixel_col]

    imgds = None

    return class_npts, nonclass_npts

def calcErrorMatrix(class_label, truth_label, weights=None):
    """
    Calculate error matrix from labels of classification and ground truth.

    class_label (1D numpy array, int): labels of classification

    truth_label (1D numpy array, int): labels of ground truth

    weights (1D numpy array, float): weights of each pair of class and truth in
    the calculation of error matrix, e.g. area represented by each
    pixel/points. default: all weights are one.
    """

    tmpclass = np.unique(class_label)
    tmptruth = np.unique(truth_label)
    class_code = np.union1d(tmpclass, tmptruth)
    nclass = len(class_code)
    errmat = pd.DataFrame(data=np.zeros((nclass, nclass)), index=class_code, columns=class_code)
    if weights is None:
        weights = np.ones_like(class_label)
    for i, (c, t) in enumerate(itertools.izip(class_label, truth_label)):
        errmat.loc[c, t] += weights[i]

    return errmat

def estErrorMatrix_Pixel2Points(class_label, truth_label, class_npts, nonclass_npts):
    """
    Estimate error matrices in terms of number of points for best and worst
    possible scenarios based on classification and ground truth labels of
    pixels.

    ONLY works for TWO-class classification.

    class_label (1D numpy array, int): labels of classification

    truth_label (1D numpy array, int): labels of ground truth

    class_npts (1D numpy array, int): number of points in a pixel that have the
    assigned pixel class label.

    nonclass_npts (1D numpy array, int): number of points in a pixel that do not
    have the assigned pixel class label.
    """
    tmpclass = np.unique(class_label)
    tmptruth = np.unique(truth_label)
    class_code = np.union1d(tmpclass, tmptruth)
    nclass = len(class_code)
    errmat = pd.DataFrame(data=np.zeros((nclass, nclass)), index=class_code, columns=class_code)
    weights = class_npts + nonclass_npts
    npts_class = np.zeros(2)
    for i, (c, t, cn, ncn) in enumerate(itertools.izip(class_label, truth_label, class_npts, nonclass_npts)):
        tmpind = np.where(class_code == c)[0]
        npts_class[tmpind] = cn
        npts_class[1-tmpind] = ncn
        truth_label_ind = np.where(class_code == t)[0]
        errmat += estPtsErrorMatrix(npts_class, truth_label_ind)*weights[i]

    return errmat

def estPtsErrorMatrix(npts_class, truth_label_ind):
    """
    Infer the error matrix in terms of proportion of points in a projection bin
    according to the ground truth label for the mode of point class and the
    number of points for each class.

    ONLY works for TWO-class scenario.

    npts_class (1D numpy array, int): number of points for each class

    truth_label_ind (scalar, int): the index to the class that is the ground
    truth.
    """
    npts = np.sum(npts_class).astype(np.int)
    def gen_npts_truth(nt, truth_label_ind, npts):
        npts_truth = np.array([0, 0])
        npts_truth[truth_label_ind] = nt
        npts_truth[1 - truth_label_ind] = npts - nt
        return npts_truth.copy()
    npts_truth_list = [ gen_npts_truth(nt, truth_label_ind, npts) for nt in range(np.fix(npts*0.5).astype(np.int)+1, npts+1) ] 
    errmat_pts_list = [ enumeratePtsErrorMatrices(npts_class, npts_truth) for npts_truth in npts_truth_list ]
    errmat_pts_all, n_errmat_list = zip(*errmat_pts_list)
    errmat_pts_total = reduce(lambda m1,m2:m1+m2, errmat_pts_all)
    return errmat_pts_total/(float(npts)*np.sum(n_errmat_list))

def enumeratePtsErrorMatrices(npts_class, npts_truth):
    """
    Enumerate all possible error matrices according to the number of points of
    each class label and the number of points of each ground truth label.

    ONLY works for TWO-class scenario
    """
    npts_class = npts_class.astype(np.int)
    npts_truth = npts_truth.astype(np.int)
    nclass = len(npts_class)
    if len(npts_truth) != nclass:
        raise RuntimeError("npts_class and npts_truth must have the same number of elements")
    npts_total = np.sum(npts_class)
    if npts_total != np.sum(npts_truth):
        raise RuntimeError("total number of points by npts_class and npts_truth must be the same")
    errmat = pd.DataFrame(data=np.zeros((nclass, nclass)), index=npts_class, columns=npts_truth)
    min_npts_class = np.min(npts_class)
    min_npts_truth = np.min(npts_truth)
    def updateErrorMatrix(errmat, irow, icol, value):
        errmat.iloc[irow, icol] = value
        errmat.iloc[irow, 1-icol] = errmat.index[irow] - errmat.iloc[irow, icol]
        errmat.iloc[1-irow, icol] = errmat.columns[icol] - errmat.iloc[irow, icol]
        errmat.iloc[1-irow, 1-icol] = errmat.index[1-irow] - errmat.iloc[1-irow, icol]
        # double check
        if np.sum(errmat.as_matrix())!=np.sum(np.array(errmat.index)) or \
                np.sum(errmat.as_matrix())!=np.sum(np.array(errmat.columns)):
            raise RuntimeError("updateErrorMatrix went wrong")
        return errmat
    if min_npts_class < min_npts_truth:
        irow = np.argmin(npts_class)
        icol = 0
        errmat_list = [ updateErrorMatrix(errmat.copy(), irow, icol, value) for value in range(min_npts_class+1) ]
    else:
        irow = 0
        icol = np.argmin(npts_truth)
        errmat_list = [ updateErrorMatrix(errmat.copy(), irow, icol, value) for value in range(min_npts_truth+1) ]

    errmat_total = reduce(lambda m1, m2: m1+m2, errmat_list)
    return errmat_total.as_matrix(), len(errmat_list)


if __name__=="__main__":
    cmdargs = getCmdArgs()
#    estPtsErrorMatrix(np.array([9, 2]), 0)
    main(cmdargs)
