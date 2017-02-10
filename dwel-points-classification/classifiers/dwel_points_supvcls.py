import sys

import itertools

import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation

import dwel_points_utils as dpu

class DWELPointsClassifier:
    """
    Supervised classifier of DWEL spectral points.

    AUTHORS:

        Zhan Li, zhanli86@bu.edu
    """

    def __init__(self, verbose=False, pf_npts=1e5):
        self.verbose = verbose
        self.pf_npts=int(1e5)

    def runRandomForest(self, spectral_points_file=None, msc_file=None, \
                        spectral_training_files=None, msc_training_files=None, class_labels=None, \
                        **params):
        if (spectral_points_file is None) != (spectral_training_files is None):
            raise RuntimeError("Inputs of spectral points to be classified and to be training must appear in pair")
        if (msc_file is None) != (msc_training_files is None):
            raise RuntimeError("Inputs of MSC data to be classified and to be training must appear in pair")
        if (spectral_points_file is None) and (msc_file is None):
            raise RuntimeError("Neither spectral nor spatial attributes are provided for classification")

        print "Reading training data ..."
        # read training data
        train_X, train_y = self.readTraining(spectral_training_files, msc_training_files)

        # set up a string to show the features to be used
        feature_names = ["" for i in range(train_X.shape[1])]
        nfeatures = len(feature_names)
        f_idx = 0
        if spectral_training_files is not None:
            feature_names[0] = 'ndi'
            feature_names[1] = 'd_I_nir'
            feature_names[2] = 'd_I_swir'
            f_idx = 3
        if msc_training_files is not None:
            tmp = int((nfeatures - f_idx)/2)
            for i in range(tmp):
                feature_names[f_idx+i] = 'msc_a_{0:d}'.format(i+1)
            f_idx = f_idx+tmp
            for i in range(tmp):
                feature_names[f_idx+i] = 'msc_b_{0:d}'.format(i+1)

        # Initialize RF classifier
        rf = RandomForestClassifier(**params)

        # Cross validation
        cv_train_X, cv_test_X, cv_train_y, cv_test_y = train_test_split(train_X, train_y, test_size=0.25, stratify=train_y)
        rf.fit(cv_train_X, cv_train_y)
        print "Cross validation with 25% stratified samples in the test: {0:3f}".format(rf.score(cv_test_X, cv_test_y))
        
        # train RF
        print "Training Random Forest with all training data samples ..."
        rf.fit(train_X, train_y)
        print "Features and their importance for the classification:"
        print ','.join([fn for fn in feature_names])
        fmtstr = ','.join(['{{0[{0:d}]:.6f}}'.format(i) for i in range(nfeatures)])
        print fmtstr.format(rf.feature_importances_)

        # predict labels

        if spectral_points_file is not None:
            print 'Preparing point spectral attibutes ...'
            spec_points = self._prepSpecPoints(spectral_points_file)

        if msc_file is not None:
            mscfobj = dpu.openMSC(msc_file)
            npts = mscfobj.header[0]
            nscales = len(mscfobj.header[1])
            if (spectral_points_file is not None) and (npts != len(spec_points)):
                raise RuntimeError("Input spectral points file and MSC file have different number of points! Check your inputs!")
        else:
            npts = len(spec_points)

        nbatch = int(npts/self.pf_npts) + 1
        beg_idx = np.arange(nbatch, dtype=np.int)*int(self.pf_npts)
        end_idx = np.copy(beg_idx)
        end_idx[0:-1] = beg_idx[1:]
        end_idx[-1] = int(npts)
        pred_labels = np.empty(npts, dtype=train_y.dtype)
        pred_proba = np.zeros(npts)
        print "Predicting labels of input points ..."
        if self.verbose:
            sys.stdout.write('\tpercent ...')
            progress_cnt=1
        for n, (bi, ei) in enumerate(itertools.izip(beg_idx, end_idx)):
            if msc_file is not None:
                msc_data = mscfobj.read(npts=self.pf_npts)
                if spectral_points_file is not None:
                    data = np.hstack((spec_points[msc_data[:, -1].astype(int)-1, :], msc_data[:, 0:2*nscales]))
                else:
                    data = msc_data[:, 0:2*nscales]
                data_idx = msc_data[:, -1].astype(int)-1
            else:
                data = spec_points[bi:ei]
                data_idx = np.arange(bi, ei, dtype=np.int)
            pred_labels[data_idx] = rf.predict(data)
            pred_proba[data_idx] = rf.predict_proba(data)
            if self.verbose and (n*self.pf_npts+ei-bi > progress_cnt*npts*0.1):
                sys.stdout.write('{0:d}...'.format(int((n*self.pf_npts+ei-bi)/float(npts)*100)))
                sys.stdout.flush()
                progress_cnt = progress_cnt + 1
        if self.verbose:
            sys.stdout.write('100\n')
            sys.stdout.flush()

        if msc_file is not None:
            mscfobj.close()

        return pred_labels, pred_proba
            
            
    def readTraining(self, spectral_training_files=None, msc_training_files=None, \
                     class_labels=None):
        if (spectral_training_files is not None) and (msc_training_files is not None):
            if len(spectral_training_files) != len(msc_training_files):
                raise RuntimeError("Different number of spectral and MSC training files")
            
        if spectral_training_files is not None:
            nspecf = len(spectral_training_files)
            if class_labels is None:
                class_labels = np.arange(nspecf) + 1
            if len(class_labels) != nspecf:
                raise RuntimeError("Number of given class labels is different from that of given spectral training files")
            spec_training_list = [self._prepSpecPoints(fname) for fname in spectral_training_files]
        
        if msc_training_files is not None:
            nmscf = len(msc_training_files)
            if class_labels is None:
                class_labels = np.arange(nmscf) + 1
            if len(class_labels) != nmscf:
                raise RuntimeError("Number of given class labels is different from that of given MSC training files")
            msc_fobj_list = [dpu.openMSC(fname) for fname in msc_training_files]
            msc_training_list = [fobj.read() for fobj in msc_fobj_list]
            msc_nscales_list = [len(fobj.header[1]) for fobj in msc_fobj_list]
            _ = [fobj.close() for fobj in msc_fobj_list]

        data_list = list()
        y_list = list()
        if (spectral_training_files is not None) and (msc_training_files is not None):
            for spec, msc, cls, ns in itertools.izip(spec_training_list, msc_training_list, class_labels, msc_nscales_list):
                data = np.hstack((spec[msc[:, -1].astype(int)-1, :], msc[:, 0:2*ns]))
                y = np.tile(cls, len(spec))
                tmp_flag = np.logical_not(np.isnan(data).any(axis=1))
                data_list.append(data[tmp_flag, :])
                y_list.append(y[tmp_flag])
        elif spectral_training_files is not None:
            for spec, cls in itertools.izip(spec_training_list, class_labels):
                data = spec
                y = np.tile(cls, len(spec))
                tmp_flag = np.logical_not(np.isnan(data).any(axis=1))
                data_list.append(data[tmp_flag, :])
                y_list.append(y[tmp_flag])
        elif msc_training_files is not None:
            for msc, cls, ns in itertools.izip(msc_training_list, class_labels, msc_nscales_list):
                data = msc[:, 0:2*ns]
                y = np.tile(cls, len(msc))
                tmp_flag = np.logical_not(np.isnan(data).any(axis=1))
                data_list.append(data[tmp_flag, :])
                y_list.append(y[tmp_flag])
        else:
            raise RuntimeError("Neither spectral nor spatial traing data is provided")
        
        return np.vstack(data_list), np.hstack(y_list)
            

    def _prepSpecPoints(self, spectral_points_file):
        data = dpu.loadPoints(spectral_points_file, \
                              usecols=['d_i_nir', 'd_i_swir', 'range'])
        valid_flag = data[:, 2]>1e-6
        ndi = np.zeros(len(data)) + np.nan
        ndi[valid_flag] = (data[valid_flag, 0] - data[valid_flag, 1]) / (data[valid_flag, 0] + data[valid_flag, 1])
        return np.hstack((ndi.reshape(len(ndi), 1), data[:, 0:2]))

    
    def writeClassification(self, out_file, pred_labels, pred_proba=None, spectral_points_file=None, msc_file=None):
        if self.verbose:
            sys.stdout.write("Writing classification ")
            sys.stdout.flush()

        npts = len(pred_labels)
        if spectral_points_file is None:
            if msc_file is not None:
                mscfobj = dpu.openMSC(msc_file)
                if npts != mscfobj.header[0]:
                    raise RuntimeError("Given class label and MSC file have different number of points")
                nscales = len(mscfobj.header[1])
                nbatch = int(npts/self.pf_npts) + 1
                beg_idx = np.arange(nbatch, dtype=np.int)*int(self.pf_npts)
                end_idx = np.copy(beg_idx)
                end_idx[0:-1] = beg_idx[1:]
                end_idx[-1] = int(npts)                
                if pred_proba is None:
                    headerstr = '{0:s} x,y,z,class,'.format(dpu._dwel_points_ascii_scheme['comments']) \
                                + ','.join(['a_{0:d},b_{0:d}'.format(i+1) for i in range(nscales)])
                else:
                    headerstr = '{0:s} x,y,z,class,proba,'.format(dpu._dwel_points_ascii_scheme['comments']) \
                                + ','.join(['a_{0:d},b_{0:d}'.format(i+1) for i in range(nscales)])
                with open(out_file, 'w') as outfobj:
                    if self.verbose:
                        sys.stdout.write('\n\tpercent ...')
                        progress_cnt=1
                    outfobj.write('{0:s}\n'.format(headerstr))
                    for n, (bi, ei) in enumerate(itertools.izip(beg_idx, end_idx)):
                        msc_data = mscfobj.read(npts=self.pf_npts)
                        for i in range(ei-bi):
                            if pred_proba is None:
                                outfobj.write('{1[0]:.3f},{1[1]:.3f},{1[2]:.3f},{0:d},'.format(pred_labels[msc_data[i, -1].astype(int)-1]), msc_data[i, -4:-1])
                            else:
                                outfobj.write('{1[0]:.3f},{1[1]:.3f},{1[2]:.3f},{0:d},{2:.3f},'.format(pred_labels[msc_data[i, -1].astype(int)-1], msc_data[i, -4:-1], pred_proba[msc_data[i, -1].astype(int)-1]))
                            for s in range(nscales-1):
                                outfobj.write('{0:.3f},{1:.3f},'.format(msc_data[i, s], msc_data[i, s+nscales]))
                                outfobj.write('{0:.3f},{1:.3f}\n'.format(msc_data[i, s+1], msc_data[i, s+1+nscales]))
                        if self.verbose and (n*self.pf_npts+ei-bi > npts*0.1*progress_cnt):
                            sys.stdout.write('{0:d}...'.format(int((n*self.pf_npts+ei-bi)/float(npts)*100)))
                            sys.stdout.flush()
                            progress_cnt = progress_cnt + 1
                    if self.verbose:
                        sys.stdout.write('100\n')
                        sys.stdout.flush()
                mscfobj.close()
        else:
            spec_header = dpu._dwel_points_ascii_scheme['skip_header']
            
            # # See if the spectral point cloud file has the column of
            # # ground_label. If so, we will replace the class label of
            # # these points with a new ground class label.
            # with open(spectral_points_file) as specfobj:
            #     for i in range(spec_header):
            #         specfobj.readline()
            #     colname_str = specfobj.readline().strip()
            #     if colname_str.find('ground_label') > -1:
            #         ground_label = dpu.loadPoints(spectral_points_file, usecols=['ground_label'])
            #         if isinstance(pred_labels[0], basestring):
            #             ground_clsname = 'ground_from_spec'
            #         else:
            #             ground_clsname = np.max(pred_labels) + 1
            #         tmpind = np.where(ground_label!=0)[0]
            #         pred_labels[tmpind] = ground_clsname
            #         if pred_proba is not None:
            #             pred_proba[tmpind] = -1
            
            if msc_file is not None:
                out_file_msc = '.'.join(out_file.split('.')[0:-1]) + '_msc.txt'
                out_file_spec = '.'.join(out_file.split('.')[0:-1]) + '_spectral.txt'
                print ""
                print "Classification result will be written twice in two files with one attaching spectral attributes and the other spatial attibutes."
            else:
                out_file_spec = '.'.join(out_file.split('.')[0:-1]) + '_spectral.txt'
                print ""
                print "Classification result will be written in one file attaching spectral attributes."
            
            with open(spectral_points_file) as specfobj, open(out_file_spec, 'w') as outfobj:
                print "Attaching class with spectral attributes to: "
                print "\t{0:s}".format(out_file_spec)
                if self.verbose:
                    sys.stdout.write('\tpercent ...')
                for i in range(spec_header):
                    outfobj.write("{0:s}".format(specfobj.readline()))
                if pred_proba is None:
                    outfobj.write("{0:s},class\n".format(specfobj.readline().strip()))
                else:
                    outfobj.write("{0:s},class,proba\n".format(specfobj.readline().strip()))
                comment_linecnt = 0
                for i, line in enumerate(specfobj):
                    if line.lstrip().find(dpu._dwel_points_ascii_scheme["comments"]) == 0:
                        comment_linecnt = comment_linecnt + 1
                        continue
                    if pred_proba is None:
                        outfobj.write("{0:s},{1:d}\n".format(line.strip(), pred_labels[i-comment_linecnt]))
                    else:
                        outfobj.write("{0:s},{1:d},{2:.3f}\n".format(line.strip(), pred_labels[i-comment_linecnt], pred_proba[i-comment_linecnt]))
                    if self.verbose and (i % int(npts*0.1) == 0):
                        sys.stdout.write("{0:d}...".format(int(float(i)/npts*100)))
                        sys.stdout.flush()
                if self.verbose:
                    sys.stdout.write("100\n")
                    sys.stdout.flush()

            if msc_file is not None:
                # points = dpu.loadPoints(spectral_points_file, usecols=['x', 'y', 'z'])

                mscfobj = dpu.openMSC(msc_file)
                if npts != mscfobj.header[0]:
                    raise RuntimeError("Given class label and MSC file have different number of points")
                nscales = len(mscfobj.header[1])
                nbatch = int(npts/self.pf_npts) + 1
                beg_idx = np.arange(nbatch, dtype=np.int)*int(self.pf_npts)
                end_idx = np.copy(beg_idx)
                end_idx[0:-1] = beg_idx[1:]
                end_idx[-1] = int(npts)                
                if pred_proba is None:
                    headerstr = '{0:s} x,y,z,class,'.format(dpu._dwel_points_ascii_scheme['comments']) \
                                +','.join(['a_{0:d},b_{0:d}'.format(i+1) for i in range(nscales)])
                    fmtstr = ','.join(['{{0[{0:d}]:.3f}}'.format(i) for i in range(3)]) + ',' \
                             + '{1:d},' \
                             + ','.join(['{{2[{0:d}]:.3f}},{{2[{1:d}]:.3f}}'.format(i, i+nscales) for i in range(nscales)]) \
                             + '\n'
                else:
                    headerstr = '{0:s} x,y,z,class,proba,'.format(dpu._dwel_points_ascii_scheme['comments']) \
                                +','.join(['a_{0:d},b_{0:d}'.format(i+1) for i in range(nscales)])
                    fmtstr = ','.join(['{{0[{0:d}]:.3f}}'.format(i) for i in range(3)]) + ',' \
                             + '{1:d},{2:.3f},' \
                             + ','.join(['{{3[{0:d}]:.3f}},{{3[{1:d}]:.3f}}'.format(i, i+nscales) for i in range(nscales)]) \
                             + '\n'
                with open(spectral_points_file) as specfobj, open(out_file_msc, 'w') as outfobj:
                    print "Attaching class with spatial attributes to: "
                    print "\t{0:s}".format(out_file_msc)
                    if self.verbose:
                        sys.stdout.write('\tpercent ...')
                        progress_cnt=1
                    for i in range(spec_header):
                        outfobj.write("{0:s}".format(specfobj.readline()))
                    outfobj.write('{0:s}\n'.format(headerstr))

                    for n, (bi, ei) in enumerate(itertools.izip(beg_idx, end_idx)):
                        msc_data = mscfobj.read(npts=self.pf_npts)
                        msc_idx = msc_data[:, -1].astype(int)-1
                        for i in range(ei-bi):
                            if pred_proba is None:
                                # outfobj.write(fmtstr.format(points[msc_idx[i], :], pred_labels[msc_idx[i]], msc_data[i,:]))
                                outfobj.write(fmtstr.format(msc_data[i, -4:-1], pred_labels[msc_idx[i]], msc_data[i,:]))
                            else:
                                # outfobj.write(fmtstr.format(points[msc_idx[i], :], pred_labels[msc_idx[i]], pred_proba[msc_idx[i]], msc_data[i,:]))
                                outfobj.write(fmtstr.format(msc_data[i, -4:-1], pred_labels[msc_idx[i]], pred_proba[msc_idx[i]], msc_data[i,:]))
                        if self.verbose and (n*self.pf_npts+ei-bi > npts*0.1*progress_cnt):
                            sys.stdout.write('{0:d}...'.format(int((n*self.pf_npts+ei-bi)/float(npts)*100)))
                            sys.stdout.flush()
                            progress_cnt = progress_cnt + 1
                    if self.verbose:
                        sys.stdout.write('100\n')
                        sys.stdout.flush()
                mscfobj.close()
