import sys
import os
import time

import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.ensemble import RandomTreesEmbedding
from sklearn.decomposition import TruncatedSVD

class DWELPointsCluster:
    """
    Method to cluster DWEL spectral points as unsupervised classification.

    AUTHORS:

        Zhan Li, zhanli86@bu.edu
    """

    def __init__(self, spectralptsfile, verbose=False):
        self.inptsfile = spectralptsfile

        self.verbose = verbose

        # set some parameters
        self.headerlines = 3
        cind = {'x':0, 'y':1, 'z':2, 'd_I_nir':3, 'd_I_swir':4, \
                    'return_number':5, 'number_of_returns':6, 'shot_number':7, \
                    'range':8, 'theta':9, 'phi':10, 'sample':11, 'line':12, \
                    'fwhm_nir':13, 'fwhm_swir':14, 'qa':15}
        self.cind = cind

    def kmeans(self, n_clusters):
        """
        Use k-means clustering
        """
        points = self.loadPoints()
        # points = self.randomForestTransform(5, 10)

        print "Running KMeans clustering ..."
        points = StandardScaler(copy=False).fit_transform(points)
        mbk = MiniBatchKMeans(n_clusters=n_clusters)
        mbk.fit(points)
        self.labels[self.validhit_ind] = mbk.labels_

    def randomForestTransform(self, n_forests, n_transdims):
        """
        Transform the original data into a high dimensional space with the
        dissimilarity measure from random forest.
        """
        transpoints = np.zeros((self.points.shape[0], n_transdims))
        hasher = RandomTreesEmbedding(n_estimators=100, n_jobs=-1)
        pca = TruncatedSVD(n_components=n_transdims)
        for nf in range(n_forests):
            print "Try transforming data with tree {0:d}".format(nf)
            transpoints += pca.fit_transform(hasher.fit_transform(self.points))
        transpoints = transpoints/n_forests

        return transpoints

    def loadPoints(self):
        """
        Read data from input file and prep data for clustering
        """
        print "Reading data from input point cloud and preparing data for clustering ..."
        
        ind = (self.cind['d_I_nir'], self.cind['d_I_swir'], self.cind['range'])

        data = np.loadtxt(self.inptsfile, usecols=ind, comments=None, delimiter=',', \
                              skiprows=self.headerlines)

        # get valid point indices (not zero-hit point)
        self.validhit_ind = np.where(data[:, 2]>1e-10)[0]
        self.labels = np.zeros(len(data), dtype=int)-1
        self.ndi = np.zeros(len(data))-2.0

        data = data[self.validhit_ind, :]
        self.ndi[self.validhit_ind] = (data[:, 0] - data[:, 1])/(data[:, 0] + data[:, 1])

        # ndi, rho_app_nir, rho_app_swir, no range
        self.points = np.hstack((self.ndi[self.validhit_ind].reshape((len(self.validhit_ind), 1)), \
                                     data[:, 0:2])).astype(np.float32)
        # # ndi, rho_app_nir, rho_app_swir, with range
        # self.points = np.hstack((self.ndi[self.validhit_ind].reshape((len(self.validhit_ind), 1)), data[:, 0:3])).astype(np.float32)

        return self.points

    def writeClusterLabels(self, outfile):
        """
        Write cluster labels an output file by adding a column to the input
        point cloud file
        """
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
            headerstr += infobj.readline().rstrip('\n')+"[Clustering by KMeans]\n"
            infobj.readline()
            headerstr += "Run made at: "+time.strftime("%c")+"\n"
            headerstr += infobj.readline().rstrip('\n')+",ndi,clabel\n"

            junk = [ fobj.write(headerstr) for fobj in outfobjs ]
            
            for n, (si, label) in enumerate(zip(self.ndi, self.labels)):
                outfobjs[label_inv[n]].write(infobj.readline().rstrip('\n')+",{0:.3f},{1:d}\n".format(si, label))
                if self.verbose and (n % 1000 == 0):
                    sys.stdout.write("Writing points {0:d}        \r".format((n*100)/npts))

        junk = [ fobj.close() for fobj in outfobjs ]

        # Write all classified points to a single file
        # npts = len(self.labels)
        # with open(self.inptsfile, 'r') as infobj, open(outfile, 'w') as outfobj:
        #     outfobj.write(infobj.readline().rstrip('\n')+"[Clustering by KMeans]\n")
        #     infobj.readline()
        #     outfobj.write("Run made at: "+time.strftime("%c")+"\n")
        #     outfobj.write(infobj.readline().rstrip('\n')+",clabel\n")
        #     for n, label in enumerate(self.labels):
        #         outfobj.write(infobj.readline().rstrip('\n')+",{0:d}\n".format(label))
        #         if self.verbose and (n % 1000 == 0):
        #             sys.stdout.write("Writing points {0:d}        \r".format((n*100)/npts))
    
