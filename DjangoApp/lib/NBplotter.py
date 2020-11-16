import os
import numpy as np
import scipy as sc
#import pandas as pd
import sys
import matplotlib
matplotlib.use('Agg')
from matplotlib import pylab as plt
#import seaborn as sb

import dtt2hdf
from scipy import signal as sig, interpolate
# CHANGE FOR LOCAL
from gwpy.timeseries import TimeSeries
from gwpy.plot import Plot
from gwpy.time import to_gps

from control import matlab
import re

def plot_DARM(start,end,fres,figval=1):
    ch = 'K1:CAL-CS_PROC_DARM_DISPLACEMENT_DQ'

    gps_beg = int(to_gps( start ))
    gps_end = int(to_gps( end ))
    gps_beg_head = int(gps_beg/100000)
    gps_end_head = int(gps_end/100000)
    if gps_beg_head == gps_end_head:
        cache_file="/home/devel/cache/Cache_GPS/%s.cache" % gps_beg_head
    else:
        # merge two cache file
        cache1="/home/devel/cache/Cache_GPS/%s.cache" % gps_beg_headelse
        cache2="/home/devel/cache/Cache_GPS/%s.cache" % gps_end_head
        cache_file="/var/www/html/past_data_viewer/data/%s_%s.cache" % (gps_beg, gps_end)

        with open(cache_file, 'w') as outfile:
            for i in [cache1, cache2]:
                with open(i) as infile:
                    outfile.write(infile.read())

    try:
        data = TimeSeries.read(cache_file, ch, start=gps_beg, end=gps_end, nproc=4)
        #data = TimeSeries.get(ch, start, end, host='k1nds2', port=8088)
    except:
        return 1,'DARM data cannot be obtained. Try with more recent data. %d %d' % (gps_beg, gps_end)
    spectrum = data.asd(1./fres,1./fres/2.)
    tf = sig.ZerosPolesGain([10.,10.,10.,10.,10],[1.,1.,1.,1.,1.],1.e-14)
    freq, mag, phase = sig.bode(tf, spectrum.frequencies.to_value())
    darm = spectrum.value*(10.**(mag/20.))
    fig = plt.figure(figval)
    plt.loglog(freq,darm,label='DARM')
    #plt.loglog(spectrum.frequencies,spectrum.value,label='DARM')
    plt.ylabel(r'Displacement [m/$\sqrt{\rm Hz}$]')
    plt.xlabel('Frequency [Hz]')
    plt.legend()
    plt.grid(True)
    return 0,freq

def plot_DARM_local(start,end,fres,figval=1):
    #ch = 'K1:CAL-CS_PROC_DARM_DISPLACEMENT_DQ'
    data = np.loadtxt('C:\\Users\\ayaka\\Dropbox (個人)\\Shoda\\NoiseSubtraction\\DARMspe.txt')
    ff=data[0]
    spectrum = data[1]
    tf = sig.ZerosPolesGain([10.,10.,10.,10.,10.],[1.,1.,1.,1.,1.],1.e-14)
    freq, mag, phase = sig.bode(tf, ff)
    darm = spectrum*(10.**(mag/20.))
    fig = plt.figure(figval)
    plt.loglog(freq,darm,label='DARM')
    #plt.loglog(spectrum.frequencies,spectrum.value,label='DARM')
    plt.ylabel(r'Displacement [m/$\sqrt{\rm Hz}$]')
    plt.xlabel('Frequency [Hz]')
    plt.legend()
    plt.grid(True)
    return 0,freq


def plot_TheoN(TheoN, fmin, fmax, freq_tot, total, figval=1):
    #print('input freq: '+str(len(freq_tot)))
    #print('input total: '+str(len(total)))
    
    fig = plt.figure(figval)
    status = 0
    for name,conf in TheoN.items():
        ## plot data file
        ans = plot_singleTheoN(conf,freq_tot,total)
        status = ans[0]
        if status == 1:
            return status, ans[1]
        else:
            total = ans[1]
            freq = ans[2]
            line = ans[3]
            plt.figure(figval)
            plt.loglog(freq,line,label=name)
            plt.ylabel(r'Displacement [m/$\sqrt{\rm Hz}$]')
            plt.xlabel('Frequency [Hz]')
            plt.legend()
            plt.grid(True)
            
    return status,total

def plot_RTN(RTN,start,end,fres,freq_tot,total,figval=1):
    
    fig = plt.figure(figval)
    status = 0
    
    for name, conf in RTN.items():
        ans = plot_singleRTN(conf,start,end,fres,freq_tot,total)
        status = ans[0]
        if status == 1:
            return status, ans[1]
        else:
            total = ans[1]
            freq = ans[2]
            line = ans[3]
            plt.figure(figval)
            plt.loglog(freq,line,label=name)
            plt.ylabel(r'Displacement [m/$\sqrt{\rm Hz}$]')
            plt.xlabel('Frequency [Hz]')
            plt.legend()
            plt.grid(True)
        
    return status,total


def plot_Category(Category,start,end,fres,freq_tot,total,figval=1):
    fig = plt.figure(figval)
    status = 0
    for name, Items in Category.items():
        cattotal = np.zeros(len(freq_tot))
        for subname, conf in Items.items():
            if 'equation' in conf:
                ans = plot_singleTheoN(conf,freq_tot,cattotal)
                status = ans[0]
                if status == 1:
                    return status, ans[1]
                else:
                    cattotal = ans[1]
            elif 'chan' in conf:
                ans = plot_singleRTN(conf,start,end,fres,freq_tot,cattotal)
                status = ans[0]
                if status == 1:
                    return status, ans[1]
                else:
                    cattotal = ans[1]
                    
        plt.figure(figval)
        plt.loglog(freq_tot,cattotal,label=name)
        plt.ylabel(r'Displacement [m/$\sqrt{\rm Hz}$]')
        plt.xlabel('Frequency [Hz]')
        plt.legend()
        plt.grid(True)
        
        total = np.sqrt(total*total+cattotal*cattotal)
        
    return status, total

def plot_oneCategonly(name,oneCategory,start,end,fres,freq_tot,figval=1):
    fig = plt.figure(figval)
    status = 0
    cattotal = np.zeros(len(freq_tot))
    for subname, conf in oneCategory.items():
        if 'equation' in conf:
            ans = plot_singleTheoN(conf,freq_tot,cattotal)
            status = ans[0]
            if status == 1:
                return status, ans[1]
            else:
                cattotal = ans[1]
                freq = ans[2]
                line = ans[3]
                plt.figure(figval)
                plt.loglog(freq,line,label=subname)
        elif 'chan' in conf:
            ans = plot_singleRTN(conf,start,end,fres,freq_tot,cattotal)
            status = ans[0]
            if status == 1:
                return status, ans[1]
            else:
                cattotal = ans[1]
                freq = ans[2]
                line = ans[3]
                plt.figure(figval)
                plt.loglog(freq,line,label=subname)
                plt.figure(figval+100)
    plt.figure(figval)
    plt.loglog(freq_tot,cattotal,'k--',linewidth=2.0,label=name+' total')
    plt.ylabel(r'Displacement [m/$\sqrt{\rm Hz}$]')
    plt.xlabel('Frequency [Hz]')
    plt.grid(True)
    plt.legend()
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    plt.subplots_adjust(right=0.7)
    plt.title('NB from '+start+' to '+end)
    return status,freq_tot,cattotal
                

def readzpk(zz,pp,kk):
    zz = zz.replace(' ','')
    pp = pp.replace(' ','')
    zz=zz.split(";")
    pp=pp.split(";")
    try:
        if zz!=['']:
            for i in range(len(zz)):
                if '+i*' in zz[i]:
                    zz_cmp = zz[i].split('+i*')
                    zz[i]=complex(float(zz_cmp[0]),float(zz_cmp[1]))
                elif '-i*' in zz[i]:
                    zz_cmp = zz[i].split('-i*')
                    zz[i]=complex(float(zz_cmp[0]),-1*float(zz_cmp[1]))
                else:
                    zz[i]=complex(zz[i])
        else:
            zz = []
        if pp!=['']:
            for k in range(len(pp)):
                if '+i*' in pp[k]:
                    pp_cmp = pp[k].split('+i*')
                    pp[k]=complex(float(pp_cmp[0]),float(pp_cmp[1]))
                elif '-i*' in pp[k]:
                    pp_cmp = pp[k].split('-i*')
                    pp[k]=complex(float(pp_cmp[0]),-1*float(pp_cmp[1]))
                else:
                    pp[k]=complex(pp[k])
                
        else:
            pp = []
        kk=float(kk)
    except TypeError:
        return False
    return zz, pp, kk
    
def loadxmltf(conf, freq):
    try:
        xmlfile = dtt2hdf.access.DiagAccess(conf['tf_xml'])
    except:
        return 1, 'xml file '+conf['tf_xml']+' cannot be opened.'
    
    if 'TF' in xmlfile.results:
        if conf['tf_chA'] not in xmlfile.results['TF']:
            return 1, conf['tf_chA']+' cannot be found in '+conf['tf_xml']
        elif conf['tf_chB'] not in xmlfile.results['TF'][conf['tf_chA']]['channelB']:
            return 1, conf['tf_chB']+' cannot be found in '+conf['tf_xml']
    elif 'CSD' in xmlfile.results:
        if conf['tf_chA'] not in xmlfile.results['CSD']:
            return 1, conf['tf_chA']+' cannot be found in '+conf['tf_xml']
        elif conf['tf_chB'] not in xmlfile.results['CSD'][conf['tf_chA']]['channelB']:
            return 1, conf['tf_chB']+' cannot be found in '+conf['tf_xml']
    else:
        return 1, 'Check if the xml is TF data.'

    tfxfer = xmlfile.xfer(conf['tf_chB'],conf['tf_chA'])
    xml_f = tfxfer.FHz
    xml_tf = abs(tfxfer.xfer)

    # interpolate to multiply
    if max(xml_f) < max(freq):
        for f in freq:
            if f > max(xml_f):
                xml_f=np.append(xml_f,f)
                xml_tf = np.append(xml_tf,0.)
                break
        xml_f=np.append(xml_f,max(freq))
        xml_tf = np.append(xml_tf,0.)
    if min(xml_f) > min(freq):
        for f in reversed(freq):
            if f < min(xml_f):
                xml_f = np.append(f,xml_f)
                xml_tf = np.append(0.,xml_tf)
                break
        xml_f=np.append(min(freq),xml_f)
        xml_tf = np.append(0.,xml_tf)
    tf_interp = interpolate.interp1d(xml_f,xml_tf)
    tf = tf_interp(freq)
    
    return 0, tf

def loadtxttf(conf,freq):
    status=0
    datafile = conf['tf_txt']
    with open(datafile,'r') as fd:
        line1 = fd.read().split('\n')[0]
    try:
        if ',' in line1:
            data = np.loadtxt(datafile,delimiter=',')
        elif ' ' in line1:
            data = np.loadtxt(datafile)
    except:
        status=1
        msg = datafile+' cannot be opened.'
        return status, msg
    
    if np.shape(data)[1]==2:
        txt_f = data[:,0]
        txt_tf = data[:,1]
    elif np.shape(data)[0]==2:
        txt_f = data[0]
        txt_tf = data[1]
    else:
        status=1
        msg = 'data in '+datafile+' is not proper.'
        return status, msg    
    
    if max(txt_f) < max(freq):
        for f in freq:
            if f > max(txt_f):
                txt_f=np.append(txt_f,f)
                txt_tf = np.append(txt_tf,0.)
                break
        txt_f=np.append(txt_f,max(freq))
        txt_tf = np.append(txt_tf,0.)
    if min(txt_f) > min(freq):
        for f in reversed(freq):
            if f < min(txt_f):
                txt_f = np.append(f,txt_f)
                txt_tf = np.append(0.,txt_tf)
                break
        txt_f=np.append(min(freq),txt_f)
        txt_tf = np.append(0.,txt_tf)
    tf_interp = interpolate.interp1d(txt_f,txt_tf)
    tf = tf_interp(freq)
    
    return 0, tf

def loadzpktf(conf,freq):
    zz,pp,kk = readzpk(conf['zz'],conf['pp'],conf['kk'])
    tf_zpk = sig.ZerosPolesGain(zz,pp,kk)
    freq, mag, phase = sig.bode(tf_zpk, freq)
    tf = 10.0**(mag/20.0)
    return 0, tf

def plot_singleTheoN(conf,freq_tot,total):
    status=0
    if conf['equation'] =='None':
        datafile = conf['datafile']
        with open(datafile,'r') as fd:
            line1 = fd.read().split('\n')[0]
        try:
            if ',' in line1:
                data = np.loadtxt(datafile,delimiter=',')
            elif ' ' in line1:
                data = np.loadtxt(datafile)
        except:
            status=1
            msg = datafile+' cannot be opened.'
            return status, msg
        
        if np.shape(data)[1]==2:
            freq = data[:,0]
            line = data[:,1]
        elif np.shape(data)[0]==2:
            freq = data[0]
            line = data[1]
        else:
            status=1
            msg = 'data in '+datafile+' is not proper.'
            return status, msg
        
        tf = np.zeros(len(freq))+1.
        if conf['tf_xml']!='None':
        ## add tf_xml
            status, tfxml = loadxmltf(conf, freq)
            if status ==1:
                return status, tfxml
            else:
                tf = tf*tfxml
        if conf['zz'] !='None':
            ## add zpk
            status,tfzpk = loadzpktf(conf,freq)
            tf = tf*tfzpk
            
        if 'tf_txt' in conf:
            if conf['tf_txt']=='':
                tf = tf
            elif conf['tf_txt']=='None':
                tf = tf
            else:
                status, tftxt = loadtxttf(conf,freq)
                if status ==1:
                    return status, tftxt
                else:
                    tf = tf*tftxt
        
        line = line*tf

        ## calc total noise
        #freq = np.ndarray(freq)
        #line = np.ndarray(line)
        
        # interpolate to multiply
        if max(freq) < max(freq_tot):
            for f in freq_tot:
                if f > max(freq):
                    freq = np.append(freq,f)
                    line = np.append(line,0)
                    break
            freq = np.append(freq,max(freq_tot))
            line = np.append(line,0.)
        if min(freq) > min(freq_tot):
            for f in reversed(freq_tot):
                if f < min(freq):
                    freq = np.append(f,freq)
                    line = np.append(0.,line)
                    break
            freq=np.append(min(freq_tot),freq)
            line=np.append(0.,line)
        line_interp = interpolate.interp1d(freq,line)
        total = np.sqrt(total*total+line_interp(freq_tot)*line_interp(freq_tot))
    
    elif conf['datafile'] == 'None':
        freq = freq_tot
        line = eval(conf['equation'])
        
        tf = np.zeros(len(freq))+1.
        if conf['tf_xml']!='None':
        ## add tf_xml
            status, tfxml = loadxmltf(conf, freq)
            if status ==1:
                return status, tfxml
            else:
                tf = tf*tfxml
        if conf['zz'] !='None':
            ## add zpk
            status,tfzpk = loadzpktf(conf,freq)
            tf = tf*tfzpk
        
        if 'tf_txt' in conf:
            if conf['tf_txt']=='':
                tf = tf
            elif conf['tf_txt']=='None':
                tf = tf
            else:
                status, tftxt = loadtxttf(conf,freq)
                if status ==1:
                    return status, tftxt
                else:
                    tf = tf*tftxt
                    
        line = line*tf
        
        ## calc total noise
        total = np.sqrt(total*total+line*line)
        
    return status, total, freq, line


def plot_singleRTN(conf,start,end,fres,freq_tot,total):
    status = 0
    #print(start, end)
    ch = conf['chan']

    gps_beg = int(to_gps( start ))
    gps_end = int(to_gps( end ))
    gps_beg_head = int(gps_beg/100000)
    gps_end_head = int(gps_end/100000)
    if gps_beg_head == gps_end_head:
        cache_file="/home/devel/cache/Cache_GPS/%s.cache" % gps_beg_head
    else:
        # merge two cache file
        cache1="/home/devel/cache/Cache_GPS/%s.cache" % gps_beg_headelse
        cache2="/home/devel/cache/Cache_GPS/%s.cache" % gps_end_head
        cache_file="/var/www/html/past_data_viewer/data/%s_%s.cache" % (gps_beg, gps_end)

        with open(cache_file, 'w') as outfile:
            for i in [cache1, cache2]:
                with open(i) as infile:
                    outfile.write(infile.read())

    try:
        data = TimeSeries.read(cache_file, ch, start=gps_beg, end=gps_end, nproc=4)
        #data = TimeSeries.get(ch, start, end, host='k1nds2', port=8088)
    except:
        return 1, ch+' cannot be loaded.'
    spe = data.asd(1./fres,1./fres/2.)
    freq = spe.frequencies.to_value()
    ch_spe = spe.value
    tf = np.zeros(len(freq))+1.
    #print('size of total: '+str(len(total)))
    #print('size of freq: '+str(len(freq)))
    if conf['tf_xml']!='None':
        ## add tf_xml
        status, tfxml = loadxmltf(conf, freq)
        if status ==1:
            return status, tfxml
        else:
            tf = tf*tfxml

    if conf['zz'] !='None':
        ## add zpk
        status,tfzpk = loadzpktf(conf,freq)
        tf = tf*tfzpk
        
    if 'tf_txt' in conf:
        if conf['tf_txt']=='':
            tf = tf
        elif conf['tf_txt']=='None':
            tf = tf
        else:
            status, tftxt = loadtxttf(conf,freq)
            if status ==1:
                return status, tftxt
            else:
                tf = tf*tftxt

    spe = ch_spe*tf

    # interpolate for total
    if max(freq) < max(freq_tot):
        freq=np.append(freq,max(freq_tot))
        spe =np.append(spe,0.)
    if min(freq) > min(freq_tot):
        freq=np.append(min(freq_tot),freq)
        spe =np.append(0.,spe)
    spe_interp = interpolate.interp1d(freq,spe)
    total = np.sqrt(total*total+spe_interp(freq_tot)*spe_interp(freq_tot))
    
    return status, total, freq, spe
