#!/usr/bin/env python
"""Accuracy assessment of DWEL point cloud classification of two
classes (leaf vs wood) by comparing hemiphotos and hemi-projection of
point cloud. This accuracy assessment from hemi-pixels to points uses
an enumaration of all possible point labels that gives us the
hemi-pixel labels. It ONLY works for two-class classification scheme
for now.

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

    p.add_argument("--csv", dest="csv", nargs='+', required=True, default=None, help="CSV files of 'ground truth' data, with the columns in order from the first to last: pixel_X(image sample/column), pixel_Y(image line/row), pixel_value(can be empty), primary_truth_label,secondary_truth_label, truth_label_confidence(optional).")
    p.add_argument("--cls", dest="cls", nargs="+", required=True, default=None, help="ENVI image files of the projections of DWEL point cloud classification.")
    p.add_argument("--img", dest="img", nargs='+', required=False, default=None, help="ENVI image files of extra information for accuracy assessment, providing number of points both included and excluded per pixel/projection bin in the projection images. When this extra informatinon is provided, pixel-based accuracy assessment over projection images will be converted to point-based assessment by enumerating all possible point labels per pixel that gives the projection pixel label. It ONLY works for two-class classification scheme for now.")
    p.add_argument("-o", "--outfile", dest="outfile", required=True, default=None, help="Output file of accuracy assessment summary.")

    p.add_argument("--inptsB", dest="inptsB", type=int, default=3, help="In the ENVI image file, the band index of the number of points included in generation of pixel values of projection images from DWEL point cloud, with first band being 1. Default: 3.")
    p.add_argument("--outptsB", dest="outptsB", type=int, default=4, help="In the ENVI image file, the band index of the number of points NOT included in generation of pixel values of projection images from DWEL point cloud, with first band being 1. Default: 4.")

    p.add_argument("--zerozen", dest='zerozen', type=int, nargs=2, metavar=('zerozen_row', 'zerozen_col'), default=(1022, 1022), help='Location of zero zenith in the projection images. Default: (1022, 1022)')
    p.add_argument("--inres", dest="inres", type=float, default=2.0, help="Resolution of input projection images. Unit: mrad. Default: 2.0 mrad.")

    cmdargs = p.parse_args()

    nfiles = len(cmdargs.csv)
    if nfiles != len(cmdargs.cls):
        p.print_help()
        msgstr = "Number of CSV files of ground truth must be the same as the number of ENVI image files of the projection DWEL point cloud classification."
        raise RuntimeError(msgstr)
    if cmdargs.img is not None:
        if len(cmdargs.img) != nfiles:
            p.print_help()
            raise RuntimeError("Number of CSV files of ground truth must be the same as the number of ENVI image files of extra information if you give the ENVI image files of extra information.")

    return cmdargs

def main(cmdargs):
    csvfiles = cmdargs.csv
    clsfiles = cmdargs.cls
    imgfiles = cmdargs.img
    outfile = cmdargs.outfile

    inptsB = cmdargs.inptsB
    outptsB = cmdargs.outptsB

    inresolution = cmdargs.inres*1e-3
    zerozen = cmdargs.zerozen

    # read CSV file
    groundtruth_list = [ np.genfromtxt(csv, delimiter=',', skip_header=1) for csv in csvfiles ]

    # Somehow the Y/row/line of ground truth sample pixels are in
    # negative values in my current data. The input data in future
    # needs be fixed and the code here be fixed as well!
    pixel_row_list = [ (gt[:, 1] + 0.5)*-1 for gt in groundtruth_list ]
    pixel_col_list = [ gt[:, 0] - 0.5 for gt in groundtruth_list ]

    # error matrix by number of pixels
    # class_label_list = [ gt[:, 2] for gt in groundtruth_list ]
    class_label_list = [ getClassCode(clsf, prow, pcol) for clsf, prow, pcol in itertools.izip(clsfiles, pixel_row_list, pixel_col_list)]
    primary_label_list = [ gt[:, 3] for gt in groundtruth_list ]
    secondary_label_list = [ gt[:, 4] for gt in groundtruth_list ]

    pixel_zen = np.sqrt((np.hstack(pixel_row_list)-zerozen[0])**2+(np.hstack(pixel_col_list)-zerozen[1])**2)*inresolution
    # Because larger zenith angles have more pixels in the
    # hemi-projection, hence larger probability to have more samples
    # from these larger zenith angles, and thus the weight needs to be
    # the inverse of zenith angles to account for the zenith ring areas
    # for pixels in the hemi-projection.
    pixel_zen[np.abs(pixel_zen)<1e-10] = inresolution / (2*np.pi)
    weights = 1./pixel_zen

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
        tmp = [ getTotalNumPts(clsf, imgf, classcode, inptsB=inptsB, outptsB=outptsB, \
                               pixelcount=True, pixelarea=True, zerozen=zerozen, pixelres=inresolution) \
                for clsf, imgf in itertools.izip(clsfiles, imgfiles) ]
        total_npts_list, npixel_list, pixelarea_list = zip(*tmp)
        total_npts = np.sum(np.array(total_npts_list), axis=0)
        total_npixel = np.sum(np.array(npixel_list), axis=0).astype(np.float)
        total_pixelarea = np.sum(np.array(pixelarea_list), axis=0)
        
        # inclusion probability of each pixel for primary labels
        n_i_dot = np.array([np.sum(class_label_list==cls) for cls in classcode])
        tmp = total_npixel / n_i_dot
        pixel_weights = weights * np.array([tmp[np.where(classcode==cll)[0][0]] for cll in np.hstack(class_label_list).astype(np.int)])
        # normalize the pixel_weights such that the total number of
        # points from the pixels will remain unchanged.
        pixel_weights = pixel_weights / np.sum(pixel_weights)

        npts_list = [ getSampleNumPts(imgf, prow, pcol, inptsB=inptsB, outptsB=outptsB) for imgf, prow, pcol in itertools.izip(imgfiles, pixel_row_list, pixel_col_list) ]
        class_npts_list, nonclass_npts_list = zip(*npts_list)
        primary_errmat_point_counts = \
            estErrorMatrix_Pixel2Points(np.hstack(class_label_list).astype(np.int), \
                                        np.hstack(primary_label_list).astype(np.int), \
                                        np.hstack(class_npts_list).astype(np.int), \
                                        np.hstack(nonclass_npts_list).astype(np.int), \
                                        pixel_weights=pixel_weights)

        secondary_errmat_point_counts = \
            estErrorMatrix_Pixel2Points(np.hstack(class_label_list).astype(np.int), \
                                        np.hstack(secondary_label_list).astype(np.int), \
                                        np.hstack(class_npts_list).astype(np.int), \
                                        np.hstack(nonclass_npts_list).astype(np.int), \
                                        pixel_weights=pixel_weights)

        mean_errmat_point_counts = (primary_errmat_point_counts + secondary_errmat_point_counts)*0.5

        primary_errmat_pixel_counts = ErrorMatrixSummary(primary_errmat_pixel_counts, total_npixel)
        secondary_errmat_pixel_counts = ErrorMatrixSummary(secondary_errmat_pixel_counts, total_npixel)
        mean_errmat_pixel_counts = ErrorMatrixSummary(mean_errmat_pixel_counts, total_npixel)

        primary_errmat_pixel_area = ErrorMatrixSummary(primary_errmat_pixel_area, total_npixel)
        secondary_errmat_pixel_area = ErrorMatrixSummary(secondary_errmat_pixel_area, total_npixel)
        mean_errmat_pixel_area = ErrorMatrixSummary(mean_errmat_pixel_area, total_npixel) 

        primary_errmat_point_counts = ErrorMatrixSummary(primary_errmat_point_counts, total_npts)
        secondary_errmat_point_counts = ErrorMatrixSummary(secondary_errmat_point_counts, total_npts)
        mean_errmat_point_counts = ErrorMatrixSummary(mean_errmat_point_counts, total_npts)

    with open(outfile, 'w') as outfobj:
        outfobj.write("Report on Classification Accuracy Assessment of DWEL point cloud\n")
        outfobj.write("Run made at: "+time.strftime("%c")+"\n")
        outfobj.write("\n")
        outfobj.write("# Inputs for this assessment\n")
        outfobj.write("============================\n")
        outfobj.write("\n")
        outfobj.write("## CSV files of grouth truth data\n")
        outfobj.write("\n".join(csvfiles))
        outfobj.write("\n")
        outfobj.write("\n")
        outfobj.write("## Projection images of point cloud classifications\n")
        outfobj.write("\n".join(clsfiles))
        outfobj.write("\n")
        outfobj.write("\n")
        if imgfiles is not None:
            outfobj.write("## Extra information images for projection images of classifications\n")
            outfobj.write("\n".join(imgfiles))
            outfobj.write("\n")
            outfobj.write("\n")
            outfobj.write("# Distribution of classes\n")
            outfobj.write("=========================\n")
            outfobj.write("\n")
            outfobj.write("## Number of pixels in mapped classes\n")
            outfobj.write(",".join([ "{0:d}".format(n) for n in range(len(total_npixel)) ]))
            outfobj.write("\n")
            outfobj.write(",".join([ "{0:d}".format(int(n)) for n in total_npixel ]))
            outfobj.write("\n")
            outfobj.write("\n")
            outfobj.write("## Number of pixels corrected for projection area of zenith rings in mapped classes\n")
            outfobj.write(",".join([ "{0:d}".format(n) for n in range(len(total_pixelarea)) ]))
            outfobj.write("\n")
            outfobj.write(",".join([ "{0:d}".format(int(n)) for n in total_pixelarea ]))
            outfobj.write("\n")
            outfobj.write("\n")
            outfobj.write("## Number of points in mapped classes\n")
            outfobj.write(",".join([ "{0:d}".format(n) for n in range(len(total_npts)) ]))
            outfobj.write("\n")
            outfobj.write(",".join([ "{0:d}".format(int(n)) for n in total_npts ]))
            outfobj.write("\n")
            
        outfobj.write("\n")
        outfobj.write("# Primary ground truth labels\n")
        outfobj.write("=============================\n")
        outfobj.write("\n")
        outfobj.write("## pixel counts\n")
        primary_errmat_pixel_counts.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        outfobj.write("## pixel counts corrected for projection area of zenith rings\n")
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
        outfobj.write("## pixel counts corrected for projection area of zenith rings\n")
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
        outfobj.write("## pixel counts corrected for projection area of zenith rings\n")
        mean_errmat_pixel_area.to_csv(outfobj, mode="a", float_format="%.3f")
        outfobj.write("\n")
        if imgfiles is not None:
            outfobj.write("## point counts\n")
            mean_errmat_point_counts.to_csv(outfobj, mode="a", float_format="%.3f")
            outfobj.write("\n")


def ErrorMatrixSummary(con_mat_samp, cls_strata_size):
    """
    con_mat_samp, pandas DataFrame: Nclass x Nclass, error matrix in terms of
    pixel/point counts directly from the samples without
    poststratified correction. rows are mapped, columns are reference.

    cls_strata_size, 1D numpy array: total number of classified points
    in each class used to calculate the proportion of each stratum, or
    you can provide the proportion of each stratum directly.
    """
    errmat = con_mat_samp.copy()
    con_mat_samp = errmat.values

    n_cls = len(con_mat_samp)
    cls_npix = cls_strata_size
    cls_w = cls_npix / float(np.sum(cls_npix))

    # calcualte population confusion matrix in terms of area proportion
    n_i_dot = np.sum(con_mat_samp, axis=1)
    con_mat_pop = np.tile((cls_w / n_i_dot).reshape((n_cls, 1)), (1, n_cls)) * con_mat_samp

    # calcualte user's accuracy
    p_i_dot = np.sum(con_mat_pop, axis=1)
    U = np.array([con_mat_pop[i, i]/p_i_dot[i] for i in range(n_cls)])
    # calculate user's accuracy standard error
    SU = np.sqrt(U * (1. - U) / (n_i_dot-1))

    # calculate overall accuracy
    OA = reduce(lambda x, y: x+y, [con_mat_pop[i, i] for i in range(n_cls)])
    SO = np.sqrt(np.sum(cls_w**2 * U * (1.-U) / (n_i_dot-1)))

    # calculate producer's accuracy
    p_dot_j = np.sum(con_mat_pop, axis=0)
    P = np.array([con_mat_pop[i, i]/p_dot_j[i] for i in range(n_cls)])
    # calculate producer's accuracy standard error
    N_i_dot = cls_npix
    N_dot_j = np.tile((N_i_dot / n_i_dot.astype(float)).reshape((n_cls, 1)), (1, n_cls)) * con_mat_samp
    N_dot_j = np.sum(N_dot_j, axis=0)
    term1 = N_i_dot**2 * (1-P)**2 * U * (1.-U) / (n_i_dot - 1)

    term2 = N_i_dot**2 / n_i_dot.astype(float)
    term2 = np.tile(term2.reshape((n_cls, 1)), (1, n_cls)) * con_mat_samp
    term2 = term2 * (1 - con_mat_samp / np.tile(n_i_dot.reshape((n_cls, 1)), (1, n_cls)))
    term2 = term2 / np.tile(n_i_dot.reshape((n_cls, 1)), (1, n_cls))
    for i in range(n_cls):
        term2[i, i] = 0
    term2 = np.sum(term2, axis=0) * P**2
    SP = np.sqrt((term1 + term2) / N_dot_j**2)

    # calculate estimated proportion of area for classes adjusted for 
    # classification error based on our reference data
    p_dot_k = np.sum(con_mat_pop, axis=0)
    # calculate the standard error of the estimated area proportion
    tmp = np.tile(cls_w.reshape((n_cls, 1)), (1, n_cls)) * con_mat_pop - con_mat_pop**2
    tmp = tmp / (np.tile(n_i_dot.reshape((n_cls, 1)), (1, n_cls)) - 1)
    tmp = np.sum(tmp, axis=0)
    Sp_dot_k = np.sqrt(tmp)

    errmat_summary = pd.DataFrame(errmat, copy=True)
    oldindex = errmat.index.tolist()
    errmat_summary.loc[oldindex, oldindex] = con_mat_pop
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
    errmat_summary.loc[oldindex, 'Ui'] = U
    errmat_summary.loc[oldindex, 'S(Ui)'] = SU
    # producer's accuracy and its variance
    errmat_summary.loc['Pj', oldindex] = P
    errmat_summary.loc['S(Pj)', oldindex] =SP
    # overall accuracy and its variance
    errmat_summary.loc['Pj', 'Ui'] = OA
    errmat_summary.loc['S(Pj)', 'S(Ui)'] = SO

    # for cls in errmat.index:
    #     errmat_summary.loc[cls, 'Ui'] = U
    #     errmat_summary.loc[cls, 'S(Ui)'] = np.sqrt(errmat_summary.loc[cls, 'Ui']*(1-errmat_summary.loc[cls, 'Ui'])/(ni-1))

    # # producer's accuracy and its variance
    # ni = np.sum(errmat, axis=1)
    # nj = np.sum(errmat, axis=0)
    # nij_to_ni = errmat/np.tile(ni, (2, 1)).T
    # Nj = nij_to_ni * np.tile(Ni, (2, 1)).T
    # Nj = np.sum(Nj, axis=0)
    # for truth in errmat.columns:
    #     errmat_summary.loc['Pj', truth] = errmat_summary.loc[truth, truth]/np.sum(errmat_summary.loc[errmat.index, truth])

    #     tmpbool = errmat.index!=truth
    #     tmp_nij_to_ni = nij_to_ni.loc[tmpbool, truth]
    #     VPj = Ni[tmpbool]**2*tmp_nij_to_ni*(1-tmp_nij_to_ni)/(ni[tmpbool]-1)
    #     VPj = np.sum(VPj)
    #     VPj = VPj * errmat_summary.loc['Pj', truth]**2

    #     leftVPj = Nj.loc[truth]**2*(1-errmat_summary.loc['Pj', truth])**2
    #     leftVPj = leftVPj*errmat_summary.loc[truth, 'Ui']*(1-errmat_summary.loc[truth, 'Ui'])
    #     leftVPj = leftVPj/(nj.loc[truth]-1)
    #     VPj = (VPj + leftVPj)/Nj.loc[truth]**2

    #     errmat_summary.loc['S(Pj)', truth] = np.sqrt(VPj)

    # # overall accuracy and its variance
    # errmat_summary.loc['Pj', 'Ui'] = np.sum(np.diagonal(errmat))/np.sum(errmat.as_matrix())
    # Wi = Ni/np.sum(Ni)
    # VO = Wi**2*errmat_summary.loc[errmat.index, 'Ui']*(1-errmat_summary.loc[errmat.index, 'Ui'])/(ni-1)
    # VO = np.sum(VO)
    # errmat_summary.loc['S(Pj)', 'S(Ui)'] = np.sqrt(VO)

    return errmat_summary

def getTotalNumPts(clsfile, imgfile, classcode, maskB=2, inptsB=3, outptsB=4, \
                   pixelcount=False, pixelarea=False, zerozen=None, pixelres=None):
    """
    ONLY works for TWO-class scenario

    pixelcount (boolean): if return counts of pixels for each class
    pixelarea (boolean): if return areas of pixels according to the solid angle coverage
    zerozen (two-element sequence): pixel location of zero zenith angle, [row, col]
    pixeres (float): angular resolution of pixel, unit: radian.
    """
    imgds = gdal.Open(imgfile, gdal.GA_ReadOnly)
    clsds = gdal.Open(clsfile, gdal.GA_ReadOnly)
    classband = clsds.GetRasterBand(1)
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
    inpts_total = np.array([ np.sum(selectinpts[selectclass==cls]) for cls in classcode ])
    outpts_total = np.array([ np.sum(selectoutpts[selectclass==cls]) for cls in classcode ])

    out_tuple = (inpts_total + outpts_total[::-1],)
    if pixelcount:
        pixel_count = np.array([ np.sum(selectclass==cls) for cls in classcode ])
        out_tuple = out_tuple + (pixel_count,)

    if pixelarea:
        if zerozen is None or pixelres is None:
            msgstr = "getTotalNumPts: keyword arguments zerozen and pixelres are required if pixelarea is set True to calculate pixel areas according to the solid angle by weighting sin(zenith_angle)"
            raise RuntimeError(msgstr)
        clsrows, clscols = np.where(maskimg)
        clszen = np.sqrt((clsrows-zerozen[0])**2+(clscols-zerozen[1])**2)*pixelres
        clszen[np.abs(clszen)<1e-10] = pixelres/(2.*np.pi)
        clsweights = 1./clszen
        pixel_area = np.array([np.sum(clsweights[selectclass==cls]) for cls in classcode])
        out_tuple = out_tuple + (pixel_area,)

    imgds = None
    clsds = None
    return  out_tuple


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

def getClassCode(clsimg, pixel_row, pixel_col, clsB=1):
    pixel_row = pixel_row.astype(np.int)
    pixel_col = pixel_col.astype(np.int)
    imgds = gdal.Open(clsimg, gdal.GA_ReadOnly)
    clsband = imgds.GetRasterBand(clsB)
    clsdata = clsband.ReadAsArray(0, 0, clsband.XSize, clsband.YSize)    
    clscode = clsdata[pixel_row, pixel_col]
    imgds = None

    return clscode

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

def estErrorMatrix_Pixel2Points(class_label, truth_label, class_npts, nonclass_npts, pixel_weights=None):
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
    if pixel_weights is None:
        pixel_weights = np.ones_like(class_label)
    weights = (class_npts + nonclass_npts) * pixel_weights
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
    main(cmdargs)
