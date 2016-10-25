# Generation of a bi-spectral point cloud from two spectral point clouds by DWEL

Zhan Li, zhanli86@bu.edu
Thu Jun  9 10:09:14 EDT 2016

##  1. How do we generate bi-spectral point clouds? 
Single DWEL scans at the two wavelengths, 1064 nm and 1548 nm first generates 
two mono-spectral point clouds at 1064 nm and 1548 nm. These two point clouds 
are then merged together to generate the bi-spectral point cloud. There are 
two ways of merging two mono-spectral point clouds, 

1. Intersection of two point clouds.
	
	Common points in 1064-nm and 1548-nm point clouds are matched with laser
	shot  number and ranges. That is, if two points have the same shot number
	and their  range difference is smaller than a given threshold, then the
	two points are  matched as returns from the same targets. These points are
	saved to the  bi-spectral point cloud with both 1064-nm and 1548-nm
	apparent reflectance.

2. Union of two point clouds.

	Besides common points found by the above intersection approach, other
	points at one wavelength may not have corresponding points at the other
	wavelength. Union  approach will synthesize intensity at the point-missing
	wavelength from the  intensity of the other wavelength with the help of a
	synthesized NDI value  (normalized difference index) of the laser shot.
	The NDI value for this laser  shot could be from average apparent
	reflectance values at the two wavelengths in the same shot or interpolated
	from neighboring shots if this shot does not have any retrieved point at
	one wavelength.

## 2. What do the code files in this folder do? 
* dwel_generate_spectral_points.py

	Main interface of the generation program. It takes inputs and parameters for
	the generation of bi-spectral point clouds.

* dwel_spectral_points.py

	A class that deals with all the functions and parameters for the generation of
	bi-spectral point clouds.

* dwel_ndi_image_gap_filling.py

	Generates gap-filled NDI image in AT projection from DWEL pcinfo images at the
	two wavelengths out of the DWEL IDL processing program for point cloud
	generation. This gap-filled NDI image will be used in the union way of
	generating bi-spectral point clouds.

## 3. How do we run the programs to generate bi-spectral point clouds?

### 3.1 Dependencies to install before running the programs
* Python 2.7
* Pyhton libraries to install
  	* numpy
  	* scikit-learn
  	* gdal

### 3.2 Some possible change to the code files to accomodate your input file format
* dwel_spectral_points.py

	line 32 - 53
	```python
    # ------------------------------------------------------------
    # Set some parameters according to your own input point
    # clouds.
    self.i_scale = 1000.0
    self.headerlines = 3
    # Column indices in ASCII file, with 0 as the first.
    # 
    # Ten mandatory columns: x, y, z, d_I, shot_number, range,
    # theta, phi, sample, line
    # 
    # One or more optional columns: fwhm
    cind = {'range':8, 'sample':12, 'line':13, 'x':0, 'y':1, 'z':2, \
            'd_I':3, 'shot_number':6, 'theta':9, 'phi':10, \
            'fwhm':16, 'band':14}
    # Below ind_label lists column name labels in the order of the
    # columns that actually exist in your ASCII file.
    #
    # Mandatory columns MUST be BEFORE optional columns in the
    # following list. 
    self.ind_label = ('x', 'y', 'z', 'd_I', 'shot_number', 'range', \
                      'theta', 'phi', 'sample', 'line')
    # ------------------------------------------------------------	
	```

* dwel_ndi_image_gap_filling.py

	line 67 - 68
	```python
	# change the indices to the bands, "Total_d" (sum of apparent reflectance), 
	# "Nhits" (number of hits), and "Mask" (mask of invalid shots)
	def __init__(self, nirfile, swirfile, outfile, \
	                 rhoband=2, nhitsband=1, maskband=13):
	```

### 3.3 Intersection way
```python
python dwel_generate_spectral_points.py -n NIR_PTS_FILE -s SWIR_PTS_FILE -o DUAL_PTS_FILE -c NUM_COLS -r NUM_ROWS -R RANGE_DIFF_THRESHOLD
```

Get help:

```python
python dwel_generate_spectral_points.py -h
```

### 3.4 Union way 
* Step 1

	```python
	python dwel_ndi_image_gap_filling.py -n NIR_PCINFO_FILE -s SWIR_PCINFO_FILE -o NDI_FILE -k NUM_NEIGHBOUR
	```

	Get help:

	```python
	python dwel_ndi_image_gap_filling.py -h
	```

* Step 2

	```python
	python dwel_generate_spectral_points.py -n NIR_PTS_FILE -s SWIR_PTS_FILE -o DUAL_PTS_FILE -c NUM_COLS -r NUM_ROWS -R RANGE_DIFF_THRESHOLD --union --ndi NDI_FILE
	```

	Get help:

	```python
	python dwel_generate_spectral_points.py -h
	```

## 4. Data format of point cloud ascii file
Comma-separated values
### Headers: 
* Line 1 & 2: header information, self-explanatory
* Line 3: column names
### Columns in point cloud ascii files of mono-spectral apparent reflectance (1064 nm or 1548 nm)
* X, Y, Z: Cartesian coordinates of a point
* d_I: apparent reflectance
* Return_Number: the first return, second return and etc. 
* Number_of_Returns: number of points from a laser shot
* Shot_Number: the index number of a laser shot
* Run_Number: an integer number to indicate the time of data processing
* range: range value from interpolation of return pulse peak. 
* theta: zenith angle
* phi: azimuth angle
* rk: range value at maximum bin of return pulse, no interpolation. 
* Sample: the sample (column) index in the AT projection image of DWEL scan where the laser shot is from.
* Line: the line (row) index in the AT projection image of DWEL scan where the laser shot is from.
* Band: the index to the waveform bin of the return pulse maximum. 
* d0: intensity of the point before calibration, in unit of digital counts.
* fwhm: full-width at half maximum of the return pulse. _Highly inaccurate due to waveform noise interference_.
### Additional columns in point cloud ascii files of dual-wavelength apparent reflectance (dual), not in the above listed columns
* d_I_nir: apparent reflectance of 1064 nm, NIR band.
* d_I_swir: apparent reflectance of 1548 nm, SWIr band.
* fwhm_nir: full-width at half maximum of the return pulse at 1064 nm. _Highly inaccurate due to waveform noise interference_.
* fwhm_swir: full-width at half maximum of the return pulse at 1548 nm. _Highly inaccurate due to waveform noise interference_.

* qa: QA flag for the apparent reflectance of the two wavelength. The meaning of QA values is given by the following table. 
	
	In the first three columns of the table, 0 means the value is from actual
	scanning data, 1 mean the value is from synthesis.  Simply speaking, QA=0
	means the highest quality of dual-wavelength points, apparent reflectance
	values at both wavelengths are from actual data by intersection approach,
	no synthesized values are used.

| bit for NDI | bit for NIR app. refl. | bit for SWIR app. refl. | QA values |
| --- | -------------- | --------------- | --------- |
| 0   | 0              | 0               | 0         |
| 0   | 0              | 1               | 1         |
| 0   | 1              | 0               | 2         |
| 1   | 0              | 1               | 5         |
| 1   | 1              | 0               | 6         |

* r, g, b: RGB values for color-composite display of points. Red as 1548 nm, green as 1064 nm, and blue as dark. 

## 5. Which generation way should I choose, union or intersection? 

The intersection way gives you the best quality points with bi-spectral
apparent reflectance values. Both app. refl. values of each point are actual
retrievals from waveforms. But it may miss a lot of hits where the signal at
one wavelength is too weak to be retrieved by our point cloud generation
though the other wavelength retrieves a point.

To have more points in the bi-spectral point cloud, you can use the union way.
However, one app. refl. value of a point can be synthesized according to NDI
of the laser shot. The quality of the synthesized app. refl. value can vary.
You need to use these values cautiously. Use the QA flags to sieve the points
you want.
