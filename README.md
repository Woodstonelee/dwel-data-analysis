# DWEL Data Analysis Tools

---

# About

A collection of tools and programs to analyze preprocessed data from a dual-wavelength terristral lidar, the **DWEL**, Dual-Wavelength Echidna Lidar, and produce useful products for applications, such as Pgap, leaf are index, foliage profile, 3D reconstruction and tree modelling, and etc.. The preprocessed DWEL data is outputs from IDL programs of DWEL waveform preprocessing. The preprocessed DWEL data includes two major data categories: 

1. **Waveform data** after baseline fix, saturation fix, noise removal possibly by filtering. This is usually labeled as 'pfilter' in the outpu file names from IDL programs. However, at this moment, *no actual clean waveforms for DWEL* is generated because of high background noise level and ringing noise. The synthesis waveforms from extracted points may be served as the de-facto clean waveforms. Potentially future development of improved waveform filtering and decomposition algorithms for DWEL can output both better waveform and point cloud data of DWEL. Waveform data is stored in **_ENVI data cube (like hyperspectral image)_** possibly with an associated **_ENVI image file_** containing ancillary data such as, mask, angle data and etc.. This image file of ancillary data is the projection of compressed waveform data. 
2. **Point cloud data** after preprocessing steps mentioned above. The point cloud data can be stored in two formats, (1) **_discrete points_** usually in simple ASCII files. Each point has the following records, x, y, z, range, overlap-corrected peak intensity, approximate FWHM and other records about where a point is extracted from; (2) **_projected images of point cloud_** usually in ENVI image files (pcinfo file out of IDL programs) or TIFF. Projected images provide an easier and clearer way to present point cloud in 2D. The projection can be Andrieu equal-angle projection and hemispherical projection. Each pixel of a projected image contains the following attributes: intensity (total, mean, maximum, first-return, last-return intensity of points in this projected pixel), zenith and azimuth angle, mask, number of averaged laser beams in this pixel, and other attributes. 

The tools and programs for DWEL data analysis here are written and developed in different programming languages. Ultimately, they will *be wrapped into commands usable in Linux command line interface (CLI)* with consistent style. For now, Zhan is too busy with dissertation to do this important cosmetic step :(. 

---

# Directory Structure

Programs are grouped into different folders based on their functionality and data categories they are fed with. *Folders keep growing and more tools will be added.* The current folders and description of their functionality and purposes are listed in the following sections.

## 1. dwel-wf-analysis

Programs that take in and process DWEL waveform data stored in *ENVI data cube*.

### *To be filled*. 
(Analysis of waveform data out of IDL programs of DWEL waveform preprocessing.)
### *To be filled*. 
(Experimental algorithms of DWEL waveform filtering and decomposition to improve noise removal and point cloud generation.)
### *To be filled*. 
(Gap probability from calibrated waveforms for leaves and woody materials together and separately.)

## 2. dwel-points-analysis

Programs that take in and process DWEL point cloud data stored in *discrete points*. The point cloud data can be directly from IDL DWEL preprocessing programs or from some experimental waveform decomposition functions in the folder of *dwel-wf-analysis*. 

### 2.1. dwel-points-classifier

+ Generate single point cloud with dual-wavelength intensities from DWEL point cloud files. 
+ Classify points in dual-wavelength point cloud with intensity information by, 
  - Simple normalized difference index (NDI) thresholding. 
  - Maximum likeliehood (ML) classifier.
  - Random forest (RF) classifier. 
+ Classify points in single-wavelength point cloud with pulse shape information by,  
  - Thresholding ratio of peak intensity to FWHM of a return pulse that gives a point.

### 2.2. dwel-dual-pgap-estimator

+ Estimate gap probability (Pgap) from DWEL *discrete ponits*.
  - Pgap of all vegetation elements from unclassified points. 
  - Pgap of leaves and woody materials separately from classified points.

### 2.3. dwel-point-cloud-registration

+ *To be filled*. Functions to help registration of multiple point cloud. At present we don't have a fully automatic registration algorithm. But some functions here will help manual registration. 
+ *To be filled*. Functions to write registered and merged point cloud of a whole forest site from several scans. The output point cloud will be fed to Pasi's quantitative structure modeling (QSM) to generate tree models and estimate tree volume. 

## 3. dwel-projected-image-analysis

Programs that take in and process projected images of either waveforms or discrete points from DWEL. 

### *To be filled*

## 4. dwel-pgap2profile

Programs that take in total or classified Pgap from DWEL data and process them to canopy structural parameters, such as area index, foliage profile, clumping index and etc.. for total vegetation elements or for leaves and woody materials separately. 

### *to be filled*

## 5. dwel-data-utils

Programs that are not specific for DWEL's dual-wavelength data but universal for any lidar waveform and point cloud. 

+ Convert discrete points to hemispherical projected image. 

---

# Requirements

## Main dependencies

(_required by most functions_)

+ Python (2.6.x)
+ GDAL (10.0.2)

## Python dependencies

(_required by functions in python)

+ numpy (>=1.9.1)
+ matplotlib (>=1.4.2)

## Other dependencies

(_required by a few functions_)

MATLAB (R2013a :()

---

# Contribution

**Helps are definitely welcome and needed!**

Zhan Li, zhanli86@bu.edu