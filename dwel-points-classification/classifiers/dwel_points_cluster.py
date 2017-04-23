import sys
import os
import time
import warnings

from collections import namedtuple
import itertools
import resource

import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans, Birch
from sklearn.ensemble import RandomTreesEmbedding
from sklearn.decomposition import IncrementalPCA

# add parent folder to Python path
addpath = os.path.dirname(os.path.abspath("."))
if addpath not in sys.path:
    sys.path.append(addpath)
import utils.dwel_points_utils as dpu

class DWELPointsCluster:
    """
    Method to cluster DWEL spectral points as unsupervised classification.

    AUTHORS:

        Zhan Li, zhanli86@bu.edu
    """

    def __init__(self, verbose=False, pf_npts=1e4):

        self.verbose = verbose

        # set some parameters
        self.headerlines = 3
        cind = {'x':0, 'y':1, 'z':2, 'd_I_nir':3, 'd_I_swir':4, \
                    'return_number':5, 'number_of_returns':6, 'shot_number':7, \
                    'range':8, 'theta':9, 'phi':10, 'sample':11, 'line':12, \
                    'd0_nir':13, 'd0_swir':14, 'qa':15, \
                'grd_label':19}
        self.cind = cind

        # number of points fed to BIRCH clustering's partial fit each
        # time
        birch = namedtuple('birch', ['pf_npts', 'threshold', 'branching_factor'])
        self.birch = birch(int(pf_npts), 0.5, 50)

        mbk = namedtuple('mbk', ['pf_npts', 'max_iter'])
        self.mbk = mbk(int(pf_npts), int(1e3))

    def specKmeans(self, n_clusters, spectralptsfile):
        """
        Use k-means clustering on spectral data only.
        """
        self.classifier = "Spectral-KMeans"
        self.inptsfile = spectralptsfile   
        points = self.loadPoints()
        points = points[self.validhit_bool, :]
        # points = self.randomForestTransform(points, 5, 10)

        print "Running KMeans clustering on spectral data only ..."
        points = StandardScaler(copy=False).fit_transform(points)
        mbk = MiniBatchKMeans(n_clusters=n_clusters)
        mbk.fit(points)
        self.labels[self.validhit_bool] = mbk.labels_

    def spaKmeans(self, n_clusters, spectralptsfile, mscfile, use_scales=None):
        """
        Use mini-batch Kmeans on spatial data only.
        """
        self.classifier = "Spatial-KMeans"
        self.inptsfile = spectralptsfile
        self.mscfile = mscfile

        self.loadPoints()

        print "Running KMeans clustering on spatial data only ..."

        mscfobj = dpu.openMSC(mscfile)
        mscheader = mscfobj.header

        nscales = len(mscheader[1])
        if use_scales is None:
            use_scales = np.arange(nscales)
        else:
            if np.any(use_scales >= nscales):
                raise RuntimeError("Indices to scales out of bound, {0:d} scales in input MSC\n".format(nscales))
            if np.any(use_scales < 0):
                raise RuntimeError("Indices to scales out of bound, negative indices found")
        
        # Process the points in batches
        npts = mscheader[0]
        niter = int(npts/self.mbk.pf_npts) + 1

        rusage_denom = 1024.
        
        pca_flag = True
        
        if pca_flag:
            # Transform the data with PCA
            print "\tPCA of MSC spatial data ..."
            ipca = IncrementalPCA(n_components=len(use_scales))
            for i in xrange(niter):
                mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
                mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
                if np.sum(mscbool) == 0:
                    if self.verbose:
                        # debug
                        print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                    continue
                ipca.partial_fit(mscdata[mscbool, 0:-1])
                sys.stdout.write("{0:d} / {1:d}  \n".format(i, niter))
            
            print np.cumsum(ipca.explained_variance_ratio_)
            
        # Train the standard scaler to scale the input data
        # incrementally
        print
        print "\tTraining preprocessing scaler for MSC spatial data ..."
        mscfobj.next_pt_idx = 0
        scaler = StandardScaler()
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                scaler.partial_fit(ipca.transform(mscdata[mscbool, 0:-1]))
            else:
                scaler.partial_fit(mscdata[mscbool, 0:-1])
                
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))

        # Train the mini-batch KMeans
        print
        print "\tTraining the mini-batch KMeans cluster ..."
        mscfobj.next_pt_idx = 0
        mbk = MiniBatchKMeans(n_clusters=n_clusters)
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                mbk.partial_fit(scaler.transform(ipca.transform(mscdata[mscbool, 0:-1])))
            else:
                mbk.partial_fit(scaler.transform(mscdata[mscbool, 0:-1]))
            
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))
        
        # Predict the label of points after feeding all points to
        # mini-batch KMeans
        print
        print "\tPredicting mini-batch KMeans clustering labels ..."
        # Rewind the MSC file object to read points from the
        # beginning.
        mscfobj.next_pt_idx = 0
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                self.labels[mscdata[mscbool, -1].astype(int)-1] = mbk.predict(scaler.transform(ipca.transform(mscdata[mscbool, 0:-1])))
            else:
                self.labels[mscdata[mscbool, -1].astype(int)-1] = mbk.predict(scaler.transform(mscdata[mscbool, 0:-1]))
                
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))

        mscfobj.close()

    def ssKmeans(self, n_clusters, spectralptsfile, mscfile, use_scales=None):
        """
        Use mini-batch KMeans clustering on both spectral and spatial data.
        """
        self.classifier = "Spectral-Spatial-KMeans"
        self.inptsfile = spectralptsfile
        self.mscfile = mscfile

        points = self.loadPoints()

        print "Running KMeans clustering on both spectral and spatial data ..."

        mscfobj = dpu.openMSC(mscfile)
        mscheader = mscfobj.header

        nscales = len(mscheader[1])
        if use_scales is None:
            use_scales = np.arange(nscales)
        else:
            if np.any(use_scales >= nscales):
                raise RuntimeError("Indices to scales out of bound, {0:d} scales in input MSC\n".format(nscales))
            if np.any(use_scales < 0):
                raise RuntimeError("Indices to scales out of bound, negative indices found")
        
        # Process the points in batches gradually
        npts = mscheader[0]
        niter = int(npts/self.mbk.pf_npts) + 1

        rusage_denom = 1024.

        pca_flag = True
        
        # Train the standard scaler to scale the input data
        # incrementally
        print
        print "\tTraining preprocessing scaler for spectral and MSC spatial data ..."
        mscfobj.next_pt_idx = 0
        scaler = StandardScaler()
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            
            scaler.partial_fit(np.concatenate((points[mscdata[mscbool, -1].astype(int)-1, :], mscdata[mscbool, 0:-1]), axis=1))
            
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))

        if pca_flag:
            # Transform the data with PCA
            print "\tPCA of spectral and MSC spatial data ..."
            mscfobj.next_pt_idx = 0
            ipca = IncrementalPCA(n_components=len(use_scales)+points.shape[1])
            for i in xrange(niter):
                mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
                mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
                if np.sum(mscbool) == 0:
                    if self.verbose:
                        # debug
                        print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                    continue
                ipca.partial_fit(scaler.transform(np.concatenate((points[mscdata[mscbool, -1].astype(int)-1, :], mscdata[mscbool, 0:-1]), axis=1)))
                sys.stdout.write("{0:d} / {1:d}  \n".format(i, niter))

            print ipca.explained_variance_ratio_
            print np.cumsum(ipca.explained_variance_ratio_)
            print ipca.var_
            print ipca.components_

            import pdb; pdb.set_trace()
            
        # Train the mini-batch KMeans
        print
        print "\tTraining the mini-batch KMeans cluster ..."
        mscfobj.next_pt_idx = 0
        mbk = MiniBatchKMeans(n_clusters=n_clusters)
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                mbk.partial_fit(ipca.transform(scaler.transform(np.concatenate((points[mscdata[mscbool, -1].astype(int)-1, :], mscdata[mscbool, 0:-1]), axis=1))))
            else:
                mbk.partial_fit(scaler.transform(np.concatenate((points[mscdata[mscbool, -1].astype(int)-1, :], mscdata[mscbool, 0:-1]), axis=1)))
            
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))
        
        # Predict the label of points after feeding all points to
        # mini-batch KMeans
        print
        print "\tPredicting mini-batch KMeans clustering labels ..."
        # Rewind the MSC file object to read points from the
        # beginning.
        mscfobj.next_pt_idx = 0
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.mbk.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                self.labels[mscdata[mscbool, -1].astype(int)-1] = mbk.predict(ipca.transform(scaler.transform(np.concatenate((points[mscdata[mscbool, -1].astype(int)-1, :], mscdata[mscbool, 0:-1]), axis=1))))
            else:
                self.labels[mscdata[mscbool, -1].astype(int)-1] = mbk.predict(scaler.transform(np.concatenate((points[mscdata[mscbool, -1].astype(int)-1, :], mscdata[mscbool, 0:-1]), axis=1)))
            
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))

        mscfobj.close()
        
    def spaBIRCH(self, n_clusters, spectralptsfile, mscfile, use_scales=None):
        """
        Use BIRCH clustering on spatial data only.
        """
        self.classifier = "Spatial-BIRCH"
        self.inptsfile = spectralptsfile
        self.mscfile = mscfile

        self.loadPoints()

        print "Running BIRCH clustering on spatial data only ..."
        
        mscfobj = dpu.openMSC(mscfile)
        mscheader = mscfobj.header

        nscales = len(mscheader[1])
        if use_scales is None:
            use_scales = np.arange(nscales)
        else:
            if np.any(use_scales >= nscales):
                raise RuntimeError("Indices to scales out of bound, {0:d} scales in input MSC\n".format(nscales))
            if np.any(use_scales < 0):
                raise RuntimeError("Indices to scales out of bound, negative indices found")
        
        # Process the points in batches gradually
        npts = mscheader[0]
        niter = int(npts/self.birch.pf_npts) + 1

        rusage_denom = 1024.

        pca_flag = False

        if pca_flag:
            # Transform the data with PCA
            print "\tPCA of MSC spatial data ..."
            ipca = IncrementalPCA(n_components=len(use_scales))
            for i in xrange(niter):
                mscdata = mscfobj.read(npts=self.birch.pf_npts, use_scales=use_scales)
                mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
                if np.sum(mscbool) == 0:
                    if self.verbose:
                        # debug
                        print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                    continue
                ipca.partial_fit(mscdata[mscbool, 0:-1])
                sys.stdout.write("{0:d} / {1:d}  \n".format(i, niter))

            print np.cumsum(ipca.explained_variance_ratio_)
        
        # Train the standard scaler to scale the input data
        # incrementally
        print
        print "\tTraining preprocessing scaler for MSC spatial data ..."
        mscfobj.next_pt_idx = 0
        scaler = StandardScaler()
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.birch.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                scaler.partial_fit(ipca.transform(mscdata[mscbool, 0:-1]))
            else:
                scaler.partial_fit(mscdata[mscbool, 0:-1])
                
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))

        # Train the BIRCH
        print
        print "\tTraining the BIRCH cluster ..."
        mscfobj.next_pt_idx = 0
        brc = Birch(n_clusters=n_clusters)
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.birch.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                brc.partial_fit(scaler.transform(ipca.transform(mscdata[mscbool, 0:-1])))
            else:
                brc.partial_fit(scaler.transform(mscdata[mscbool, 0:-1]))
            
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))
        
        # Predict the label of points after feeding all points to
        # BIRCH
        print
        print "\tPredicting BIRCH clustering labels ..."
        # Rewind the MSC file object to read points from the
        # beginning.
        mscfobj.next_pt_idx = 0
        for i in xrange(niter):
            mscdata = mscfobj.read(npts=self.birch.pf_npts, use_scales=use_scales)
            mscbool = self.validhit_bool[mscdata[:, -1].astype(int)-1]
            if np.sum(mscbool) == 0:
                if self.verbose:
                    # debug
                    print "\t\tno valid points, {0:d} / {1:d}".format(i, niter)
                continue
            if pca_flag:
                self.labels[mscdata[mscbool, -1].astype(int)-1] = brc.predict(scaler.transform(ipca.transform(mscdata[mscbool, 0:-1])))
            else:
                self.labels[mscdata[mscbool, -1].astype(int)-1] = brc.predict(scaler.transform(mscdata[mscbool, 0:-1]))
                
            mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom
            sys.stdout.write("{0:d} / {1:d}: {2:.2f}\n".format(i, niter, mem))
                                                  
        mscfobj.close()

    def specBIRCH(self, n_clusters, spectralptsfile):
        """
        Use BIRCH clustering on spectral data only.
        """
        self.classifier = "Spectral-BIRCH"
        self.inptsfile = spectralptsfile
        points = self.loadPoints()
        points = points[self.validhit_bool, :]

        print "Running BIRCH clustering on spectral data only ..."
        points = StandardScaler(copy=False).fit_transform(points)
        brc = Birch(n_clusters=n_clusters)
        # Feed the points to the BIRCH gradually
        npts = len(points)
        niter = int(npts/self.birch.pf_npts) + 1
        for i in xrange(niter-1):
            brc.partial_fit(points[i*self.birch.pf_npts:(i+1)*self.birch.pf_npts, :])
        brc.partial_fit(points[(niter-1)*self.birch.pf_npts:, :])
        self.labels[self.validhit_bool] = brc.predict(points)

    def ssBIRCH(self, n_clusters):
        """
        Use BIRCH clustering on both spectral and spatial data.
        """
        self.classifier = "Spectral-Spatial-BIRCH"
        print "TODO"
        
    def randomForestTransform(self, points, n_forests, n_transdims):
        """
        Transform the original data into a high dimensional space with the
        dissimilarity measure from random forest.
        """
        transpoints = np.zeros((points.shape[0], n_transdims))
        hasher = RandomTreesEmbedding(n_estimators=100, n_jobs=-1)
        pca = TruncatedSVD(n_components=n_transdims)
        for nf in range(n_forests):
            print "Try transforming data with tree {0:d}".format(nf)
            transpoints += pca.fit_transform(hasher.fit_transform(points))
        transpoints = transpoints/n_forests

        return transpoints

    def loadPoints(self, inptsfile=None):
        """
        Read data from input file and prep data for clustering
        """
        print "Reading data from input point cloud and preparing data for clustering ..."
        
        ind = (self.cind['d_I_nir'], self.cind['d_I_swir'], self.cind['range'], self.cind['d0_nir'], self.cind['d0_swir'])

        if inptsfile is None:
            inptsfile = self.inptsfile

        if inptsfile is None:
            raise RuntimeError("Input point cloud file is neither provided by the DWELPointsCluster class instance nor given to the loadPoints function")
        
        data = np.loadtxt(inptsfile, usecols=ind, comments=None, delimiter=',', \
                              skiprows=self.headerlines)

        # get valid point indices (not zero-hit point)
        # self.validhit_ind = np.where(data[:, 2]>1e-10)[0]
        self.validhit_bool = data[:, 2]>1e-6
        # # remove ground points from the analysis and classification
        # self.validhit_bool = np.logical_and(self.validhit_bool, data[:, 5]<1e-6)
        
        self.labels = np.zeros(len(data), dtype=int)-1
        self.ndi = np.zeros(len(data))-2.0

        # get NDI from the uncalibrated/raw intensity for comparison
        self.ndi0 = np.zeros(len(data)) - 2.0

        self.ndi[self.validhit_bool] = (data[self.validhit_bool, 0] - data[self.validhit_bool, 1])/(data[self.validhit_bool, 0] + data[self.validhit_bool, 1])
        
        self.ndi0[self.validhit_bool] = (data[self.validhit_bool, 3] - data[self.validhit_bool, 4])/(data[self.validhit_bool, 3] + data[self.validhit_bool, 4])
        # also no interpolated values for missing NIR or SWIR raw intensity. no NDI for these points
        tmp_bool = np.logical_or(data[:, 3].astype(int) == 0, data[:, 4].astype(int) == 0)
        self.ndi0[tmp_bool] = -2.0
        
        # ndi, rho_app_nir, rho_app_swir, no range
        # points = np.hstack((self.ndi[self.validhit_bool].reshape((np.sum(self.validhit_bool), 1)), \
        #                              data[self.validhit_bool, 0:2])).astype(np.float32)
        points = np.hstack((self.ndi.reshape(len(self.ndi), 1), data[:, 0:2])).astype(np.float32)
        # # ndi, rho_app_nir, rho_app_swir, with range
        # points = np.hstack((self.ndi[self.validhit_bool].reshape((len(self.validhit_bool), 1)), data[self.validhit_bool, 0:3])).astype(np.float32)

        # self.data = data
        return points
        
    
    def writeClusterLabels(self, outfile, multiout=False):
        """
        Write cluster labels an output file by adding a column to the input
        point cloud file
        """
        if multiout:
            print "Writing classification to multiple output files, one class per file ..."
            # Write classified points to different files, one file for one class for
            # easy display in CloudCompare
            fileprefix = ".".join(outfile.split(".")[0:-1])
            cl_max = np.max(self.labels)
            namefmtstr = "_{0:0>"+str(len(str(cl_max)))+"d}.txt"
            ulabels, label_inv = np.unique(self.labels, return_inverse=True)
            outfobjs = [open(fileprefix+namefmtstr.format(cl), 'w') for cl in ulabels]

            headerstr = ""
            npts = len(self.labels)
            with open(self.inptsfile, 'r') as infobj:
                headerstr += infobj.readline().rstrip('\n')+"[Clustering by {0:s}]\n".format(self.classifier)
                infobj.readline()
                headerstr += "Run made at: "+time.strftime("%c")+"\n"
                headerstr += infobj.readline().rstrip('\n')+",ndi,ndi0,clabel\n"

                junk = [ fobj.write(headerstr) for fobj in outfobjs ]

                for n, (si, si0, label) in enumerate(itertools.izip(self.ndi, self.ndi0, self.labels)):
                    outfobjs[label_inv[n]].write(infobj.readline().rstrip('\n')+",{0:.3f},{1:.3f},{2:d}\n".format(si, si0, label))
                    if self.verbose and (n % 1000 == 0):
                        sys.stdout.write("Writing points {0:d} %        \r".format((n*100)/npts))

            junk = [ fobj.close() for fobj in outfobjs ]
        else:
            # Write all classified points to a single file
            print "Writing classification to one output file ..."
            npts = len(self.labels)
            headerstr = ""
            with open(self.inptsfile, 'r') as infobj, open(outfile, 'w') as outfobj:
                headerstr += infobj.readline().rstrip('\n')+"[Clustering by {0:s}]\n".format(self.classifier)
                infobj.readline()
                headerstr += "Run made at: "+time.strftime("%c")+"\n"
                headerstr += infobj.readline().rstrip('\n')+",ndi,ndi0,clabel\n"
                outfobj.write(headerstr)

                # outfobj.write(infobj.readline().rstrip('\n')+"[Clustering by KMeans]\n")
                # infobj.readline()
                # outfobj.write("Run made at: "+time.strftime("%c")+"\n")
                # outfobj.write(infobj.readline().rstrip('\n')+",clabel\n")

                for n, (si,si0, label) in enumerate(itertools.izip(self.ndi, self.ndi0, self.labels)):
                    outfobj.write(infobj.readline().rstrip('\n')+",{0:.3f},{1:.3f},{2:d}\n".format(si, si0, label))
                    if self.verbose and (n % 1000 == 0):
                        sys.stdout.write("Writing points {0:d} %        \r".format((n*100)/npts))
