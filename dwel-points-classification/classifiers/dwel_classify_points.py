#!/usr/bin/env python

"""
Classify points in a dual-wavelength spectral point cloud from a DWEL scan.
"""

import sys
import os
import argparse

import numpy as np

from dwel_points_cluster import DWELPointsCluster
from dwel_points_supvcls import DWELPointsClassifier

def getCmdArgs():
    p = argparse.ArgumentParser(description="Classify dual-wavelength spectral point cloud from a DWEL scan")

    p.add_argument("-i", '--infile', dest="infile", required=False, default=None, help="Input dual-wavelength spectral point cloud")
    p.add_argument("-m", "--mscfile", dest="mscfile", default=None, help="MSC (Multi-Scale Characteristics) file from CANUPO processing as spatial information for classification")    
    p.add_argument("-o", '--outfile', dest="outfile", required=True, default=None, help="Output file of classified point cloud")
    
    p.add_argument("--classifier", dest="classifier", choices=['Spectral-KMeans', 'Spatial-KMeans', 'Spectral-Spatial-KMeans', \
                                                               'Spectral-RF', 'Spatial-RF', 'Spectral-Spatial-RF'], default="Spectral-KMeans")

    p.add_argument("--nclusters", dest="n_clusters", type=int, default=100, help="Number of clusters to generate by clustering")

    p.add_argument('--train_spectral', dest='train_spec', nargs='+', default=None, help="List of spectral point cloud files for training Random Forest classifier, with each file for one class.")
    p.add_argument('--train_spatial', dest='train_spa', nargs='+', default=None, help='List of MSC files for training Random Forest classifier, with each file for one class.')

    p.add_argument("-M", "--multiout", dest="multiout", default=False, action="store_true", help="Output classification into mulitiple files, one file for one class for easy display in CloudCompare. Default: false")

    p.add_argument("--use_msc_scales", dest="use_msc_scales", type=int, nargs="+", default=None, help="Indices of MSC scales to use in the classification, with first scale being indexed 1. Use \"msc_tool info file.msc\" to check the list of scales in the MSC file.")
    
    p.add_argument("-v", "--verbose", dest='verbose', default=False, action='store_true', help='Turn on verbose. Default: false')

    cmdargs = p.parse_args()

    if (cmdargs.outfile is None):
        p.print_help()
        print "Output file of classification or clustering is required"
        sys.exit()

    if ((cmdargs.classifier == "Spectral-Spatial-KMeans") \
        or (cmdargs.classifier == "Spectral-KMeans") \
        or (cmdargs.classifier == 'Spectral-Spatial-RF') \
        or (cmdargs.classifier == 'Spectral-RF')) \
       and (cmdargs.infile is None):
        p.print_help()
        print "Spectral points file is required for the classifiers using spectral attibutes: Spectral-KMeans, Spectral-Spatial-KMeans, Spectral-RF and Spectral-Spatial-RF"
        sys.exit()
        
    if ((cmdargs.classifier == "Spectral-Spatial-KMeans") \
        or (cmdargs.classifier == "Spatial-KMeans") \
        or (cmdargs.classifier == 'Spectral-Spatial-RF') \
        or (cmdargs.classifier == 'Spatial-RF')) \
       and (cmdargs.mscfile is None):
        p.print_help()
        print "MSC file is required for the classifiers using spatial attibutes: Spatial-KMeans, Spectral-Spatial-KMeans, Spatial-RF and Spectral-Spatial-RF"
        sys.exit()

    if (cmdargs.classifier == 'Spectral-Spatial-RF') \
       and (cmdargs.train_spec is None or cmdargs.train_spa is None):
        p.print_help()
        print "Training files of spectral point clouds and MSC data are required for the classifier, Spectral-Spatial-RF"
        sys.exit()
    if (cmdargs.classifier == 'Spectral-RF') \
       and (cmdargs.train_spec is None):
        p.print_help()
        print 'Training files of spectral point clouds are required for the classifier, Spectral-RF'
    if (cmdargs.classifier == 'Spatial-RF') \
       and (cmdargs.train_spa is None):
        p.print_help()
        print 'Training files of MSC data are required for the classifier, Spatial-RF'

    return cmdargs

def main(cmdargs):
    infile = cmdargs.infile
    outfile = cmdargs.outfile
    classifier = cmdargs.classifier
    n_clusters = cmdargs.n_clusters
    verbose = cmdargs.verbose
    mscfile = cmdargs.mscfile
    multiout = cmdargs.multiout
    use_msc_scales = cmdargs.use_msc_scales

    print "Start {0:s}".format(classifier)
    
    if classifier == "Spectral-KMeans":
        dpc = DWELPointsCluster(verbose)
        dpc.specKmeans(n_clusters, infile)
        dpc.writeClusterLabels(outfile, multiout)

    if classifier == "Spatial-KMeans":
        dpc = DWELPointsCluster(verbose)
        dpc.spaKmeans(n_clusters, infile, mscfile)
        dpc.writeClusterLabels(outfile, multiout)        

    if classifier == "Spectral-Spatial-KMeans":
        dpc = DWELPointsCluster(verbose)
        dpc.ssKmeans(n_clusters, infile, mscfile)
        dpc.writeClusterLabels(outfile, multiout)

    if classifier == 'Spectral-Spatial-RF':
        dpc = DWELPointsClassifier(verbose)
        pred_labels, pred_proba = dpc.runRandomForest(spectral_points_file=infile, \
                                                      msc_file=mscfile, \
                                                      spectral_training_files=cmdargs.train_spec,
                                                      msc_training_files=cmdargs.train_spa, \
                                                      use_msc_scales=use_msc_scales, \
                                                      n_estimators=100, n_jobs=-1)
        dpc.writeClassification(outfile, pred_labels, pred_proba=pred_proba, \
                                spectral_points_file=infile, msc_file=mscfile, \
                                use_msc_scales=use_msc_scales)

    if classifier == 'Spectral-RF':
        dpc = DWELPointsClassifier(verbose)
        pred_labels, pred_proba = dpc.runRandomForest(spectral_points_file=infile, \
                                                      spectral_training_files=cmdargs.train_spec, \
                                                      use_msc_scales=use_msc_scales, \
                                                      n_estimators=100, n_jobs=-1)
        dpc.writeClassification(outfile, pred_labels, pred_proba=pred_proba, \
                                spectral_points_file=infile, \
                                use_msc_scales=use_msc_scales)
        
    if classifier == 'Spatial-RF':
        dpc = DWELPointsClassifier(verbose)
        pred_labels, pred_proba = dpc.runRandomForest(msc_file=mscfile, \
                                                      msc_training_files=cmdargs.train_spa, \
                                                      use_msc_scales=use_msc_scales, \
                                                      n_estimators=100, n_jobs=-1)
        dpc.writeClassification(outfile, pred_labels, pred_proba=pred_proba, \
                                msc_file=mscfile, spectral_points_file=infile, \
                                use_msc_scales=use_msc_scales)

        
if __name__ == "__main__":
    cmdargs = getCmdArgs()
    main(cmdargs)
