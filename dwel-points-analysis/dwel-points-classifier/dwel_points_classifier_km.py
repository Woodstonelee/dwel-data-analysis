#!/usr/bin/env python
"""
Classify DWEL's dual-wavelength point cloud with dual-wavelength intensities.
unsupervised k-means clustering

USAGE:

    dwel_points_classifier_km.py

OPTIONS:

EXAMPLES:

AUTHORS:


"""

class CmdArgs:
    def __init__(self):
        p = optparse.OptionParser()

        p.add_option("-i", "--input", dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_small.txt", help="Input dual-wavelength point cloud file")
        p.add_option("-o", "--output", dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_sdfac2_sievefac10_ptcl_points_small_class.txt", help="Output classified point cloud file")

#        p.add_option("-i", "--input", dest="infile", default=None, help="Input dual-wavelength point cloud file")
#        p.add_option("-o", "--output", dest="outfile", default=None, help="Output classified point cloud file")


        p.add_option("-x", "--index", dest="index", default="NDI", help="Name of spectral index for thresholding, NDI, SR")
        p.add_option("-t", "--thresh", dest="thresh", default=None, type="float", help="Spectral index threshold for classification")

        p.add_option("-c", "--clipI", dest="clipI", default=False, action="store_true", help="Clip apparent reflectance values greater than 1 to one. Default: false (no clip)")
        p.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="Verbose. Save intermediate files and figures. Default: false.")

        (options, args) = p.parse_args()
        self.__dict__.update(options.__dict__)

        if (self.infile is None) | (self.outfile is None):
            p.print_help()
            print "Both input and output file names are required."
            sys.exit()

if __name__ == "__main__":
    cmdargs = CmdArgs()
    main(cmdargs)
