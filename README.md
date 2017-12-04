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

+ dwel-data-utils: Programs that are not specific for DWEL's dual-wavelength data but universal for any lidar waveform and point cloud. 
+ dwel-plant-profile: Estimate gap probability (Pgap) from DWEL *discrete ponits* and then plant profiles.
  - obsolete: Not used.
  - one-band-a-time: Estimation from each band separately.
  - two-bands-a-time: Not used.
+ dwel-points-analysis: Programs that take in and process DWEL point cloud data stored in *discrete points*.
  - dwel-points2dem
  - dwel-points-modeling
  - dwel-points-registration
+ dwel-points-classification: Classify points from DWEL scans and accuracy assessments.
  - classifiers
  - cls-accuracy
  - ground-filter
  - obsolete: Not used.
  - utils
+ dwel-spectral-points-generation: Generate a bispectral point cloud from two monospectral DWEL point cloud files.
+ dwel-waveform-analysis: Programs that take in and process DWEL waveform data stored in *ENVI data cube*.
  - dwel-ndi
  - dwel-wf-misc

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

(_required by a few functions_ in dwel-points-classification/ground-filter)

MATLAB ( R2013a :( )

---

# Contribution

**Helps are definitely welcome and needed!**

Zhan Li, zhanli86@bu.edu
