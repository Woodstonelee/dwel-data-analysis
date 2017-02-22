#!/usr/bin/env python
"""
Project point cloud of a single scan to hemispherical image. Specially for
projecting classified points. The projection function of the virtual lens of
hemispherical images uses equidistant projection that maintains angular
distance, that is distance from image center (zenith point),
r=focal_length*theta. focal_length here is not the actual lens focal length but
also including the CCD effect that relates distance between an image point and
CCD frame center to number of pixels. Here we assume a normalized focal_length =
1 pixel/angular_resolution, where angular resolution is provided by the user.

Note:

(0) Strictly speaking, the correct way to project classification of points
should be: 1) for each waveform, find the class of maximum return and remove the
other returns from point cloud. 2) assign the mode of point class in a projected
bin. But here for simplicity, we haven't remove non-maximum points in each
waveform and just assigned mode of point class from all points.

(1) DWEL point cloud generation already add instrument height when calculating z
coordinates of points. Thus the coverage of zenith is approximately 90 deg not
original 117 deg set by DWEL instrument case. But azimuth should remain
unchanged except those points with zero zenith angle. We cannot recover their
actual azimuth angle from xyz coordinates since they are at zenith point and
their azimuth from xyz will be simply assigned zero.

(2) Use gdal to write projected image to an ENVI image file and format the
envi header file properly as an ENVI classification file for later
classification accuracy assessment.

USAGE:

OPTIONS:

EXAMPLES:

AUTHORS:

    Zhan Li, zhanli86@bu.edu
"""

import sys
import time
import optparse
import os

from functools import partial

import numpy as np
from scipy import stats as spstats
from osgeo import gdal

import matplotlib as mpl
# mpl.use('TkAgg')
mpl.use('Agg')
import matplotlib.pyplot as plt

gdal.AllRegister()

def hunt_max_return(points):
    """
    Get maximum return for each pulse in the given points, which supplies return
    intensities and shot numbers of points

    Args:

        points (2D numpy array, [npts, 2]): [intensity, shotnum]

    Returns:

        index_max (1D numppy array): indices of maximum returns of all pulses.
    """

    ushotnum, ui, ui_inverse, ucounts \
        = np.unique(points[:, 1].astype(int), return_index=True, return_inverse=True, \
                        return_counts=True)
    index_max = np.zeros_like(ushotnum, dtype=np.int)

    pts_ucounts = ucounts[ui_inverse]
    sortind = np.argsort(points[:,1])
    sortpoints = points[sortind, 0:2]
    pts_ucounts = pts_ucounts[sortind]
    ui_inverse = ui_inverse[sortind]
    p = 0
    while p<len(sortpoints):
        if np.sum(np.fabs(pts_ucounts[p:p+pts_ucounts[p]]-pts_ucounts[p])) > 1e-10:
            print "Error: number of duplicates is wrong"
        tmppoints = sortpoints[p:p+pts_ucounts[p], :]
        tmpsortind = sortind[p:p+pts_ucounts[p]]
        index_max[ui_inverse[p]] = tmpsortind[np.argmax(tmppoints[:, 0])]

        p += pts_ucounts[p]

    # if np.count_nonzero(ucounts>1) > 0:
    #     import pdb; pdb.set_trace()
    
    return index_max

    

def hs_tp2xy(theta, phi):
    """
    Utility function, convert actual theta (zenith) and phi (azimuth) of 3D
    points to normalized coordinates on a hemispherical image. The normalized
    coordinate system is defined as, [0, 0] as zenith point, radius distance to
    [0, 0] equals to one being the 90 deg or pi/2 radians.

    Args:

        theta, phi (1D numpy array): theta and phi of 3D points, unit:
        radians. They MUST have the same length. Note: phi (azimuth) is measured
        from y axis and clockwise, the same definition with actual geographic
        azimuth.

    Returns:

        x, y (1D numpy array): the normalized x and y coordinates on a
        hemispherical image plane.
    """

    r = theta*2/np.pi
    x = r * np.sin(phi)
    y = r * np.cos(phi)
    return x, y

def dwel_points2hsproj2(infile, outfile, \
                           xyzcols, \
                           indexcol, indexfunc, \
                           pixelcol, pixelfunc, \
                           outres=2.0, \
                           minzen=0.0, maxzen=91.0, \
                           pulsemax=True, \
                           camheight=0.0):
    """
    A second version of projecting points to hemispherical images.The coverage
    of pixels in hemi-image overlap each other a bit to reduce holes in the
    projection image, e.g. at 2 mrad resolution, each 2-mrad pixel will take
    points within sqrt(2)*2 mrad from the pixel center. To implement this, for
    each pixel in hemi-image, uses lists to store indices of points that are
    projected to this pixel. Then loop through this array of lists, which could
    be slow. Let's see...

    Args:

        camheight (float): hemi-camera height relative to zero Z point of input
        point cloud.

    Returns:
    
    """
    
    # set debug switch
    debug = True

    # set some parameters for now. may need to move to function argument in
    # future.
    cind = {'shotnum':5, 'd_I_nir':3}
    
    # read points
    print "Loading points"
    points = np.loadtxt(infile, dtype=np.float32, delimiter=',', skiprows=3)
    # preprocess points
    if pulsemax:
        print "Selecting out maximum of each pulse"
        index_max = hunt_max_return(points[:, \
                [cind['d_I_nir'], cind['shotnum']]])
        points = points[index_max, :]
    
    npts = points.shape[0]

    # convert zenith angle range to radians
    maxzen = maxzen / 180.0 * np.pi
    minzen = minzen / 180.0 * np.pi
    outres = outres * 0.001
    # calculate the dimension of hemi-projection image
    zerozenind = np.fix(maxzen / outres).astype(int)
    nrows = zerozenind*2 + 1
    ncols = zerozenind*2 + 1
    tmpvec = np.hstack((np.arange(zerozenind*-1, 0, 1), \
                            np.arange(0, zerozenind+1)))*outres
    outxymax = tmpvec[-1]+outres*0.5
    outxymin = tmpvec[0]-outres*0.5
    outx, outy = np.meshgrid(tmpvec, tmpvec, indexing='ij')
    matzen = np.sqrt(outx**2 + outy**2)
    outmask = np.logical_and(matzen >= minzen, matzen <=maxzen)
    outind = np.where(outmask)
    flatoutind = np.ravel_multi_index(outind, (nrows, ncols))
    # set up a 2D numpy array as the hemi-image
    outimage = np.zeros((nrows, ncols))

    # calculate azimuth angles of all points
    ptsaz = np.arctan2(points[:, xyzcols[0]], points[:, xyzcols[1]])
    # calculate zenith angles of all points
    xoyrg = np.sqrt(points[:, xyzcols[0]]**2 + points[:, xyzcols[1]]**2)
    ptszen = np.arctan2(xoyrg, points[:, xyzcols[2]]-camheight)
    # calculate the pixel location on hemi-image of all points
    ptsoutx, ptsouty = hs_tp2xy(ptszen, ptsaz)
    ptsoutx = ptsoutx*np.pi*0.5
    ptsouty = ptsouty*np.pi*0.5
    ptsoutcol = zerozenind + np.fix(ptsoutx/outres+0.5*np.sign(ptsoutx)).astype(int)
    ptsoutrow = zerozenind - np.fix(ptsouty/outres+0.5*np.sign(ptsouty)).astype(int)

    # set up a 1D numpy array to store flattened indices in hemi-image of all
    # points. if a point is outside the projection extent, its index is assigned
    # -1
    ptsoutind = np.zeros_like(ptsoutrow, dtype=np.int)-1
    # select points inside projection extent
    rowinflag = np.logical_and(ptsoutrow > 0, ptsoutrow < nrows)
    colinflag = np.logical_and(ptsoutcol > 0, ptsoutcol < ncols)
    bothinflag = np.logical_and(rowinflag, colinflag)
    # calcualte the flattened indices in hemi-image of these points
    ptsoutind[bothinflag] = \
        np.ravel_multi_index((ptsoutrow[bothinflag], ptsoutcol[bothinflag]), \
                                 (nrows, ncols))
    # find out those within the defined extent of hemi-projection
    ptsinflag = np.in1d(ptsoutind, flatoutind)
    # If a point is not inside the projection image, its index is assigned -1
    ptsoutind[np.logical_not(ptsinflag)] = -1

    # now set up a tuple of empty list to store indices to points for all
    # pixels in hemi-image
    print "Linking points to hemispherical image"
    pts_pointer = tuple([[] for x in range(nrows*ncols)])
    # the perturbation of points on hemi-projection image plane
    tmpdist = (outres*np.sqrt(2)-outres)*0.5
    pertdist = [-1*tmpdist, 0, tmpdist]
    lravel_multi_index = partial(np.ravel_multi_index, dims=(nrows, ncols))
    lunique = np.unique
    lsign = np.sign
#    import pdb; pdb.set_trace()
    for p in range(npts):
        if ptsoutind[p] == -1:
            continue
        tmpx = [ptsoutx[p]+x for x in pertdist \
                    if ((ptsoutx[p]+x>=outxymin) and (ptsoutx[p]+x<=outxymax))]
        tmpy = [ptsouty[p]+x for x in pertdist \
                    if ((ptsouty[p]+x>=outxymin) and (ptsouty[p]+x<=outxymax))]
        
        tmpoutind = [lravel_multi_index((\
                    zerozenind - np.fix(y/outres+0.5*lsign(y)).astype(int), \
                        zerozenind + np.fix(x/outres+0.5*lsign(x)).astype(int))) \
                         for y in tmpy for x in tmpx]
        tmpoutind = lunique(tmpoutind)
        if len(tmpoutind)<1:
            print "error in linking"
#            import pdb; pdb.set_trace()
        for toi in tmpoutind:
            pts_pointer[toi].append(p)

#    import pdb; pdb.set_trace()

    # projecting points to hemi-image
    print "Projecting!"
    lunravel_index = partial(np.unravel_index, dims=(nrows, ncols))
    for poi in ptsoutind:
        if poi == -1:
            continue
        # get points located in this pixel
        tmppoints = points[pts_pointer[poi], :]
        # which point/points to be used in hs-imag pixel assingment
        if tmppoints.shape[0] == 1:
            # only one point inside this pixel, no need to call indexfunc to
            # choose points. Assign attribute of this point to the pixel
            outimage[lunravel_index(poi)] \
                = np.asscalar(pixelfunc(np.array([tmppoints[0, pixelcol]]), axis=None)[0])
        else:
            # more than one points in this pixel. call indexfunc to choose
            # points to assign this pixel.
            tmpind = indexfunc(tmppoints[:, indexcol])
            tmppoints = tmppoints[tmpind, :]
            # # test
            # tmpu, tmpucounts = np.unique(tmppoints[:, cind['shotnum']], return_counts=True)
            # if np.count_nonzero(tmpucounts>1) > 0:
            #     print "Error, maximum of each pulse are not select out properly"
#            try:
            outimage[lunravel_index(poi)] \
                = np.asscalar(pixelfunc(np.array([tmppoints[:, pixelcol]]), axis=None)[0])
#            except:
#                import pdb; pdb.set_trace()

    plt.figure()
    plt.imshow(outimage)
    plt.savefig("{0:.3f}".format(outres)+"tesths_new.png")

#    import pdb; pdb.set_trace()

    return 0

def dwel_points2hsproj(infile, outfile, \
                           xyzcols, \
                           indexcol, indexfunc, \
                           pixelcol, pixelfunc, \
                           outres=2.0, \
                           minzen=0.0, maxzen=91.0, \
                           pulsemax=True, \
                           camheight=0.0, \
                           classflag=True, \
                           pulsenocol=5, \
                           intensitycol=3):
    """
    Project 3D points to a hemispherical image.

    Args:

        infile:

        outfile:

        xyzcols (list or numpy array of three elements): column indices of X, Y
        and Z coordinates, with first column being 0.

        indexcol:

        indexfunc (function handle): ALWAYS check if input variable to indexfunc
        has more than one element. ONLY pass sequence-like numpy array variable
        to indexfunc, NOT scalar.

        pixelcol:

        pixelfunc:

        outres (float): resolution of hemispherical projection, unit: mrad.

        minzen (float): minimum zenith angle of hemispherical projection, unit:
        deg.

        minzen (float): maximum zenith angle of hemispherical projection, unit:
        deg.

    Returns:
    
    """

    # set debug switch
    debug = False

    # set some parameters for now. may need to move to function argument in
    # future.

    # read points
    print "Loading points"
    points = np.loadtxt(infile, dtype=np.float32, delimiter=',', skiprows=3)
    # preprocess points
    if pulsemax:
        # Now the two indices are used only when pulsemax is switched on. 
        cind = {'shotnum':pulsenocol, 'd_I_nir':intensitycol}
        print "Selecting out maximum of each pulse"
        index_max = hunt_max_return(points[:, \
                [cind['d_I_nir'], cind['shotnum']]])
        points = points[index_max, :]
    
    npts = points.shape[0]

    # convert zenith angle range to radians
    maxzen = maxzen / 180.0 * np.pi
    minzen = minzen / 180.0 * np.pi
    outres = outres * 0.001
    # calculate the dimension of hemi-projection image
    zerozenind = np.fix(maxzen / outres).astype(int)
    nrows = zerozenind*2 + 1
    ncols = zerozenind*2 + 1
    tmpvec = np.hstack((np.arange(zerozenind*-1, 0, 1), \
                            np.arange(0, zerozenind+1)))*outres
    outx, outy = np.meshgrid(tmpvec, tmpvec, indexing='ij')
    matzen = np.sqrt(outx**2 + outy**2)
    outmask = np.logical_and(matzen >= minzen, matzen <=maxzen)
    outind = np.where(outmask)
    flatoutind = np.ravel_multi_index(outind, (nrows, ncols))
    # set up a 2D numpy array as the hemi-image
    outimage = np.zeros((nrows, ncols))
    outimage.fill(np.nan)
    # set up a 2D numpy array to store number of pixels selected for output
    # image and another 2D numpy array to store the number of remaining pixels
    # not selected.
    num_inpts = np.zeros((nrows, ncols))
    num_inpts.fill(np.nan)
    num_outpts = np.zeros((nrows, ncols))
    num_outpts.fill(np.nan)

    # calculate azimuth angles of all points
    ptsaz = np.arctan2(points[:, xyzcols[0]], points[:, xyzcols[1]])
    # calculate zenith angles of all points
    xoyrg = np.sqrt(points[:, xyzcols[0]]**2 + points[:, xyzcols[1]]**2)
    ptszen = np.arctan2(xoyrg, points[:, xyzcols[2]]-camheight)

    # calculate the pixellocation on hemi-image of all points
    ptsoutx, ptsouty = hs_tp2xy(ptszen, ptsaz)
    ptsoutcol = zerozenind + np.fix(ptsoutx*np.pi/2.0/outres+0.5*np.sign(ptsoutx)).astype(int)
    ptsoutrow = zerozenind - np.fix(ptsouty*np.pi/2.0/outres+0.5*np.sign(ptsouty)).astype(int)

    # set up a 1D numpy array to store flattened indices in hemi-image of all
    # points. if a point is outside the projection extent, its index is assigned
    # -1
    ptsoutind = np.zeros_like(ptsoutrow)-1
    # select points inside projection extent
    rowinflag = np.logical_and(ptsoutrow > 0, ptsoutrow < nrows)
    colinflag = np.logical_and(ptsoutcol > 0, ptsoutcol < ncols)
    bothinflag = np.logical_and(rowinflag, colinflag)
    # calcualte the flattened indices in hemi-image of these points
    ptsoutind[bothinflag] = \
        np.ravel_multi_index((ptsoutrow[bothinflag], ptsoutcol[bothinflag]), \
                                 (nrows, ncols))
    # find out those within the defined extent of hemi-projection
    ptsinflag = np.in1d(ptsoutind, flatoutind)
    # If a point is not inside the projection image, its index is assigned -1
    ptsoutind[np.logical_not(ptsinflag)] = -1
    # Now sorted the flattened indices in hemi-image of all points and record
    # the indices of each point in original input point cloud.
    ptsinind = np.argsort(ptsoutind)
    ptsoutind = ptsoutind[ptsinind]
    # find out each hemi-image pixel has how many points are located inside.
    junk, ui_inverse, ucounts = \
        np.unique(ptsoutind, return_inverse=True, return_counts=True)
    ptsoutcounts = ucounts[ui_inverse]
    # number of points outside projection extent, i.e. ptsoutind == -1
    ninvalid = np.sum(ptsoutind==-1)
    # from valid points inside the projection extent, start projecting!
    print "Projecting!"
    p = ninvalid
    while p < npts:
        # flattened indice in hemi-image of current pixel to be assigned value
        currentoutind = ptsoutind[p]
        if debug:
            # check if count of points in a pixel is correct
            if np.sum(np.fabs(ptsoutcounts[p:p+ptsoutcounts[p]]-ptsoutcounts[p])) > 1e-10:
                print "Error, counts of points in a projected is wrong at " \
                    +"{0:d}".format(p)
        # get points located in this pixel
        tmppoints = points[ptsinind[p:p+ptsoutcounts[p]], :]
        # pixel location to be assigned in the hemi-image
        pixel_loc = np.unravel_index(currentoutind, (nrows, ncols))
        # which point/points to be used in hs-imag pixel assingment
        if tmppoints.shape[0] == 1:
            # only one point inside this pixel, no need to call indexfunc to
            # choose points. Assign attribute of this point to the pixel
            outimage[pixel_loc] \
                = np.asscalar(pixelfunc(np.array([tmppoints[0, pixelcol]])))
            num_inpts[pixel_loc] = 1
            num_outpts[pixel_loc] = 0
        else:
            # more than one points in this pixel. call indexfunc to choose
            # points to assign this pixel.
            tmpind = indexfunc(tmppoints[:, indexcol])
            tmpnum_in = len(tmpind)
            tmpnum_out = len(tmppoints) - tmpnum_in
            num_inpts[pixel_loc] = tmpnum_in
            num_outpts[pixel_loc] = tmpnum_out
            tmppoints = tmppoints[tmpind, :]
            if debug and pulsemax:
                # test
                tmpu, tmpucounts = np.unique(tmppoints[:, cind['shotnum']], return_counts=True)
                if np.count_nonzero(tmpucounts>1) > 0:
                    print "Error, maximum of each pulse are not select out properly"
#            import pdb; pdb.set_trace()
            outimage[pixel_loc] \
                = np.asscalar(pixelfunc(np.array([tmppoints[:, pixelcol]])))
            if classflag:
                # num_inpts then stores the number of points of the assigned
                # class to the pixel
                tmpnum_in = np.sum(tmppoints[:, pixelcol] == outimage[pixel_loc])
                tmpnum_out = len(tmppoints) - tmpnum_in
                num_inpts[pixel_loc] = tmpnum_in
                num_outpts[pixel_loc] = tmpnum_out

        # go to next hemi-image pixel
        p += ptsoutcounts[p]

    # before export the image, transpose the array so that it conforms with the
    # view from bottom to up
    outimage = np.transpose(outimage)
    num_inpts = np.transpose(num_inpts)
    num_outpts = np.transpose(num_outpts)
    # export image resolution
    dpi = 72
    # get image size
    outwidth = outimage.shape[1]/float(dpi)
    outheight = outimage.shape[0]/float(dpi)
    outimage_masked = np.ma.masked_where(np.isnan(outimage), outimage)
    outpngfile = outfile.rsplit(".")
    outpngfile = ".".join(outpngfile[0:-1])
    # plt.figure()
    # plt.axis("off")
    # plt.imshow(outimage_masked, vmin=np.percentile(outimage[~np.isnan(outimage)], 2), \
    #                vmax=np.percentile(outimage[~np.isnan(outimage)], 98))
    # plt.savefig(outpngfile+".png", dpi=dpi, bbox_inches="tight")

    if classflag:
        mpl.image.imsave(outpngfile+".png", outimage_masked, dpi=dpi, \
                             vmin=np.percentile(outimage[~np.isnan(outimage)], 2), \
                             vmax=np.percentile(outimage[~np.isnan(outimage)], 98), \
                             cmap=plt.get_cmap("RdYlGn"))

        outimagemask = np.isnan(outimage)
        # now write projection image to ENVI classification file
        outimage[outimagemask] = 0
        outimage.astype(np.uint8)
        outformat = "ENVI"
        driver = gdal.GetDriverByName(outformat)
        outds = driver.Create(outfile, outimage.shape[1], outimage.shape[0], 1, gdal.GDT_Byte)
        outds.GetRasterBand(1).WriteArray(outimage)
        outds.FlushCache()
        # close the dataset
        outds = None
        # Now write envi header file manually. NOT by gdal...which can't do this
        # job...  set header file
        # get header file name
        strlist = outfile.rsplit('.')
        hdrfile = ".".join(strlist[0:-1]) + ".hdr"
        if os.path.isfile(hdrfile):
            os.remove(hdrfile)
            print "Old header file removed: " + hdrfile 
        hdrfile = outfile + ".hdr"
        hdrstr = \
            "ENVI\n" + \
            "description = {\n" + \
            "Hemispherical projection image of DWEL classification of point cloud, \n" + \
            infile + ", \n" + \
            "Create, [" + time.strftime("%c") + "], \n" + \
            "Camera height for projection, {0:f}}}\n".format(camheight) + \
            "samples = " + "{0:d}".format(outimage.shape[1]) + "\n" \
            "lines = " + "{0:d}".format(outimage.shape[0]) + "\n" \
            "bands = 1\n" + \
            "header offset = 0\n" + \
            "file type = ENVI classification\n" + \
            "data type = 1\n" + \
            "interleave = bsq\n" + \
            "sensor type = Unknown\n" + \
            "byte order = 0\n" + \
            "wavelength units = unknown\n" + \
            "band names = {DWEL Classification}\n" + \
            "classes = 3\n" + \
            "class names = {Unclassified, Others, Leaves}\n" + \
            "class lookup = {0,  0,  0, 255,  0,  0,  0, 255,  0}"
        with open(hdrfile, 'w') as hdrf:
            hdrf.write(hdrstr)

        # prepare a file name for writing an extra ENVI file of output image,
        # mask and number of points in each pixel
        strlist = outfile.rsplit('.')
        outfile = ".".join(strlist[0:-1]) + "_extrainfo.img"

    else:
        mpl.image.imsave(outpngfile+".png", outimage_masked, dpi=dpi, \
                             vmin=np.percentile(outimage[~np.isnan(outimage)], 2), \
                             vmax=np.percentile(outimage[~np.isnan(outimage)], 98), \
                             cmap=plt.get_cmap("jet"))

        outimagemask = np.isnan(outimage)
        outimage[outimagemask] = 0
        
    num_inpts[outimagemask] = 0
    num_outpts[outimagemask] = 0
    # now write projection image to ENVI standard file
    outimage.astype(np.float32)
    num_inpts.astype(np.float32)
    num_outpts.astype(np.float32)

    outformat = "ENVI"
    driver = gdal.GetDriverByName(outformat)
    nbands = 4
    outds = driver.Create(outfile, outimage.shape[1], outimage.shape[0], nbands, gdal.GDT_Float32)
    outds.GetRasterBand(1).WriteArray(outimage)
    outds.FlushCache()
    # write a mask band
    outimagemask = np.logical_not(outimagemask)
    outimagemask.astype(np.float32)
    outds.GetRasterBand(2).WriteArray(outimagemask)
    outds.FlushCache()
    # write number of points in a pixels selected to generate the assigned
    # pixel values.
    outds.GetRasterBand(3).WriteArray(num_inpts)
    outds.FlushCache()
    outds.GetRasterBand(4).WriteArray(num_outpts)
    outds.FlushCache()
    # close the dataset
    outds = None
    # Now write envi header file manually. NOT by gdal...which can't do this
    # job...  set header file
    # get header file name
    strlist = outfile.rsplit('.')
    hdrfile = ".".join(strlist[0:-1]) + ".hdr"
    if os.path.isfile(hdrfile):
        os.remove(hdrfile)
        print "Old header file removed: " + hdrfile 
    hdrfile = outfile + ".hdr"
    hdrstr = \
        "ENVI\n" + \
        "description = {\n" + \
        "Hemispherical projection image of DWEL point cloud, \n" + \
        infile + ", \n" + \
        "Create, [" + time.strftime("%c") + "], \n" + \
        "Camera height for projection, {0:f}}}\n".format(camheight) + \
        "samples = {0:d}\n".format(outimage.shape[1]) + \
        "lines = {0:d}\n".format(outimage.shape[0]) + \
        "bands = {0:d}\n".format(nbands) + \
        "header offset = 0\n" + \
        "file type = ENVI standard\n" + \
        "data type = 4\n" + \
        "interleave = bsq\n" + \
        "sensor type = Unknown\n" + \
        "byte order = 0\n" + \
        "wavelength units = unknown\n" + \
        "band names = {pts_proj, mask, num_inpts, num_outpts}"
    with open(hdrfile, 'w') as hdrf:
        hdrf.write(hdrstr)

#    import pdb; pdb.set_trace()

    return 0

def main(cmdargs):
    """
    Take inputs from command line and pass them to correct functions
    """

    infile = cmdargs.infile
    outfile = cmdargs.outfile
    indexcol = cmdargs.index - 1
    pixelcol = cmdargs.pixel - 1
    indexfuncname = cmdargs.indexfunc
    pixelfuncname = cmdargs.pixelfunc
    xyzcols = [cmdargs.cx-1, cmdargs.cy-1, cmdargs.cz-1]
    outres = cmdargs.outres
    minzen = cmdargs.minzen
    maxzen = cmdargs.maxzen
    camheight = cmdargs.camheight
    classflag = cmdargs.classflag
    maxonly = cmdargs.maxonly
    if maxonly:
        pulsenocol = cmdargs.pulsenocol - 1
        intensitycol = cmdargs.intensitycol - 1
    else:
        pulsenocol = None
        intensitycol = None
    
    print "Input file: " + infile
    print "Output file: " + outfile
    print "Projection resolution: {0:.3f} mrad".format(outres)
    print "Camera height: {0:.3f}".format(camheight)
    print "Projection minimum zenith: {0:.3f} deg".format(minzen)
    print "Projection maximum zenith: {0:.3f} deg".format(maxzen)
    print "Output is a classification image? " + ("Yes" if classflag else "No")
    print "Only use maximum return points in waveforms? " + ("Yes" if maxonly else "No")
    
    # choose the function for index
    if indexfuncname.upper() == "MAX":
        indexfunc = np.argmax
    elif indexfuncname.upper() == "MIN":
        indexfunc = np.argmin
    elif indexfuncname.upper() == "ALL":
        indexfunc = lambda x: np.arange(len(x))
    else:
        print "Error, cannot recognize the name of index function. Avaialbe, \n" \
            + "max: select the point/points with maximum value in a projected bin;\n" \
            + "min: select the point/points with minimum value in a projected bin;\n" \
            + "all: use all points in a projected bin."
        return ()

    # choose the function for pixel values:
    if pixelfuncname.upper() == "DIRECT":
        pixelfunc = lambda x: x
    elif pixelfuncname.upper() == "MAX":
        pixelfunc = np.nanmax
    elif pixelfuncname.upper() == "MIN":
        pixelfunc = np.nanmin
    elif pixelfuncname.upper() == "SUM":
        pixelfunc = np.nansum
    elif pixelfuncname.upper() == "MEAN":
        pixelfunc = np.nanmean
    elif pixelfuncname.upper() == "MODE":
        pixelfunc = lambda x: spstats.mode(x, axis=None)[0]
    else:
        print "Given name of pixel function: " + pixelfuncname
        print "Error, cannot recognize the name of pixel function. Avaialbe, \n" \
            + "direct: directly assign a 'pixel' column value of select " + \
            "point for a projected bin. If more than one points are " + \
            "returned by index function, use the value of the first select point" \
            + "max: assign the maximum of 'pixel' column values of select " + \
            "points for a projected bin;\n" \
            + "min: assign the minimum of 'pixel' column values of select " + \
            "points for a projected bin;\n" \
            + "sum: assign the sum of 'pixel' column values of select " + \
            "points for a projected bin;\n"
        return ()

    print "Indexing method: " + indexfuncname.upper()
    print "Output image assigning method: "+ pixelfuncname.upper()

    dwel_points2hsproj(infile, outfile, xyzcols, \
                           indexcol, indexfunc, pixelcol, pixelfunc, \
                           outres=outres, minzen=minzen, maxzen=maxzen, \
                           camheight=camheight, classflag=classflag, \
                           pulsemax=maxonly, pulsenocol=pulsenocol, \
                           intensitycol=intensitycol)

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()

        p.add_option("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points-clustering/merging/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans_canupo_class.txt", help="Input csv file of DWEL point cloud data")
        p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140503/spectral-points-by-union/HFHD20140503-dual-points/HFHD_20140503_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_nir_hsp2.img", help="Output hemispherical projection image")

#        p.add_option("-i", "--input", dest="infile", default=None, help="Input csv file of DWEL point cloud data")
#        p.add_option("-o", "--output", dest="outfile", default=None, help="Output hemispherical projection image")

        p.add_option("-r", "--resolution", dest="outres", default=2.0, type=float, help="Resolution of hemispherical projection. Unit: mrad. Default: 2.0 mrad")
        p.add_option("-H", "--camheight", dest="camheight", default=0.0, type=float, help="Height of hemi-camera relative to zero Z point of input point cloud. Unit: the same with input point cloud coordinates. Default: 0.0")
        p.add_option("--minzen", dest="minzen", default=0.0, type=float, help="Minimum zenith angle in hemispherical projection. Unit: deg. Default: 0.0 deg")
        p.add_option("--maxzen", dest="maxzen", default=95.0, type=float, help="Maximum zenith angle in hemispherical projection. Unit: deg. Default: 95.0 deg")
        p.add_option("-x", "--index", dest="index", default=None, type=int, help="Column index of values used to decide which point/points in a projected bin will offer pixel values, with first column being 1. Default: 4.")
        p.add_option("-p", "--pixel", dest="pixel", default=None, type=int, help="Column index of values used to assign pixel values, with first column being 1. Default: 16. Notice 'index' decides which point/points offer values to pixels. 'pixel' decides which attribute value of those points are assigned. 'index' and 'pixel' do NOT have to be the same.")
        p.add_option("--indexfunc", dest="indexfunc", default="all", help="Function applied to 'index' column to decide which point/points in a projected bin will offer pixel values. Available, 'max', 'min', 'all'. If 'all', -x --index option will have no effect. Default: all")
        p.add_option("--pixelfunc", dest="pixelfunc", default="mode", help="Function applied to 'pixel' column to calculate a pixel value from select points by 'index' column and 'indexfunc'. Available, 'direct', 'max', 'min', 'mean', 'sum'. Default: mode")
        p.add_option("--cx", dest="cx", default=1, type=int, help="Column index of X coordinate, with first column being 1. Default: 1.")
        p.add_option("--cy", dest="cy", default=2, type=int, help="Column index of Y coordinate, with first column being 1. Default: 2.")
        p.add_option("--cz", dest="cz", default=3, type=int, help="Column index of Z coordinate, with first column being 1. Default: 3.")

        p.add_option("-C", "--classflag", dest="classflag", default=False, action="store_true", help="If set (on), 'pixel' column is class label and output image is ENVI classification image. Default: off")
        
        p.add_option("-M", "--maxonly", dest="maxonly", default=False, action="store_true", help="If set (on), only maximum return points of waveforms will be used in projection. Default: off")
        p.add_option("--pulseno", dest="pulsenocol", default=None, type=int, help="Column index of pulse No., with first column being 1, to sort points from the same pulse together when '-M --maxonly' is set.")
        p.add_option("--intensity", dest="intensitycol", default=None, type=int, help="Column index of intensity, with first column being 1, to find maximum return points of waveforms when '-M --maxonly' is set.")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.infile is None) | (self.outfile is None):
            p.print_help()
            print "Both input and output file names are required."
            sys.exit()
        if (self.indexfunc.upper() != "ALL") and (self.index is None):
            print "You must explicitly set which column to use as index if your indexing function is not 'all'"
            print "Use option '-h --help' to find out how to set index column"
            sys.exit()
        if (self.indexfunc.upper() == "ALL") and (self.index is None):
            self.index = 4
        if (self.pixel is None):
            print "You must explicitly set which column's values to fill projection image"
            print "Use option '-h --help' to find out how to set pixel column"
            sys.exit()
        if (self.maxonly) and ((self.pulsenocol is None) or (self.intensitycol is None)):
            print "You must explicitly set which columns are pulse No. and intensity if you choose to only use maximum return points of waveforms in projection."
            print "Use option '-h --help' to find out how to set column of pulse No. and intensity"
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)

