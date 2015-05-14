"""
A new version of spdtlsfile module for Zhan Li's own test and use for DWEL data.

Adapted from John Armston's original version.
"""

import h5py
import numpy as np
np.seterr(all='ignore')
import sys

from spdtlstools.spdtlserrors import *


class SPDFileIterator(object):
    """
    Class to allow iteration across an SPDFile instance.
    Do not instantiate this class directly - it is created by SPDFile.__iter__().
    Returns a numpy array pair for each iteration   
    """
    def __init__(self,filehandle):
        self.filehandle = filehandle
        self.row = 0
        
    def __iter__(self):
        return self

    def next(self):
        return self.__next__()
        
    def __next__(self):
        try:
            pulsedata,pointdata = self.filehandle.readSPDRows(self.row,recarray=False)
            self.row += 1
        except OutsideBoundsError:
            raise StopIteration()
        
        return self.row-1,pulsedata,pointdata


class SPDFile:
    """
    Some methods to read and write an SPD file
    """

    def __init__(self,infile,resfactor=1,ybinsize=None,rowstart=0):
        self.f = h5py.File(infile, 'a')
        self.resfactor = resfactor
        self.yblockstart = 0
        self.rowstart = rowstart
        if self.f['HEADER']["PULSE_INDEX_METHOD"][0] > 0:
            if ybinsize is None:
                ybinsize = self.f['HEADER']['BIN_SIZE'][0]
            self.yblocksize = int(ybinsize / self.f['HEADER']['BIN_SIZE'][0])
            self.nyblocks = int(np.ceil(self.f['HEADER']['NUMBER_BINS_Y'][0] / self.yblocksize))

    
    def __iter__(self):           
        return SPDFileIterator(self)


    def closeSPDFile(self):
        """
        Close the SPD header
        """
        self.f.close()
        

    def readSPDHeader(self):
        """
        Read the SPD header
        """
        dictn = {}
        for name,obj in self.f['HEADER'].items():
            if obj[()].size == 1:
                dictn[name] = obj[0]
            else:
                dictn[name] = obj[()]
        return dictn


    def readSPDWaveforms(self,pulsedata,field='RECEIVED'):
        """
        Read a block of waveform data. Returns as a 2D array.
        """
        
        if field == 'RECEIVED':
            nbins = pulsedata.NUMBER_OF_WAVEFORM_RECEIVED_BINS
            binstart = pulsedata.RECEIVED_START_IDX[0]
            binend = pulsedata.RECEIVED_START_IDX[-1] + nbins[-1]
        elif field == 'TRANSMITTED':
            nbins = pulsedata.NUMBER_OF_WAVEFORM_TRANSMITTED_BINS
            binstart = pulsedata.TRANSMITTED_START_IDX[0]
            binend = pulsedata.TRANSMITTED_START_IDX[-1] + nbins[-1]    
        else:
            raise AttributeError('%s is not a recognised waveform attribute' % field)
        
        if binstart < binend:
            
            waveformdata = self.f['DATA'][field][binstart:binend]
            maxn = np.max(nbins)
            pulse_idx,bin_idx = np.mgrid[0:nbins.size,0:maxn]
            mask = bin_idx < nbins[:,np.newaxis]
            waveformdata2D = np.ma.masked_all((nbins.size,maxn),dtype=waveformdata.dtype)
            waveformdata2D[pulse_idx[mask],bin_idx[mask]] = waveformdata
            
            return waveformdata2D
            
        else:
            
            return None
        

    def readSPDRows(self,row,recarray=True):
        """
        Read rows of pulse and point data

        Actually here only read one row (defined by one ybinsize) of pulse and
        point data. But it could be multiple rows (defined by the binsize of SPD
        file itself) if ybinsize is larger than SPD file's binsize
        """
        
        self.yblockstart = self.rowstart + row * self.yblocksize
        yblockend = min(self.yblockstart+self.yblocksize, self.f['HEADER']['NUMBER_BINS_Y'][0])     
        if self.yblockstart >= yblockend:
            raise OutsideBoundsError("start block = %i; endblock = %i" % (self.yblockstart,yblockend))
        
        cnt = self.f['INDEX']['PLS_PER_BIN'][self.yblockstart:yblockend]
        if cnt.any():
            
            idx = self.f['INDEX']['BIN_OFFSETS'][self.yblockstart:yblockend]
            
            if idx.ndim == 1:
                idx.shape = 1,idx.size
                cnt.shape = 1,cnt.size
            
            yblocksize = yblockend - self.yblockstart
            pulsedata = self.f['DATA']['PULSES'][idx[0,0]:idx[yblocksize-1,-1]+cnt[yblocksize-1,-1]]
            
            start = pulsedata['PTS_START_IDX'][0]
            finish = pulsedata['PTS_START_IDX'][-1] + pulsedata['NUMBER_OF_RETURNS'][-1]
            
            if start < finish:
                
                pointdata = self.f['DATA']['POINTS'][start:finish]
                            
                if self.resfactor > 1:
                    
                    mask = pulsedata['NUMBER_OF_RETURNS'] > 0
                    keep = (pulsedata['SCANLINE'][mask] % self.resfactor == 0) & (pulsedata['SCANLINE_IDX'][mask] % self.resfactor == 0)
                    pointdata = pointdata[np.repeat(keep, pulsedata['NUMBER_OF_RETURNS'][mask])]
                    pulsedata = pulsedata[keep]
        
                if recarray:
                    return pulsedata.view(np.recarray),pointdata.view(np.recarray)
                else:
                    return pulsedata,pointdata
                
            else:
            
                return pulsedata,None
        else:
        
            return None,None


    def readSPDRowsList(self,row,recarray=True):
        """
        Read rows of pulse data and point data but group points in multiple
        lists according to their pulse ID.

        Actually here only read one row (defined by one ybinsize) of pulse and
        point data. But it could be multiple rows (defined by the binsize of SPD
        file itself) if ybinsize is larger than SPD file's binsize
        """
        
        self.yblockstart = self.rowstart + row * self.yblocksize
        yblockend = min(self.yblockstart+self.yblocksize, self.f['HEADER']['NUMBER_BINS_Y'][0])     
        if self.yblockstart >= yblockend:
            raise OutsideBoundsError("start block = %i; endblock = %i" % (self.yblockstart,yblockend))

        cnt = self.f['INDEX']['PLS_PER_BIN'][self.yblockstart:yblockend]
        if cnt.any():
            
            idx = self.f['INDEX']['BIN_OFFSETS'][self.yblockstart:yblockend]
            
            if idx.ndim == 1:
                idx.shape = 1,idx.size
                cnt.shape = 1,cnt.size
            
            yblocksize = yblockend - self.yblockstart
            pulsedata = self.f['DATA']['PULSES'][idx[0,0]:idx[yblocksize-1,-1]+cnt[yblocksize-1,-1]]

            start = pulsedata['PTS_START_IDX'][0]
            finish = pulsedata['PTS_START_IDX'][-1] + pulsedata['NUMBER_OF_RETURNS'][-1]

            if start > finish:
                finish = start
                
            pointdata = self.f['DATA']['POINTS'][start:finish]

            if self.resfactor > 1:
                keep = (pulsedata['SCANLINE'] % self.resfactor == 0) & (pulsedata['SCANLINE_IDX'] % self.resfactor == 0)
                pointdata = pointdata[np.repeat(keep, pulsedata['NUMBER_OF_RETURNS'])]
                pulsedata = pulsedata[keep]

            if recarray:
                pulsedatav = pulsedata.view(np.recarray)
                pointdatav = pointdata.view(np.recarray)
            else:
                pulsedatav = pulsedata
                pointdatav = pointdata

            ptscnt = pulsedata['NUMBER_OF_RETURNS']
            splitind = np.cumsum(ptscnt)[:-1]
            pointslist = np.split(pointdatav, splitind)

            return pulsedatav,np.array(pointslist)

        else:
        
            return None,None

        
    def readSPDRowCols(self,row,startCol,endCol,recarray=True):
        """
        Read a block of puulse and point data from startCol to endCol in a row
        (defined by one ybinsize). It de-facto equals to
        spdpy.readSPDPulsesIntoBlock but also return point data other than pulse
        data

        row, startCol, endCol, with first row/col being 0. startCol is inclusive
        while endCol is exclusive

        Actually here only read one row (defined by one ybinsize) of pulse and
        point data. But it could be multiple rows (defined by the binsize of SPD
        file itself) if ybinsize is larger than SPD file's binsize

        Zhan Li, zhanli86@bu.edu
        """
        
        self.yblockstart = self.rowstart + row * self.yblocksize
        yblockend = min(self.yblockstart+self.yblocksize, self.f['HEADER']['NUMBER_BINS_Y'][0])     
        if self.yblockstart >= yblockend:
            raise OutsideBoundsError("start block = %i; endblock = %i" % (self.yblockstart,yblockend))

        cnt = self.f['INDEX']['PLS_PER_BIN'][self.yblockstart:yblockend, startCol:endCol]
        if cnt.any():
            
            idx = self.f['INDEX']['BIN_OFFSETS'][self.yblockstart:yblockend, startCol:endCol]

            # Read pulses
            npulse = np.sum(cnt)
            pulsedata = np.zeros(npulse, dtype=self.f['DATA']['PULSES'].dtype)
            plsind = np.cumsum(np.ravel(cnt, 'C'))
            for i, c in enumerate(np.ravel(cnt, 'C')):
                if c:
                    if i==0:
                        pulsedata[0:plsind[i]] = self.f['DATA']['PULSES'][idx.flat[i]:idx.flat[i]+c]
                    else:
                        pulsedata[plsind[i-1]:plsind[i]] = self.f['DATA']['PULSES'][idx.flat[i]:idx.flat[i]+c]

            if self.resfactor > 1:
                mask = pulsedata['NUMBER_OF_RETURNS'] > 0
                keep = (pulsedata['SCANLINE'][mask] % self.resfactor == 0) & (pulsedata['SCANLINE_IDX'][mask] % self.resfactor == 0)
                pulsedata = pulsedata[keep]

            # Read points
            ptscnt = pulsedata['NUMBER_OF_RETURNS']
            npts = np.sum(ptscnt)
            if npts:
                ptsind = np.cumsum(ptscnt)
                # build a list indices to points
                ptslistind = np.zeros(npts, dtype=int) - 1
                for i, pc in enumerate(ptscnt):
                    if pc:
                        if i == 0:
                            ptslistind[0:ptsind[i]] = range(pc) + pulsedata['PTS_START_IDX'][i]
                        else:
                            ptslistind[ptsind[i-1]:ptsind[i]] = range(pc) + pulsedata['PTS_START_IDX'][i]
                pointdata = self.f['DATA']['POINTS'][list(np.sort(ptslistind))]
                if recarray:
                    return pulsedata.view(np.recarray), pointdata.view(np.recarray)
                else:
                    return pulsedata, pointdata
            else:
                if recarray:
                    return pulsedata.view(np.recarray), None
                else:
                    return pulsedata, None
        else:
            return None,None


    def readSPDOffset(self,pulseidx,blocksize,recarray=True):
        """
        Read pulse and point data for a number of pulse data records from an offset
        """
        
        finish = min(pulseidx+blocksize, self.f['HEADER']['NUMBER_OF_PULSES'][0])        
        if pulseidx < finish:      
            
            pulsedata = self.f['DATA']['PULSES'][pulseidx:finish]
            
            point_start = pulsedata['PTS_START_IDX'][0]
            point_finish = pulsedata['PTS_START_IDX'][-1] + pulsedata['NUMBER_OF_RETURNS'][-1]
            
            if point_start < point_finish:
                
                pointdata = self.f['DATA']['POINTS'][point_start:point_finish]
                
                if self.resfactor > 1:
                    
                    mask = pulsedata['NUMBER_OF_RETURNS'] > 0
                    keep = (pulsedata['SCANLINE'][mask] % self.resfactor == 0) & (pulsedata['SCANLINE_IDX'][mask] % self.resfactor == 0)
                    pointdata = pointdata[np.repeat(keep, pulsedata['NUMBER_OF_RETURNS'][mask])]
                    pulsedata = pulsedata[keep]
                
                if recarray:
                    return pulsedata.view(np.recarray),pointdata.view(np.recarray)
                else:
                    return pulsedata,pointdata
            
            else:
            
                return pulsedata,None
                
        else:
        
            return None,None


    def updateSPDRowPointFields(self,row,field,data):
        """
        Update a point field in a row of data
        """
        
        if not isinstance(field, list):
            field = [field]
            data = [data]
                  
        self.yblockstart = self.rowstart + row * self.yblocksize
        yblockend = min(self.yblockstart+self.yblocksize, self.f['HEADER']['NUMBER_BINS_Y'][0])     
        if self.yblockstart >= yblockend:
            raise OutsideBoundsError("start block = %i; endblock = %i" % (self.yblockstart,yblockend))
        
        cnt = self.f['INDEX']['PLS_PER_BIN'][self.yblockstart:yblockend]        
        if cnt.any():
            
            idx = self.f['INDEX']['BIN_OFFSETS'][self.yblockstart:yblockend]
            
            if idx.ndim == 1:
                idx.shape = 1,idx.size
                cnt.shape = 1,cnt.size
            
            yblocksize = yblockend - self.yblockstart
            pulsedata = self.f['DATA']['PULSES'][idx[0,0]:idx[yblocksize-1,-1]+cnt[yblocksize-1,-1],'PTS_START_IDX','NUMBER_OF_RETURNS']          
            
            start = pulsedata['PTS_START_IDX'][0]
            finish = pulsedata['PTS_START_IDX'][-1] + pulsedata['NUMBER_OF_RETURNS'][-1]
            
            if start < finish:
                
                try:
                    pointdata = self.f['DATA']['POINTS'][start:finish]
                    for i,fieldname in enumerate(field):
                        pointdata[fieldname] = data[i]
                    self.f['DATA']['POINTS'][start:finish] = pointdata
                except:
                    raise UpdateError("Could not update point data records")


    def updateSPDRowPulseFields(self,row,field,data):
        """
        Update a pulse field in a row of data
        """
        
        if not isinstance(field, list):
            field = [field]
            data = [data]
                  
        self.yblockstart = self.rowstart + row * self.yblocksize
        yblockend = min(self.yblockstart+self.yblocksize, self.f['HEADER']['NUMBER_BINS_Y'][0])     
        if self.yblockstart >= yblockend:
            raise OutsideBoundsError("start block = %i; endblock = %i" % (self.yblockstart,yblockend))
        
        cnt = self.f['INDEX']['PLS_PER_BIN'][self.yblockstart:yblockend]        
        if cnt.any():
            
            idx = self.f['INDEX']['BIN_OFFSETS'][self.yblockstart:yblockend]
            
            if idx.ndim == 1:
                idx.shape = 1,idx.size
                cnt.shape = 1,cnt.size
                
            try:
                yblocksize = yblockend - self.yblockstart
                pulsedata = self.f['DATA']['PULSES'][idx[0,0]:idx[yblocksize-1,-1]+cnt[yblocksize-1,-1],'PTS_START_IDX','NUMBER_OF_RETURNS']
                for i,fieldname in enumerate(field):
                    pulsedata[fieldname] = data[i]
                self.f['DATA']['PULSES'][idx[0,0]:idx[self.yblocksize-1,-1]+cnt[self.yblocksize-1,-1]] = pulsedata
            except:
                raise UpdateError("Could not update pulse data records")
            

    def updateSPDOffsetPulseFields(self,pulseidx,field,data):
        """
        Update pulse data for a number of pulse data records from an offset
        """
        
        if not isinstance(field, list):
            field = [field]
            data = [data]
                   
        finish = min(pulseidx+data[0].size,self.f['HEADER']['NUMBER_OF_PULSES'][0])
        if pulseidx < finish:      
            
            pulsedata = self.f['DATA']['PULSES'][pulseidx:finish]
            
            try:        
                for i,fieldname in enumerate(field):
                    pulsedata[fieldname] = data[i]
                self.f['DATA']['PULSES'][pulseidx:finish] = pulsedata        
            except:
                raise UpdateError("Could not update pulse data records")


    def updateSPDOffsetPointFields(self,pulseidx,field,data):
        """
        Update point data for a number of pulse data records from an offset
        """
        
        if not isinstance(field, list):
            field = [field]
            data = [data]
                   
        finish = min(pulseidx+data[0].size,self.f['HEADER']['NUMBER_OF_PULSES'][0])
        if pulseidx < finish:      
            
            pulsedata = self.f['DATA']['PULSES'][pulseidx:finish]
            
            point_start = pulsedata['PTS_START_IDX'][0]
            point_finish = pulsedata['PTS_START_IDX'][-1] + pulsedata['NUMBER_OF_RETURNS'][-1]
            
            if point_start < point_finish:
                
                pointdata = self.f['DATA']['POINTS'][point_start:point_finish]
            
                try:        
                    for i,fieldname in enumerate(field):
                        pointdata[fieldname] = data[i]
                    self.f['DATA']['POINTS'][point_start:point_finish] = pointdata    
                except:
                    raise UpdateError("Could not update pulse data records")


    def updateSPDHeaderField(self,field,value):
        """
        Update an SPD header field
        """
        self.f['HEADER'][field][()] = value

    
    @staticmethod
    def getNumpyDataType(obj,attr,attributetype='point'):
        """
        Get numpy data type for an SPD field
        """
        if attributetype in ['pulse','waveform']:
            if attr in obj.f['DATA']['PULSES'].dtype.names:
                npdtype = obj.f['DATA']['PULSES'][0,attr].dtype
            else:
                raise IncorrectAttribute('%s is not a recognised pulse or waveform attribute' % attr)
        else:
            if attr in obj.f['DATA']['POINTS'].dtype.names:
                npdtype = obj.f['DATA']['POINTS'][0,attr].dtype
            else:
                raise IncorrectAttribute('%s is not a recognised point attribute' % attr)
        return npdtype
        

    @staticmethod
    def filterPoints(pulsedata,pointdata,returntype,n=1):
        """
        Filter points by returntype:
            1 = nth returns (default n is 1)
            2 = middle returns
            3 = last returns
            4 = single returns     
        """
        
        return_n = pointdata['RETURN_ID'] - np.min(pointdata['RETURN_ID']) + 1
        
        if returntype == 1:
            mask = (return_n == n)
                
        elif returntype == 2:
            n_return = np.repeat(pulsedata['NUMBER_OF_RETURNS'], pulsedata['NUMBER_OF_RETURNS'])
            mask = (return_n != n_return) & (return_n != 1)
                
        elif returntype == 3:
            n_return = np.repeat(pulsedata['NUMBER_OF_RETURNS'], pulsedata['NUMBER_OF_RETURNS'])
            mask = (n_return == return_n)
                
        elif returntype == 4:
            n_return = np.repeat(pulsedata['NUMBER_OF_RETURNS'], pulsedata['NUMBER_OF_RETURNS'])
            mask = (n_return == 1)
            
        else:
            raise IncorrectReturnType("Return type %i not implemented yet" % returntype)
            
        return mask

