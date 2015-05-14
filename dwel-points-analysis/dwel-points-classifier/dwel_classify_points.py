#!/usr/bin/env python
"""
Classify points in a dual-wavelength spectral point cloud from a DWEL scan.
"""

import sys
import os
import argparse

from dwel_points_cluster import DWELPointsCluster

def getCmdArgs():
    p = argparse.ArgumentParser(description="Classify dual-wavelength spectral point cloud from a DWEL scan")

    p.add_argument("-i", '--infile', dest="infile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/Hardwood20140919/spectral-points-by-union/HFHD_20140919_dual_points/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points.txt", help="Input dual-wavelength spectral point cloud")
    p.add_argument("-o", '--outfile', dest="outfile", default="/projectnb/echidna/lidar/DWEL_Processing/HF2014/tmp-test-data/HFHD_20140919_C_dual_cube_bsfix_pxc_update_atp2_ptcl_points_kmeans.txt", help="Output file of classified point cloud")
    p.add_argument("--classifier", dest="classifier", choices=['KMeans', 'NDI'], default="KMeans")

    kmeans_p = p.add_argument_group("KMeans clustering", "Options for Kmeans clustering")
    kmeans_p.add_argument("--nclusters", dest="n_clusters", type=int, default=100, help="Number of clusters to generate by KMeans")

    p.add_argument("-v", "--verbose", dest='verbose', default=False, action='store_true', help='Turn on verbose. Default: false')

    cmdargs = p.parse_args()

    if (cmdargs.infile is None) or (cmdargs.outfile is None):
        p.print_help()
        print "Input and output files are required"
        sys.exit()

    return cmdargs

def main(cmdargs):
    infile = cmdargs.infile
    outfile = cmdargs.outfile
    classifier = cmdargs.classifier
    n_clusters = cmdargs.n_clusters
    verbose = cmdargs.verbose

    if classifier == "KMeans":
        dpc = DWELPointsCluster(infile, verbose)
        dpc.kmeans(n_clusters)
        dpc.writeClusterLabels(outfile)

if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
