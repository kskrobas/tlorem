#!/usr/bin/python3

from tkinter import ttk, Tk, Frame,Menu
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import filedialog as fd

import labelEdit as le
import dataProcessing as dpr
import windowPlot as wp
import windowPlotResults as wpr
import windowPlotWavelets as wpw


import os
import numpy as np
import regex as re
import pywt
from skued import baseline_dwt


import findFitPeaks as ffp
import initsetRW as ini
#import pywt
#pywt.wavelist()



#------------------------------------------------------------------------------
# docs: http://tcl.tk/man/tcl8.5/TkCmd/bind.htm#M2
#
class MainFrame(tk.Frame):
    inputFile=""
    outputFile=""
    __currRow__=0
    __defFont__=""
    __titFont__=""
    __frwidth__=700
    
    data2D=None
    dataInfo={}
    flabels={}
    
    TEST=False
    
    __inparams__={}
    
    def __getRow__(self):
        return self.__currRow__
    def __incRow__(self):
        self.__currRow__+=1        
#------------------------------------------------------------------------------  
    

    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        appDir=ini.getValue('default','apath') 
        
        self.InputFileName=tk.StringVar()    
        self.InputFileName.set(ini.getValue('default','inpath'))   
        fileName=self.InputFileName.get()         

        self.DataReductType=tk.StringVar()        
        self.DataReductType.set(ini.getValue('data.reduction','name'))     

        self.DataFromTo=tk.StringVar()
        if self.TEST:
            self.DataFromTo.set(":")
        else:
            self.DataFromTo.set(ini.getValue('data.reduction','fromto'))
            
            
        print('--- start running ---')
                                                                         
        self.iniDir= appDir if not fileName else fileName.rsplit('/',1)[0]
                                
        self.initUI()                        
                             
        if fileName:
            self.readFile()
                
        self.font=self.__titFont__   
        self.bind('<Destroy>',self.Destroy)

                              
#------------------------------------------------------------------------------    

    def __del__(self):
        print('close')            
        
    def Destroy(self,*arg):
                
        ini.setValue("calibration.pixe","onoff",str(self.DataOnOff.get()))
        ini.setValue("calibration.pixe","A",self.Data_Aprm.get())
        ini.setValue("calibration.pixe","B", str(self.Data_Bprm.get()))
        ini.setValue("calibration.pixe","C", str(self.Data_Cprm.get()))
        #ini.setValue("calibration.pixe","ula",  str(self.DataCalibUla.get()))
        #ini.setValue("calibration.pixe","uma",  str(self.DataCalibUma.get()))
        
        ini.setValue("data.reduction", "name",self.DataReductType.get())
        ini.setValue("data.reduction","fromto",self.DataFromTo.get())
        
        ini.setValue("data.filtering","name",self.FilterType.get())
        ini.setValue("data.filtering","rank",str(self.FilterRank.get()))
        ini.setValue("data.filtering","size",str(self.FilterSize.get()))
        
        ini.setValue("wavelet.prms","family",self.WletFamily.get())
        ini.setValue("wavelet.prms","name",self.WletType.get())
        ini.setValue("wavelet.prms","levels",str(self.WletLevels.get()))
        
        print('destroy')
                  
      
    def initUI(self):          
        self.__defFont__=tkFont.Font(family="FreeMono",size=12)
        self.__titFont__=tkFont.Font(family="Helvetica",size=14)        
        
        self.buttons={}
        self.comboBox={}
        self.calibEntries={}
        
        self.initMenu()        
        self.initInputFile()
        self.initFilterData()
        self.initWaveletData()
        
        
        #self.imageRun=tk.PhotoImage(file='run.png')
        bcalc=tk.Button(self,text='RUN',command=self.dataWaveletProcessing,
                        background='gold',
                        state="disabled",
                        
                        font=self.__defFont__,width=64,height=2)
        bcalc.pack()
        
        self.buttons['bcalc']=bcalc
        
        bcalcTmp=tk.Button(self,text='find & fit',command=self.showFFWindow,
                        background='gold',
                        
                        font=self.__defFont__,width=64,height=2)
        bcalcTmp.pack()
                       
#------------------------------------------------------------------------------        

    def showFFWindow(self):
        child=ffp.findFitWindow(self)         

    def fromToEntryChanged(self,value):
        self.updateWavMaxLevels()
                         
    def openChild(self):
        child=wp.plotWindow(self)
        
#------------------------------------------------------------------------------

    def OnOffCalParams(self):        
        state= 'normal' if self.DataOnOff.get() else 'disabled'
        for k,v in self.calibEntries.items():  v['state']=state
#------------------------------------------------------------------------------

    def calibrate(self):
        ''''
        dose=float(self.DataCalibDose.get())
        Y2D=10/dose
        U_L_alfa = 13.5970 # keV
        U_M_alfa = 3.1703  # keV
        ul_in=float(self.DataCalibUla.get())
        print(self.DataCalibUma.get())
        um_in=float(self.DataCalibUma.get())
        aE = (U_L_alfa-U_M_alfa)/(ul_in-um_in)
        bE = U_L_alfa - aE * ul_in
        '''
        aE=float(self.Data_Aprm.get())
        bE=float(self.Data_Bprm.get())
        cE=float(self.Data_Cprm.get())

        pvec=np.array([aE,bE])
        
        self.data2D[:,0]=np.polyval(pvec,x=self.data2D[:,0])
        self.data2D[:,1]/=cE
#------------------------------------------------------------------------------        

    def readFile(self):
        self.data2D=dpr.readFile(self.InputFileName.get())        
        if self.data2D is None:
            print('empty inpout data')
            return
        
        if self.DataOnOff.get():
            self.calibrate()
                        
        self.dataInfo={}
        #self.DataFromTo.set("0:"+str(self.data2D.shape[0]-1))                
        self.buttons['breplot']['state']=tk.ACTIVE
        self.buttons['bcalc']['state']=tk.ACTIVE
        self.buttons['breplotSG']['state']=tk.ACTIVE        
        
#------------------------------------------------------------------------------        

    def readFilePlot(self):
        self.readFile()        
        
        if self.data2D is not None:
            self.updateWavMaxLevels()
            self.dataPlot()
            
#------------------------------------------------------------------------------   


    def updateWavMaxLevels(self):
        wletName=self.WletType.get()
        
        f,t=self.DataFromTo.get().split(':')        
        if f=='': f='0' 
        if t=='': t='-1'
                
        
        dataSize=int(t)-int(f)
        if dataSize>0:
            maxlevels=pywt.dwt_max_level(dataSize,wletName)
            self.WletLevels.set(maxlevels)
            self.flabels['Lmaxlevels']['text']='max. levels='+str(maxlevels)
        
#------------------------------------------------------------------------------        
        
    def dataReduction(self): 
        self.data2D=dpr.readFile(self.InputFileName.get())         
        if self.data2D is None:
            print('empty inpout data')
            return
        
        if self.DataOnOff.get():
            self.calibrate()
                
        self.data2D=dpr.selectData(self.data2D,self.DataFromTo.get())
        if self.data2D is None:
            print('empty inpout data')
            return
                                
        self.data2D=dpr.normData(self.data2D,self.DataReductType.get())
        if self.data2D is None:
            print('empty inpout data')
            return  
        
        
        self.dataInfo['r. type']=self.DataReductType.get()
        self.dataInfo['r. range']=self.DataFromTo.get()
        
#------------------------------------------------------------------------------        
                        
    def dataReductionPlot(self):
        self.dataReduction()                     
        if self.data2D is not None:  
            self.dataPlot()
#------------------------------------------------------------------------------       


    def reductionFiltering(self):
        self.dataReduction()              
        self.data2D=dpr.filteringData(self.data2D, self.FilterType.get(), 
                                      self.FilterRank.get(), self.FilterSize.get())
        self.dataInfo['f. name']=self.FilterType.get()
        self.dataInfo['f. rank']=self.FilterRank.get()
        self.dataInfo['f. size']=self.FilterSize.get()
        
#------------------------------------------------------------------------------                    
        

    def dataReductionFilteringPlot(self):        
        self.reductionFiltering()
        if self.data2D is not None:            
            self.dataPlot()
                
#------------------------------------------------------------------------------        
        
    def dataWaveletProcessing(self):     
        self.reductionFiltering() 
        
        if self.data2D is None:
            return
        
        wlevel=self.WletLevels.get()
        wname=self.WletType.get()
                
        self.dataInfo['ifile']=self.InputFileName.get()
        self.dataInfo['path']=os.getcwd()
        self.dataInfo['waveletname']=self.WletType.get()
        self.dataInfo['waveletlevels']=self.WletLevels.get()
        
                           
        baseline=baseline_dwt(self.data2D[:,1],level=wlevel,wavelet=wname,max_iter=100)
                        
        child=wpr.plotWindow(self)
        child.inX=self.data2D[:,0]
        child.inY=self.data2D[:,1]
        child.baseline=baseline
        child.outY=self.data2D[:,1]-baseline
        child.dataInfo=self.dataInfo
        
        corr_inoutY=np.corrcoef(child.inY, child.outY)
        
        
        ave_inY=np.average(child.inY)
        std_inY=np.std(child.inY)
        
        ave_bas=np.average(child.baseline)
        std_bas=np.std(child.baseline)
        
        ave_outY=np.average(child.outY)
        std_outY=np.std(child.outY)
        
        
        dM=child.dataMetrics
        dM['corr (S,R)']=corr_inoutY[0,1]
        dM['corr (B,S)']=np.corrcoef(child.inY, child.baseline)[0,1]
        dM['corr (R,B)']=np.corrcoef(child.outY, child.baseline)[0,1]
        
        dM['std (S,B)']=std_outY
        
        '''
        dM['ave Signal'] =ave_inY
        dM['ave Baseline'] =ave_bas
        dM['ave Final']=ave_outY
        '''
        
        '''
        dM['std Signal'] =std_inY
        dM['std Baseline'] =std_bas
        dM['std Final']=std_outY
        '''
        '''
        dM['aveIn'] =f'{ave_inY:6.3e}'
        dM['aveBs'] =f'{ave_bas:6.3e}'
        dM['aveOut']=f'{ave_outY:6.3e}'
        '''
        '''
        dM['stdIn'] =f'{std_inY:6.3e}'
        dM['stdBs'] =f'{std_bas:6.3e}'
        dM['stdOut']=f'{std_outY:6.3e}'
        '''
        
        plt_signal_args='.m'
        plt_signal_kwargs={'label':  'signal (S)',
                           'markersize': 0.5}
                
        plt_baseline_args='-k'
        plt_baseline_kwargs={'label':  'background (B)',
                           'linewidth': 0.5}
        
        plt_outY_args='-g'
        plt_outY_kwargs={'label':  'result (R)',
                           'linewidth': 2}
                        
        child.plot(plt_signal_args,plt_signal_kwargs,
                   plt_baseline_args,plt_baseline_kwargs,
                   plt_outY_args,plt_outY_kwargs  )
        
        #child.grid()
        child.pltLegend()
        child.pltTitle(self.InputFileName.get())        
                
        
#------------------------------------------------------------------------------        
        
    def plotWavelets(self):        
        child=wpw.plotWindow(self)


    def dataPlot(self):                              
        child=wp.plotWindow(self)
        child.data2D=self.data2D
        
        if bool(self.dataInfo):
            child.dataInfo=self.dataInfo
        
        plt_args='-m'
        plt_kwargs={'label':  self.InputFileName.get()}
        
        child.plot(plt_args,plt_kwargs)        
        child.pltTitle(self.InputFileName.get())
            
        
                        
#------------------------------------------------------------------------------        
    def initMenu(self):               
        menubar = Menu(self)
        self.master.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open",command=self.openFileDialog)
        fileMenu.add_command(label="Save")
        fileMenu.add_command(label="Exit", command=self.quit)
        
        optMenu =Menu(menubar)
        optMenu.add_command(label="Wavelets gallery",command=self.plotWavelets)
        
        winMenu=Menu(menubar)
        winMenu.add_command(label="Minimize all",command=self.menuMinimizeAll)
        winMenu.add_command(label="Show all",command=self.menuShowAll)
        winMenu.add_command(label="Always on top",command=self.menuShowAll)
        
        helpMenu=Menu(menubar)
        helpMenu.add_command(label="Authors/Credits",command=self.menuAuthors)
                
        menubar.add_cascade(label="File", menu=fileMenu)      
        menubar.add_cascade(label="Options",menu=optMenu)
        menubar.add_cascade(label="Windows",menu=winMenu)
        menubar.add_cascade(label="Help",menu=helpMenu)
        
        
#------------------------------------------------------------------------------        
        
    def menuMinimizeAll(self):        
        for w in self.winfo_children():            
            if re.search('plotwindow', str(w)):
                w.iconify()
                    
        
        
    def menuShowAll(self):        
        for w in self.winfo_children():            
            if re.search('plotwindow', str(w)):
               w.withdraw()     
               w.deiconify()       
               
               
        
    def stay_on_top(self):
       self.lift()
       self.after(2000, self.stay_on_top)   
       
    def menuAlwaysOnTop(self):        
        self.stay_on_top()
        
    def setDataRange(self,xmin,xmax):
        f,t=int(xmin),int(xmax)
        self.DataFromTo.set(str(f)+":"+str(t))
        self.updateWavMaxLevels()
        
     
                
#------------------------------------------------------------------------------        
    def menuAuthors(self):
        see_more = messagebox.showinfo(title='Credits',
                    message='🤠 author: K.Skrobas',
                    detail='Kazimierz.Skrobas@ncbj.gov.pl',
                    )        


#------------------------------------------------------------------------------
    def initInputFile(self):                
        bgcolor='cornsilk'
        
        fr=tk.LabelFrame(self,bg=bgcolor,text='Input Data',font=self.__titFont__,width=self.__frwidth__,height=240)
        #fr.pack(anchor='e')
        #fr.pack(anchor='w')
        fr.pack()
        fr.pack_propagate(False)
        fr.grid_propagate(False)
        #fr.grid(row=0)
                       
        #---------------- first row ----------------------------
                
        if self.TEST:
            self.InputFileName.set("/home/fizyk/pyt/tloremover/A1.npy")            
            
        inarg={'font': self.__defFont__, 
               'width': 52,
               'justify': 'center',}
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'}
        
        #  lecmFm.input.bind("<<ComboboxSelected>>",self.eWlFamilyChanged)
        lf=le.LabelEdit(fr,label='file name  ',
                        input_class=ttk.Entry,
                        input_var=self.InputFileName,
                        input_args=inarg,
                        label_args=lbarg)
        lf.grid(row=1,column=0,columnspan=3)
      
        
        self.imageFolder=tk.PhotoImage(file='folder.png')
        bt=tk.Button(fr,bg=bgcolor,image=self.imageFolder,command=self.openFileDialog)
        bt.grid(row=1,column=3,padx=10,pady=10)                
        #-------------------------------------------------------
        
        
        #------------------ second row -------------------------
        
        inarg={'font': self.__defFont__,
               'width': 10,
               'justify': 'center',
               'values': ['none','sqrt','log10']
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        

        lecm=le.LabelEdit(fr,label='reduction ',
                          input_class=ttk.Combobox,input_args=inarg,
                          input_var=self.DataReductType,
                          label_args=lbarg)
        lecm.grid(row=2,column=0,columnspan=1,padx=10,pady=10)

        
        inarg={'font': self.__defFont__,
               'width': 12,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        eft=le.LabelEdit(fr,label='from<:step:>:to  ',
                         input_class=ttk.Entry,
                         input_args=inarg,
                         input_var=self.DataFromTo,
                         label_args=lbarg)
        
        eft.grid(row=2,column=1,columnspan=1,padx=10,pady=10)
        eft.input.bind('<Return>',self.fromToEntryChanged)
        #state="disabled"
        
        if self.TEST:
            state='active'
        else:
            state='disable'
            
        self.logo=tk.PhotoImage(file='graph.png')
        bta=tk.Button(fr,bg=bgcolor,command=self.dataReductionPlot,state=state,image=self.logo)
        bta.grid(row=2,column=3,padx=10,pady=10)
        self.buttons['breplot']=bta
        #-------------------------------------------------------
        
        
        #------------------ calibrate -----------------------
        bg='khaki'
        frc=tk.LabelFrame(fr,bg=bg,text='Calibration: E=Ax+B,  I=y/C',font=self.__titFont__,width=self.__frwidth__)
        frc.grid(row=3,column=0,columnspan=6,padx=5,pady=5)
        
        self.DataOnOff=tk.IntVar()
        try:            
            self.DataOnOff.set(int(ini.getValue("calibration.pixe","onoff")))            
        except:
            self.DataOnOff.set("0")
        
        chb=tk.Checkbutton(frc,text="On/Off",background=bg,onvalue=1,offvalue=0,variable=self.DataOnOff,command=self.OnOffCalParams)
        chb.grid(row=0,column=0)
        
        #-----------
        self.Data_Aprm=tk.StringVar()
        try:            
            self.Data_Aprm.set(ini.getValue("calibration.pixe","A"))
        except:
            self.Data_Aprm.set("0.0224")
                        
        inarg={'font': self.__defFont__,
               'width': 8,
               'justify': 'center',
               'state' : 'disabled',
               
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bg,
               'justify': 'left'
               }
        
        leC_A=le.LabelEdit(frc,label='A',
                          input_class=ttk.Entry,input_args=inarg,
                          input_var=self.Data_Aprm,
                          label_args=lbarg)
        leC_A.grid(row=0,column=1,padx=5,pady=10)
        self.calibEntries['Aprm']=leC_A.input
        
        #-----------
        self.Data_Bprm=tk.StringVar()
        try:
            self.Data_Bprm.set(ini.getValue("calibration.pixe","B"))
        except:
            self.Data_Bprm.set("-0.15")
            
            
        inarg={'font': self.__defFont__,
               'width': 8,
               'justify': 'center',
               'state' : 'disabled',
               
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bg,
               'justify': 'left'
               }
        
        leC_B=le.LabelEdit(frc,label='B',
                          input_class=ttk.Entry,input_args=inarg,
                          input_var=self.Data_Bprm,
                          label_args=lbarg)
        leC_B.grid(row=0,column=3,padx=10,pady=10)
        self.calibEntries['Bprm']=leC_B.input
        
        #-----------

        self.Data_Cprm=tk.StringVar()
        try:
            self.Data_Cprm.set(ini.getValue("calibration.pixe","C"))
        except:
            self.Data_Cprm.set("1")
            
        inarg={'font': self.__defFont__,
               'width': 8,
               'justify': 'center',
               'state' : 'disabled',
               
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bg,
               'justify': 'left'
               }
        
        leC_C=le.LabelEdit(frc,label='C',
                          input_class=ttk.Entry,input_args=inarg,
                          input_var=self.Data_Cprm,
                          label_args=lbarg)
        leC_C.grid(row=0,column=4,padx=10,pady=10)
        self.calibEntries['Cprm']=leC_C.input
        #-----------
        ''''
        self.DataCalibUma=tk.StringVar()
        try:
            self.DataCalibUma.set(ini.getValue("calibration.pixe","uma"))
        except:
            self.DataCalibUma.set("1040")
            
        inarg={'font': self.__defFont__,
               'width': 8,
               'justify': 'center',
               'state' : 'disabled',
               
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bg,
               'justify': 'left'
               }
        
        leUMa=le.LabelEdit(frc,label='U Ma',
                          input_class=ttk.Entry,input_args=inarg,
                          input_var=self.DataCalibUma,
                          label_args=lbarg)
        leUMa.grid(row=1,column=6,padx=10,pady=10)   
        self.calibEntries['uma']=leUMa.input
        '''
        self.OnOffCalParams()
        
        
#------------------------------------------------------------------------------
        

    def initFilterData(self):        
        bgcolor='bisque2'
        
        fr=tk.LabelFrame(self,bg=bgcolor,text='Filter parameters',font=self.__titFont__,width=self.__frwidth__,height=75)
        fr.pack()
        fr.pack_propagate(False)
        fr.grid_propagate(False)
        #fr.grid(row=1)
        
        self.FilterType=tk.StringVar()
        try:            
            self.FilterType.set(ini.getValue("data.filtering","name"))
        except:
            self.FilterType.set('none')
        
        inarg={'font': self.__defFont__, 
               'text': self.FilterType,
               'width': 16,
               'justify': 'center',
               'values': [ 'Savitzky-Golay','moving average','none']}
        lbarg={'font': self.__defFont__ , 'background' : bgcolor}
                
        cm=le.LabelEdit(fr,label='name',
                        input_class=ttk.Combobox,
                        input_args=inarg,
                        label_args=lbarg)
        cm.grid(sticky='w',row=0,columnspan=1,padx=10,pady=10)
        
        self.FilterRank=tk.IntVar()
        try:
            self.FilterRank.set(int(ini.getValue("data.filtering", "rank")))
        except:
            self.FilterRank.set(3)
        
        inarg={'font': self.__defFont__, 
               'increment': 1,
               'from_':2,
               'to':6,
               'text': self.FilterRank,
               'width': 2 ,
               'justify': 'center',}
        lbarg={'font': self.__defFont__ , 'background' : bgcolor}
        
        sp=le.LabelEdit(fr,label=' rank',
                        input_class=ttk.Spinbox,
                        input_args=inarg,
                        label_args=lbarg)
        sp.grid(sticky='w',row=0,column=1,columnspan=1,padx=10,pady=10)
        
        self.FilterSize=tk.IntVar()
        try:
            self.FilterSize.set(ini.getValue("data.filtering","size"))
        except:
            self.FilterSize.set(100)
        
        inarg={'font': self.__defFont__, 
               'text': self.FilterSize,
               'width': 5,
               'justify': 'center',}
        lbarg={'font': self.__defFont__ , 'background' : bgcolor}
        
        ed=le.LabelEdit(fr,label='size',
                        input_class=ttk.Entry,
                        input_args=inarg,
                        label_args=lbarg)
        ed.grid(sticky='w',row=0,column=4,columnspan=2,padx=10,pady=10)
                    
        btaSG=tk.Button(fr,bg=bgcolor,command=self.dataReductionFilteringPlot,state="disabled",image=self.logo)
        btaSG.grid(row=0,column=6,padx=10,pady=10)
        self.buttons['breplotSG']=btaSG

#------------------------------------------------------------------------------
        
        
    def initWaveletData(self):
        bgcolor='bisque3'
        
        fr=tk.LabelFrame(self,bg=bgcolor,text='Wavelets',font=self.__titFont__,width=self.__frwidth__,height=125)
        fr.pack()
        fr.pack_propagate(False)
        fr.grid_propagate(False)
        
        #--------------------- first row -------------------------------------
        self.WletFamily=tk.StringVar()
        try:
            wletFamily=ini.getValue("wavelet.prms",'family')
            self.WletFamily.set(wletFamily)
            wletFamilyAbbrev=wletFamily.split(' ')[-1]
        except:
            self.WletFamily=tk.StringVar('Daubechies db')
            wletFamilyAbbrev='db'
        
    
        inarg={'font': self.__defFont__,
               'width': 25,
               'justify': 'center',
               'values': ['Daubechies db',
                          'Symlets sym',
                          'Coiflets coif',
                          'Biorthogonal bior',
                          'Reverse biorthogonal rbio',
                          ]
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        

        lecmFm=le.LabelEdit(fr,label='family ',
                          input_class=ttk.Combobox,input_args=inarg,
                          input_var=self.WletFamily,
                          label_args=lbarg)
        lecmFm.grid(row=0,column=0,columnspan=2,padx=10,pady=10)
        lecmFm.input.bind("<<ComboboxSelected>>",self.eWlFamilyChanged)
        #----------------------------------------------------------------------
        
        #--------------------- second row --------------------------------------
        
        wlcollection=pywt.wavelist(wletFamilyAbbrev)
        
        self.WletType=tk.StringVar()
        try:
            self.WletType.set(ini.getValue("wavelet.prms","name"))
        except:
            self.WletType.set(wlcollection[3]);
                    
        inarg={'font': self.__defFont__,
               'width': 10,
               'justify': 'center',
               'values': wlcollection,
               
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        lecm=le.LabelEdit(fr,label='name ',
                          input_class=ttk.Combobox,input_args=inarg,
                          input_var=self.WletType,
                          label_args=lbarg)
        lecm.grid(row=1,padx=10,pady=10)
        
        self.comboBox['Wlname']=lecm.input
                
            
        self.WletLevels=tk.IntVar()
        try:
            self.WletLevels.set(int(ini.getValue("wavelet.prms","levels")))
        except:
            self.WletLevels.set(6);
        
    
        inarg={'font': self.__defFont__,
               'width': 10,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        elev=le.LabelEdit(fr,label='level',
                          input_class=ttk.Entry,
                          input_args=inarg,
                          input_var=self.WletLevels,
                          label_args=lbarg)
        elev.grid(row=1,column=1,padx=10,pady=10)
        
        
        
        lmaxLevels=tk.Label(fr,text="-- no data --",bg=bgcolor,fg='black',font=self.__titFont__)
        lmaxLevels.grid(row=1,column=2,columnspan=4,padx=10,pady=10)
        self.flabels['Lmaxlevels']=lmaxLevels
        self.flabels['Lmaxlevels']['text']='max. levels='+str(self.WletLevels.get())
        
        #-----------------------------------------------------------

        
#------------------------------------------------------------------------------        
        
    def eWlFamilyChanged(self,event):
        evalue=event.widget.get().split()        
        wlcollection=pywt.wavelist(evalue[-1])        
        self.comboBox['Wlname']['values']=wlcollection
        self.WletType.set(wlcollection[3]);
                       
        
        
                        
    def openFileDialog(self):
        filetypes = ( ('pixie files','*.npy'),('pixie files','*.spe'),
                     ('data files', '*.dat'),
                     ('diff files','*.diff'),
                     ('All files', '*.*') )
        
        inputFileName=fd.askopenfilename(title='Open a file',
                                            initialdir=self.iniDir,
                                            filetypes=filetypes)
        if not inputFileName:
            print('no file selected')
            return
        
        ini.setValue('default','inpath', inputFileName)
        
        self.InputFileName.set(inputFileName)
        #print (self.InputFileName.get())        
        self.readFilePlot()
                        
        

                
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------        

class MyApp(tk.Tk):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.title("tlorem")
            self.geometry("700x560+1000+250")
            self.resizable(True,True)
            
            
            MF=MainFrame(self)            
            MF.grid()
                       
#------------------------------------------------------------------------------

if __name__=='__main__':    
    
    #build if not exists
    ini.setDefaultIni()
          
    app=MyApp()
    app.mainloop()
