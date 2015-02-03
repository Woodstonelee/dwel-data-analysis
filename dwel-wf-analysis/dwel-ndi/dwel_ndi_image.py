"""
Generate an NDI image from two bands of DWEL scans, and generate a histogram of
NDI values. 
Zhan Li, zhanli86@bu.edu
Created: 20140728 
"""

import numpy as np
from osgeo import gdal
import struct
import matplotlib.pyplot as plt
import matplotlib as mpl

import plotly.plotly as py # start plotly to create interactive plots online
from plotly.graph_objs import * # graph objects to piece together plots
# sign in my plotly account
py.sign_in('zhanli', 'fw4rg89h30')

from mpldatacursor import datacursor # a module to create a simple data cursor
# widget equivalent to MATLAB's datacursormode.

# from simpleEM import *
# from scipy.stats import norm

# import sklearn, a python package of machine learning
from sklearn import mixture

def dwel_ndi_image(nir_scan, swir_scan, mask):
    """
    Generate an NDI image from two bands of DWEL scans and a mask file to
    exclude invalid pixels.

    Parameters
    ----------
    nir_scan: numpy array
        NIR scanning image, should have the same dimension with swir_scan and
    mask. 
    swir_scan: numpy array
        SWIR scanning image, should have the same dimension with nir_scan and
    mask. 
    mask: numpy array
        mask of scanning image, 1 is good shot and 0 is bad shot, should have
    the same dimension with nir_scan and swir_scan
    
    Returns
    -------

    Raises
    ------ 
    """
    
    # calculate the NDI
    nodata = -9999 # a value to indicate invalid shots in the NDI image. 
    ndi = np.ones(shape=nir_scan.shape) * nodata
    nonzero_ind = mask.nonzero()
    ndi[nonzero_ind] = np.float32(nir_scan[nonzero_ind] -
        swir_scan[nonzero_ind]) / np.float32(nir_scan[nonzero_ind] +
        swir_scan[nonzero_ind]) 
    return {'NDI':ndi, 'NO_DATA':nodata}

def __main__():
    # nir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/C/HFHL_20140609_C_1064_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"
    # swir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hemlock20140609/C/HFHL_20140609_C_1548_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"
    #nir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/C/HFHD_20140608_C_1064_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"
    #swir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140608/C/HFHD_20140608_C_1548_cube_nu_basefix_satfix_pfilter_b32r04_wfmax_at_project_extrainfo.img"

    # nir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/CA2013June/CA2013_Site305/June14_01_305_NE/basefixtest/June14_01_305_NE_1064_Cube_NadirCorrect_Aligned_nu_basefix_satfix_pfilter_b32r04_4mrad_at_project_extrainfo.img"
    # swir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/CA2013June/CA2013_Site305/June14_01_305_NE/basefixtest/June14_01_305_NE_1548_Cube_NadirCorrect_Aligned_nu_basefix_satfix_pfilter_b32r04_4mrad_at_project_extrainfo.img"
    # site_name = ("Sierra Site 305 scan on 20130614")

    # intbandind = 5
    # maskbandind = 4
    # zenithbandind = 2
    # angle_scale = 10.0
    
    nir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1064_cube_bsfix_pxc_update_atp4_ptcl_pcinfo.img"
    swir_ancfile = "/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/HFHD_20140919_C/HFHD_20140919_C_1548_cube_bsfix_pxc_update_atp4_ptcl_pcinfo.img"
    site_name = ("Harvard Forest hardwood center scan on 20140919")

    intbandind = 2
    maskbandind = 13
    zenithbandind = 9
    angle_scale = 100.0
    
    min_zenith = 0.0
    max_zenith = 117.0
    
    # open the ancillary files of two bands
    nir_ads = gdal.Open(nir_ancfile, gdal.GA_ReadOnly)
    swir_ads = gdal.Open(swir_ancfile, gdal.GA_ReadOnly)
    
    # fetch the waveform mean intensity band
    nir_wfmean_band = nir_ads.GetRasterBand(intbandind) # the fifth band in the ancillary
# file is waveform mean.
    swir_wfmean_band = swir_ads.GetRasterBand(intbandind)
    # read the waveform mean
    nir_wfmean = nir_wfmean_band.ReadRaster(0, 0, nir_wfmean_band.XSize,
        nir_wfmean_band.YSize, nir_wfmean_band.XSize, nir_wfmean_band.YSize,
        nir_wfmean_band.DataType)
#    import pdb; pdb.set_trace()
    nir_wfmean = struct.unpack('i'*nir_wfmean_band.XSize*nir_wfmean_band.YSize,
        nir_wfmean) # convert the binary string from raster reading to a tuple
    nir_wfmean = np.asarray(nir_wfmean) # convert python tuple to numpy array
    nir_wfmean = np.reshape(nir_wfmean, (nir_wfmean_band.YSize,
        nir_wfmean_band.XSize)) # reshape the array to image dimension

    swir_wfmean = swir_wfmean_band.ReadRaster(0, 0, swir_wfmean_band.XSize,
        swir_wfmean_band.YSize, swir_wfmean_band.XSize, swir_wfmean_band.YSize,
        swir_wfmean_band.DataType)
    swir_wfmean = struct.unpack('i'*swir_wfmean_band.XSize*swir_wfmean_band.YSize,
        swir_wfmean) # convert the binary string from raster reading to a tuple 
    swir_wfmean = np.asarray(swir_wfmean) # convert python tuple to numpy array
    swir_wfmean = np.reshape(swir_wfmean, (swir_wfmean_band.YSize,
        swir_wfmean_band.XSize)) # reshape the array to image dimension

    # fetch the mask band
    mask_band = nir_ads.GetRasterBand(maskbandind) # the fourth band in the ancillary file
# is mask.
    # read mask
    mask = mask_band.ReadRaster(0, 0, mask_band.XSize, mask_band.YSize,
    mask_band.XSize, mask_band.YSize, mask_band.DataType) 
    mask = struct.unpack('i'*mask_band.XSize*mask_band.YSize, mask) # convert
# the binary string from raster reading to a tuple 
    mask = np.asarray(mask) # convert python tuple to numpy array 
    mask = np.reshape(mask, (mask_band.YSize, mask_band.XSize)) # reshape the
# array to image dimension

    # calculate NDI image
    ndi = dwel_ndi_image(nir_wfmean, swir_wfmean, mask) 
    #ndi['NDI'][ndi['NDI']==ndi['NO_DATA']] = 0

    # clip away the casing area from the NDI image
    # read out the zenith angle
    zenith_band = nir_ads.GetRasterBand(zenithbandind) # the second band in the ancillary file
# is zenith angles.
    # read zenith
    zenith = zenith_band.ReadRaster(0, 0, zenith_band.XSize, zenith_band.YSize,
        zenith_band.XSize, zenith_band.YSize, zenith_band.DataType) 
    zenith = struct.unpack('i'*zenith_band.XSize*zenith_band.YSize, zenith) # convert
# the binary string from raster reading to a tuple 
    zenith = np.asarray(zenith) # convert python tuple to numpy array 
    zenith = np.reshape(zenith, (zenith_band.YSize, zenith_band.XSize)) # reshape the
# array to image dimension
    zenith = zenith / angle_scale # rescale
    # the zenith angle beyond max_zenith degree is inside the case
    casing_edge_ind = np.zeros(zenith.shape[0])
    min_zen_ind = np.zeros(zenith.shape[0])
    for i in range(0, zenith.shape[0]):
        tmpind = (zenith[i,:]>=max_zenith).nonzero()
#        import pdb; pdb.set_trace()
        if len(tmpind[0]) ==0:
            casing_edge_ind[i] = zenith.shape[1]-1
        else:
            casing_edge_ind[i] = tmpind[0][0]
        tmpind = (zenith[i, :] >= min_zenith).nonzero()
        if len(tmpind[0]) ==0:
            min_zen_ind = 0
            print "No data at zenith larger than given minimum angle"
        else:
            min_zen_ind = tmpind[0][0]

    edge_pos = np.fix(np.median(casing_edge_ind))
    top_pos = np.fix(np.median(min_zen_ind))

    nir_wfmean = nir_wfmean[:, range(top_pos, edge_pos)]
    swir_wfmean = swir_wfmean[:, range(top_pos, edge_pos)]
    mask = mask[:, range(top_pos, edge_pos)];
    
#    import pdb; pdb.set_trace(
    # plot nir and swir values on a plane to see their clustering status
    tmpind = mask.nonzero()
    dualwlfig = plt.figure()
    plt.scatter(nir_wfmean[tmpind], swir_wfmean[tmpind])
    plt.savefig(("/usr3/graduate/zhanli86/Programs/dwel-wf-analysis/dualwlscatter.png"))
    plt.close(dualwlfig);

    ndi_nocasing = np.transpose(ndi['NDI'][:,range(top_pos,edge_pos)])
    valid_ndi = ndi_nocasing[ndi_nocasing!=ndi['NO_DATA']]
    valid_ndi = valid_ndi[~np.isnan(valid_ndi)]
    valid_ndi = valid_ndi[np.logical_and(valid_ndi>=-1.0, valid_ndi<=1.0)]
    bins = np.arange(np.nanmin(valid_ndi), np.nanmax(valid_ndi), 0.01)
    valid_ndi = valid_ndi[valid_ndi!=-1]
    ndihistfig = plt.figure()
#    import pdb; pdb.set_trace()
#    tmpweights = np.ones_like(valid_ndi)/len(valid_ndi)
    ndihist = plt.hist(valid_ndi, bins, normed=True)
    ndifreq = ndihist[0]
    s = valid_ndi
    # g = mixture.GMM(n_components=2, init_params='')
    # g.means_ = np.array([[0.635], [0.305]])
    # g.covars_ = np.array([[0.1*0.1], [0.06*0.06]])
    # g.fit(s)
    # print("AIC = ", g.aic(s))
    # logprob = g.score_samples(bins)
    # plt.plot(bins, np.exp(logprob[0]), color='k')
    # plt.plot(bins, np.exp(logprob[0])*logprob[1][:,0], color='r')
    # plt.plot(bins, np.exp(logprob[0])*logprob[1][:,1], color='g')
        
    plt.title(("Histogram of NDI from waveform max intensities of " + site_name))
    plt.xlabel("NDI")
    plt.ylabel("Normalized Frequency")
    plt.savefig(("/usr3/graduate/zhanli86/Programs/dwel-wf-analysis/ndihist.png"))
#    import pdb; pdb.set_trace()
    
    ndi_nocasing[ndi_nocasing==ndi['NO_DATA']] = np.nan
    ndi_nocasing[np.logical_or(ndi_nocasing<-1.0, ndi_nocasing>1.0)] = np.nan
    plt.figure()
    cmap = mpl.cm.get_cmap('Greys_r')
    cmap.set_bad(color='k')
    image1 = plt.imshow(ndi_nocasing, cmap=cmap)
    #image1.set_cmap('Greys_r')
    az_ticks = np.arange(0, ndi_nocasing.shape[1],
        20.0/360.0*ndi_nocasing.shape[1]) 
    zen_ticks = np.arange(0, ndi_nocasing.shape[0],
        20.0/max_zenith*ndi_nocasing.shape[0]) 
    plt.xticks(az_ticks, map(str,
        np.int_(np.rint(az_ticks/ndi_nocasing.shape[1]*360.0)))) 
    plt.yticks(zen_ticks, map(str,
        np.int_(np.rint(zen_ticks/ndi_nocasing.shape[0]*max_zenith)))) 
    plt.xlabel(("Instrument Azimuth"))
    plt.ylabel(("Instrumemnt Zenith"))
    plt.title(("NDI from waveform max intensities of " + site_name))
    plt.savefig(("/usr3/graduate/zhanli86/Programs/dwel-wf-analysis/ndiimage.png"))
#    datacursor()
#    plt.show()
    
    ndi_classified = ndi_nocasing
    ndi_classified[ndi_nocasing<0.6] = 0
    ndi_classified[ndi_nocasing>=0.6] = 1
    plt.figure()
    cmap = mpl.cm.get_cmap('prism')
    cmap.set_bad(color='k')
    image2 = plt.imshow(ndi_classified, cmap=cmap, interpolation='nearest', vmin=0, vmax=1) 
    plt.xticks(az_ticks, map(str,
        np.int_(np.rint(az_ticks/ndi_nocasing.shape[1]*360.0)))) 
    plt.yticks(zen_ticks, map(str,
        np.int_(np.rint(zen_ticks/ndi_nocasing.shape[0]*max_zenith))))
    plt.xlabel(("Instrument Azimuth"))
    plt.ylabel(("Instrumemnt Zenith"))
    plt.title(("NDI thresholding according to NDI histogram, " + site_name))
    plt.savefig(("/usr3/graduate/zhanli86/Programs/dwel-wf-analysis/ndithresholding.png"))
#    datacursor()
    plt.show()

    # export the figure to plotly website
    # ndi_hist_url = py.plot_mpl(ndihistfig,
    #     filename=('atwfmax NDI hist ' + site_name), auto_open=False)
    
    # close gdal datasets
    del nir_ads
    del swir_ads

if __name__ == "__main__":
    __main__()
