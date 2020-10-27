from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt
import os
from .forms import UploadFileForm, addTheoform, CSVUploadFileForm
from DjangoApp.settings import BASE_DIR ## TO BE FIXED
import datetime
from lib.NBplotter import *
import numpy as np

def index(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    if 'figure' in request.session:
        figval=request.session['figure']
        figurename = 'result'+str(figval)+'.png'
        context = {
                   'loadform':loadform,
                   'TheoN':TheoN,
                   'RTN':RTN,
                   'figurename':figurename,
                   'PlotConf':PlotConf,
                   'Category':Category
                   }
    else:
        context = {
                   'loadform':loadform,
                   'TheoN':TheoN,
                   'RTN':RTN,
                   'PlotConf':PlotConf,
                   'Category':Category
                   }
    return render(request, 'NoiseBudgetter/index.html',context)

def New(request):
    request.session.clear()
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')  
    Category = request.session.get('Category')  
    context = {
               'loadform':loadform,
               'TheoN':TheoN,
               'RTN':RTN,
               'Category':Category
               }
    return render(request, 'NoiseBudgetter/index.html',context)

def loadfile(request):
    loadform = CSVUploadFileForm(request.POST, request.FILES)
    TheoN = dict()
    RTN = dict()
    MSN = dict()
    PlotConf = dict()
    Category = dict()
    if loadform.is_valid():
        handle_uploaded_file(request.FILES['file'],'tmp.csv')
        filename = request.FILES['file'].name
        data = open('media/NB/tmp.csv')
        csv_file = csv.reader(data)
        header = next(csv_file)
        if header[0] != 'save date':
            TheoN, RTN, MSN, PlotConf, Category = loadcsvfiledata_v0(TheoN,RTN,MSN,PlotConf,Category)
        else:
            savedt = datetime.datetime.strptime(header[1], "%Y/%m/%d %H:%M:%S")
            if savedt > datetime.datetime(2020,3,12,7,0,0):
                TheoN, RTN, MSN, PlotConf, Category = loadcsvfiledata_v1(TheoN,RTN,MSN,PlotConf,Category)
        
        if TheoN==dict() and RTN==dict() and MSN==dict() and Category==dict():
            context = {'errormsg':'No data to properly loaded from '+filename,
                       'loadform':loadform,
                       'TheoN':TheoN,
                       'RTN':RTN,
                       'Category':Category
                       }
        else:
            request.session['TheoN']=TheoN
            request.session['RTN']=RTN
            request.session['MSN']=MSN
            request.session['PlotConf']=PlotConf
            request.session['Category']=Category
            context = {'errormsg':filename+' is loaded.',
                       'loadform':loadform,
                       'TheoN':TheoN,
                       'RTN':RTN,
                       'PlotConf':PlotConf,
                       'Category':Category
                       }
        
    else:
        error = 'file is not valid'
        context = {'errormsg':error,
                   'loadform':loadform,
                   'TheoN':TheoN,
                   'RTN':RTN,
                   'Category':Category
                   }
    
    
    return render(request, 'NoiseBudgetter/index.html',context)


def savefile(request):
    response = HttpResponse(content_type='text/csv')
    now = datetime.datetime.now()
    csvfilename = "NPconf_"+now.strftime('%Y%m%d_%H%M')+".csv"
    response['Content-Disposition'] = 'attachment; filename='+csvfilename
    writer = csv.writer(response)
    
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    MSN = request.session.get('MSN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    
    now = datetime.datetime.now()
    row = ['save date',now.strftime("%Y/%m/%d %H:%M:%S")]
    writer.writerow(row)
    if TheoN is not None:
        for name, conf in TheoN.items():
            if 'tf_txt' not in conf:
                conf['tf_txt'] = None
            row = [0, name, conf['equation'],conf['datafile'], conf['tf_xml'], conf['tf_chA'], conf['tf_chB'],conf['tf_txt'],conf['zz'],conf['pp'],conf['kk'],conf['notes']]
            writer.writerow(row)
    if RTN is not None:
        for name, conf in RTN.items():
            if 'tf_txt' not in conf:
                conf['tf_txt'] = None
            row = [1, name, conf['chan'], conf['tf_xml'], conf['tf_chA'], conf['tf_chB'],conf['tf_txt'],conf['zz'],conf['pp'],conf['kk'],conf['notes']]
            writer.writerow(row)
#    if MSN is not None:
#        for name, conf in MSN.items():
#            row = [2, name, conf['s_xml'],conf['s_ch'], conf['tf_xml'], conf['tf_chA'], conf['tf_chB'],conf['zpk']]
#            writer.writerow(row)
            
    if Category is not None:
        for name, oneCateg in Category.items():
            for subname, conf in oneCateg.items():
                if 'tf_txt' not in conf:
                    conf['tf_txt'] = None
                if 'equation' in conf:
                    row = [10, name, subname, conf['equation'],conf['datafile'], conf['tf_xml'], conf['tf_chA'], conf['tf_chB'],conf['tf_txt'],conf['zz'],conf['pp'],conf['kk'],conf['notes']]
                if 'chan' in conf:
                    row = [11, name, subname, conf['chan'], conf['tf_xml'], conf['tf_chA'], conf['tf_chB'],conf['tf_txt'],conf['zz'],conf['pp'],conf['kk'],conf['notes']]
                writer.writerow(row)
    
    if PlotConf is not None:
        row = [99,PlotConf['start'],PlotConf['end'],PlotConf['fres'],PlotConf['fmin'],PlotConf['fmax'],PlotConf['ymin'],PlotConf['ymax']]
        writer.writerow(row)
    
    return response

def plot(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    
    start = request.POST['start']
    end = request.POST['end']
    fres = float(request.POST['freq'])
    fmin = float(request.POST['fmin'])
    fmax = float(request.POST['fmax'])
    
    if 'figure' in request.session:
        figval=request.session['figure']
        fig = plt.figure(figval,figsize=(10,6))
        plt.clf()
    else:
        fig = plt.figure(figsize=(10,6))
        figval=fig.number
        request.session['figure'] = figval
    
    # CHANGE FOR LOCAL
    status,freq_tot = plot_DARM(start,end,fres, figval)
    #status,freq_tot = plot_DARM_local(start,end,fres, figval)
    if status==1: # error in obtaining the data
        if 'figure' in request.session:
            figurename = 'result'+str(figval)+'.png'
        else:
            figurename = 'test.jpg'
        context={'errormsg':freq_tot,
                 'loadform':loadform,
                 'TheoN':TheoN,
                 'RTN':RTN,
                 'figurename':figurename,
                 'PlotConf':PlotConf,
                 'Category':Category
                 }
        return render(request, 'NoiseBudgetter/index.html',context)
    
    total = np.zeros(len(freq_tot))
    status = 0
    ans = [status,total]
    
    if (TheoN != None) and (TheoN != dict()):
        ans =plot_TheoN(TheoN, fmin, fmax, freq_tot, total, figval)
        status = ans[0]
    if status == 0:
        if (RTN != None) and (RTN != dict()):
            total = ans[1]
            ans=plot_RTN(RTN,start,end,fres,freq_tot,total,figval)
            status = ans[0]
    if status == 0:
        if (Category != None) and (Category != dict()):
            total = ans[1]
            ans = plot_Category(Category,start,end,fres,freq_tot,total,figval)
            status = ans[0]
            
    if status == 0:
        total = ans[1]
        #print(ans[1])
        plt.loglog(freq_tot,total,'k--',linewidth=2.0,label='total')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
        plt.subplots_adjust(right=0.7)
        plt.xlim([fmin,fmax])
        plt.title('NB from '+start+' to '+end)
        
        ymin='None'
        ymax='None'
        msg = 'plotted'
        if (request.POST['ymin']!='') and (request.POST['ymax']!=''):
            ymin = float(request.POST['ymin'])
            ymax = float(request.POST['ymax'])
            plt.ylim([ymin,ymax])
        elif (request.POST['ymin']!='') or (request.POST['ymax']!=''):
            msg = 'Please specify y-axis range for both min and max.'
    
        figurename = 'result'+str(figval)+'.png'
        fig.savefig('NoiseBudgetter/static/'+figurename)
        
        PlotConf = {'start':start,'end':end,'fres':request.POST['freq'],'fmin':request.POST['fmin'],'fmax':request.POST['fmax'],'ymin':request.POST['ymin'],'ymax':request.POST['ymax']}
        request.session['PlotConf']=PlotConf
        
        context={'errormsg':msg,
                 'loadform':loadform,
                 'TheoN':TheoN,
                 'RTN':RTN,
                 'figurename':figurename,
                 'PlotConf':PlotConf,
                 'Category':Category
                 }
        
    else:
        figurename = 'result'+str(figval)+'.png'
        context={'errormsg':ans[1],
                 'loadform':loadform,
                 'TheoN':TheoN,
                 'RTN':RTN,
                 'figurename':figurename,
                 'PlotConf':PlotConf,
                 'Category':Category
                 }
    return render(request, 'NoiseBudgetter/index.html',context)
    
def plot_Subplot(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    if 'figure' in request.session:
        figval=request.session['figure']
        figurename = 'result'+str(figval)+'.png'
    else:
        figurename = 'test.jpg'
    
    start = request.POST['start']
    end = request.POST['end']
    fres = float(request.POST['freq'])
    fmin = float(request.POST['fmin'])
    fmax = float(request.POST['fmax'])
    
    if 'figure' in request.session:
        figval=request.session['figure']
        fig = plt.figure(figval+100,figsize=(8,5))
        plt.clf()
    else:
        fig = plt.figure(100,figsize=(10,6))
        figval = 0
    
    # CHANGE FOR LOCAL
    status,freq_tot = plot_DARM(start,end,fres, figval=figval+100)
    #status,freq_tot = plot_DARM_local(start,end,fres, figval)
    if status==1: # error in obtaining the data
        if 'figure' in request.session:
            figurename = 'result'+str(figval)+'.png'
        else:
            figurename = 'test.jpg'
        context={'errormsg':freq_tot,
                 'loadform':loadform,
                 'TheoN':TheoN,
                 'RTN':RTN,
                 'figurename':figurename,
                 'PlotConf':PlotConf,
                 'Category':Category
                 }
        return render(request, 'NoiseBudgetter/index.html',context)
    
    name = request.POST['categname']
    oneCategory = Category[name]
    
    ans = plot_oneCategonly(name,oneCategory,start,end,fres,freq_tot,figval=figval+100)
    status=ans[0]
    
    if status==0:
        ymin='None'
        ymax='None'
        msg = 'plotted'
        cattotal=ans[2]
        if (request.POST['ymin']!='') and (request.POST['ymax']!=''):
            ymin = float(request.POST['ymin'])
            ymax = float(request.POST['ymax'])
            plt.ylim([ymin,ymax])
        elif (request.POST['ymin']!='') or (request.POST['ymax']!=''):
            msg = 'Please specify y-axis range for both min and max.'
            
        plt.xlim([fmin,fmax])
        subfigurename = 'subplot'+str(figval)+'.png'
        fig.savefig('NoiseBudgetter/static/'+subfigurename)
        
        context={'errormsg':msg,
                 'loadform':loadform,
                 'TheoN':TheoN,
                 'RTN':RTN,
                 'figurename':figurename,
                 'PlotConf':PlotConf,
                 'Category':Category,
                 'Subplot':{'name':name,'figure':subfigurename}
                 }
        
    else:
        figurename = 'result'+str(figval)+'.png'
        context={'errormsg':ans[1],
                 'loadform':loadform,
                 'TheoN':TheoN,
                 'RTN':RTN,
                 'figurename':figurename,
                 'PlotConf':PlotConf,
                 'Category':Category
                 }
    return render(request, 'NoiseBudgetter/index.html',context)

def addTheoNoise(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    if 'figure' in request.session:
        figval=request.session['figure']
        figurename = 'result'+str(figval)+'.png'
    else:
        figurename = 'test.jpg'
    
    
    Nname = request.POST['name']
    Notes = request.POST['notes']
    
    conf = request.POST['Theoconf']
    if conf == 'eq':
        equation = request.POST['equation']
        datafile = 'None'
        try:
            freq = np.logspace(1,4,0.1)
            eqdata = eval(equation)
        except:
            context={'errormsg':'equation is not proper for python.',
                     'loadform':loadform,
                     'TheoN':TheoN,
                     'RTN':RTN,
                     'figurename':figurename,
                     'PlotConf':PlotConf,
                     'Category':Category
                     }
            return render(request, 'NoiseBudgetter/index.html',context)
    
    if conf == 'data':
        datafile = request.POST['datafile']
        equation = 'None'    
    
    
    if 'xmlconf' in request.POST:
        tf_xml = request.POST['tf_xml']
        tf_chA = request.POST['tf_chA']
        tf_chB = request.POST['tf_chB']
    else:
        tf_xml = 'None'
        tf_chA = 'None'
        tf_chB = 'None'
    
    if 'txtconf' in request.POST:
        tf_txt = request.POST['tf_txt']
    else:
        tf_txt = 'None'
    
    if 'zpkconf' in request.POST:
        tf_zz = request.POST['tf_zz']
        tf_pp = request.POST['tf_pp']
        tf_kk = request.POST['tf_kk']
        if tf_zz == None:
            tf_zz = ''
        if tf_pp == None:
            tf_pp = ''
        if readzpk(tf_zz,tf_pp,tf_kk) is False:
            context={'errormsg':tf_zz+tf_pp+tf_kk,
                     'loadform':loadform,
                     'TheoN':TheoN,
                     'RTN':RTN,
                     'figurename':figurename,
                     'PlotConf':PlotConf,
                     'Category':Category
                     }
            return render(request, 'NoiseBudgetter/index.html',context)
    else:
        tf_zz = 'None'
        tf_pp = 'None'
        tf_kk = 'None'
    
    if TheoN is None:
        TheoN = dict()
    newdict = {Nname:{'equation':equation,'datafile':datafile,'tf_xml':tf_xml,'tf_chA':tf_chA,'tf_chB':tf_chB,'tf_txt':tf_txt,'zz':tf_zz, 'pp':tf_pp,'kk':tf_kk,'notes':Notes}}
    TheoN.update(newdict)
    
    request.session['TheoN']=TheoN
    
    context = {'errormsg':'Theoretical NS added',
               'loadform':loadform,
               'TheoN':TheoN,
               'RTN':RTN,
               'figurename':figurename,
               'PlotConf':PlotConf,
               'Category':Category
               }
    return render(request, 'NoiseBudgetter/index.html',context)


def addRTNoise(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    if 'figure' in request.session:
        figval=request.session['figure']
        figurename = 'result'+str(figval)+'.png'
    else:
        figurename = 'test.jpg'
    
    if RTN == None:
        RTN = dict()
        
    Notes = request.POST['notes']

    name = request.POST['name']
    chan = request.POST['NSchan']
#    tfmethod = []
#    tfmethod.append(request.POST['xmlconf'])
#    tfmethod.append(request.POST['zpkconf'])
    
    if 'xmlconf' in request.POST:
        tf_xml = request.POST['tf_xml']
        tf_chA = request.POST['tf_chA']
        tf_chB = request.POST['tf_chB']
    else:
        tf_xml = 'None'
        tf_chA = 'None'
        tf_chB = 'None'
    
    if 'txtconf' in request.POST:
        tf_txt = request.POST['tf_txt']
    else:
        tf_txt = 'None'
        
    if 'zpkconf' in request.POST:
        tf_zz = request.POST['tf_zz']
        tf_pp = request.POST['tf_pp']
        tf_kk = request.POST['tf_kk']
        if tf_zz == None:
            tf_zz = ''
        if tf_pp == None:
            tf_pp = ''
        if readzpk(tf_zz,tf_pp,tf_kk) is False:
            context={'errormsg':'error in converting the zpk',
                     'loadform':loadform,
                     'TheoN':TheoN,
                     'RTN':RTN,
                     'figurename':figurename,
                     'PlotConf':PlotConf,
                     'Category':Category
                     }
            return render(request, 'NoiseBudgetter/index.html',context)
    else:
        tf_zz = 'None'
        tf_pp = 'None'
        tf_kk = 'None'
        
    RTN.update({name:{'chan':chan,'tf_xml':tf_xml,'tf_chA':tf_chA,'tf_chB':tf_chB,'tf_txt':tf_txt,'zz':tf_zz, 'pp':tf_pp,'kk':tf_kk,'notes':Notes}})    
    
    request.session['RTN']=RTN
    
    context = {'errormsg': 'RT noise source added.',
               'loadform':loadform,
               'TheoN':TheoN,
               'RTN':RTN,
               'figurename':figurename,
               'PlotConf':PlotConf,
               'Category':Category
               }
    
    return render(request, 'NoiseBudgetter/index.html',context)

def OnDelete(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    MSN = request.session.get('MSN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    if 'figure' in request.session:
        figval=request.session['figure']
        figurename = 'result'+str(figval)+'.png'
    else:
        figurename = 'test.png'
    
    if RTN == None:
        RTN = dict()
        
    if TheoN == None:
        TheoN = dict()
    
    name = request.POST['delete']
    if name in TheoN.keys():
        del TheoN[name]
    elif name in RTN.keys():
        del RTN[name]
    
    
    request.session['TheoN']=TheoN
    request.session['RTN']=RTN
    request.session['MSN']=MSN
    
    context = {'errormsg':'Noise source: '+name+' is deleted',
               'loadform':loadform,
               'TheoN':TheoN,
               'RTN':RTN,
               'figurename':figurename,
               'PlotConf':PlotConf,
               'Category':Category
               }
    return render(request, 'NoiseBudgetter/index.html',context)

def Categorize(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    if 'figure' in request.session:
        figval=request.session['figure']
        figurename = 'result'+str(figval)+'.png'
    else:
        figurename = 'test.jpg'
        
    if Category == None:
        Category = dict()
    if RTN == None:
        RTN = dict()
    if TheoN == None:
        TheoN = dict()
        
    title = request.POST['name']
    values = request.POST.getlist('choose')
    
    categlist = dict()
    
    for TheoNname in TheoN:
        if TheoNname in values:
            categlist.update({TheoNname:TheoN[TheoNname]})
        
    for RTNname in RTN:
        if RTNname in values:
            categlist.update({RTNname:RTN[RTNname]})
            
    for categname1 in values:
        TheoN.pop(categname1,'no key')
        
    for categname2 in values:
        RTN.pop(categname2,'no key')
    
    Category.update({title:categlist})
    
    request.session['TheoN']=TheoN
    request.session['RTN']=RTN
    request.session['Category']=Category
    

    context = {'errormsg': values,
           'loadform':loadform,
           'TheoN':TheoN,
           'RTN':RTN,
           'figurename':figurename,
           'PlotConf':PlotConf,
           'Category':Category
           }
    return render(request, 'NoiseBudgetter/index.html',context)

def UnCategorize(request):
    loadform = CSVUploadFileForm()
    TheoN = request.session.get('TheoN')
    RTN = request.session.get('RTN')
    PlotConf = request.session.get('PlotConf')
    Category = request.session.get('Category')
    if 'figure' in request.session:
        figval=request.session['figure']
        figurename = 'result'+str(figval)+'.png'
    else:
        figurename = 'test.jpg'
        
    if Category == None:
        Category = dict()
    if RTN == None:
        RTN = dict()
    if TheoN == None:
        TheoN = dict()
        
    name = request.POST['UnCategorize']
    
    unCateg = Category[name]
    
    for categkeys,config in unCateg.items():
        if 'equation' in config:
            TheoN.update({categkeys:config})
        elif 'chan' in config:
            RTN.update({categkeys:config})
    
    Category.pop(name)
    
    request.session['TheoN']=TheoN
    request.session['RTN']=RTN
    request.session['Category']=Category
    

    context = {'errormsg': 'un-categorized',
           'loadform':loadform,
           'TheoN':TheoN,
           'RTN':RTN,
           'figurename':figurename,
           'PlotConf':PlotConf,
           'Category':Category
           }
    return render(request, 'NoiseBudgetter/index.html',context)

def handle_uploaded_file(f,filename):
    destination = open(os.path.join('media/NB/',filename), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)

def manual(request):
    return HttpResponseRedirect("http://gwwiki.icrr.u-tokyo.ac.jp/JGWwiki/KAGRA/Commissioning/NoiseBudgetter")

def loadcsvfiledata_v0(TheoN,RTN,MSN,PlotConf,Category):
    data = open('media/NB/tmp.csv')
    csv_file = csv.reader(data)
    for line in csv_file:
        if line[0]=='0':
            if len(line)==4:
                TheoN.update({line[1]:{'equation':line[2],'datafile':line[3],'tf_xml':'None','tf_chA':'None','tf_chB':'None','zz':'None','pp':'None','kk':'None','notes':''}})
            elif len(line)==10:
                TheoN.update({line[1]:{'equation':line[2],'datafile':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'zz':line[7],'pp':line[8],'kk':line[9],'notes':''}})
            elif len(line)==11:
                TheoN.update({line[1]:{'equation':line[2],'datafile':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'zz':line[7],'pp':line[8],'kk':line[9],'notes':line[10]}})
        elif line[0]=='1':
            line = np.append(line,'')
            RTN.update({line[1]:{'chan':line[2],'tf_xml':line[3],'tf_chA':line[4],'tf_chB':line[5],'zz':line[6],'pp':line[7],'kk':line[8],'notes':line[9]}})
        elif line[0]=='2':
            line = np.append(line,'')
            MSN.update({line[1]:{'s_xml':line[2],'s_ch':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'zpk':line[7],'notes':line[8]}})
        elif line[0]=='10':
            line = np.append(line,'')
            name = line[1]
            if name in Category:
                Category[name].update({line[2]:{'equation':line[3],'datafile':line[4],'tf_xml':line[5],'tf_chA':line[6],'tf_chB':line[7],'zz':line[8],'pp':line[9],'kk':line[10],'notes':line[11]}})
            else:
                Category.update({name:{line[2]:{'equation':line[3],'datafile':line[4],'tf_xml':line[5],'tf_chA':line[6],'tf_chB':line[7],'zz':line[8],'pp':line[9],'kk':line[10],'notes':line[11]}}})
        elif line[0]=='11':
            line = np.append(line,'')
            name = line[1]
            if name in Category:
                Category[name].update({line[2]:{'chan':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'zz':line[7],'pp':line[8],'kk':line[9],'notes':line[10]}})
            else:
                Category.update({name:{line[2]:{'chan':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'zz':line[7],'pp':line[8],'kk':line[9],'notes':line[10]}}})
        elif line[0]=='99':
            PlotConf.update({'start':line[1],'end':line[2],'fres':line[3],'fmin':line[4],'fmax':line[5],'ymin':line[6],'ymax':line[7]})
    return TheoN, RTN, MSN, PlotConf, Category

def loadcsvfiledata_v1(TheoN,RTN,MSN,PlotConf,Category):
    data = open('media/NB/tmp.csv')
    csv_file = csv.reader(data)
    for line in csv_file:
        if line[0]=='0':
            TheoN.update({line[1]:{'equation':line[2],'datafile':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'tf_txt':line[7],'zz':line[8],'pp':line[9],'kk':line[10],'notes':line[11]}})
        elif line[0]=='1':
            RTN.update({line[1]:{'chan':line[2],'tf_xml':line[3],'tf_chA':line[4],'tf_chB':line[5],'tf_txt':line[6],'zz':line[7],'pp':line[8],'kk':line[9],'notes':line[10]}})
        #elif line[0]=='2':
        #    MSN.update({line[1]:{'s_xml':line[2],'s_ch':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'tf_txt':line[7],'zpk':line[7],'notes':line[8]}})
        elif line[0]=='10':
            name = line[1]
            if name in Category:
                Category[name].update({line[2]:{'equation':line[3],'datafile':line[4],'tf_xml':line[5],'tf_chA':line[6],'tf_chB':line[7],'tf_txt':line[8],'zz':line[9],'pp':line[10],'kk':line[11],'notes':line[12]}})
            else:
                Category.update({name:{line[2]:{'equation':line[3],'datafile':line[4],'tf_xml':line[5],'tf_chA':line[6],'tf_chB':line[7],'tf_txt':line[8],'zz':line[9],'pp':line[10],'kk':line[11],'notes':line[12]}}})
        elif line[0]=='11':
            name = line[1]
            if name in Category:
                Category[name].update({line[2]:{'chan':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'tf_txt':line[7],'zz':line[8],'pp':line[9],'kk':line[10],'notes':line[11]}})
            else:
                Category.update({name:{line[2]:{'chan':line[3],'tf_xml':line[4],'tf_chA':line[5],'tf_chB':line[6],'tf_txt':line[7],'zz':line[8],'pp':line[9],'kk':line[10],'notes':line[11]}}})
        elif line[0]=='99':
            PlotConf.update({'start':line[1],'end':line[2],'fres':line[3],'fmin':line[4],'fmax':line[5],'ymin':line[6],'ymax':line[7]})
    return TheoN, RTN, MSN, PlotConf, Category
    
