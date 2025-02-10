#!/usr/bin/python3

from tkinter import ttk, Tk, Frame,Menu
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import filedialog as fd
from ttkthemes import ThemedTk


import labelEdit as le
import windowPlot as wp
import windowPlotResults as wpr
import windowPlotWavelets as wpw


import numpy as np
import regex as re
import pywt
from scipy.signal import savgol_filter
from skued import baseline_dwt

#from ttkthemes import themed_tk as tk
#import pywt
#pywt.wavelist()

class MainFrame(ttk.Frame):
    inputFile=""
    outputFile=""
    __currRow__=0
    __defFont__=""
    __titFont__=""
    
    data2D=None
    
    TEST=False
    
    def __getRow__(self):
        return self.__currRow__
    def __incRow__(self):
        self.__currRow__+=1
    
    
    
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        #style=ttk.Style()
        #style.theme_use('arc')
        
        self.initUI()                        
        self.font=self.__titFont__
        
        
        
        #self.attributes ('-topmost', True)
                        
                        
                
                        
    def initUI(self):          
        self.__defFont__=tkFont.Font(family="FreeMono",size=12)
        self.__titFont__=tkFont.Font(family="Helvetica",size=14)
        #self.configure(bg='red')
        
        self.buttons={}
        self.comboBox={}
        
        self.initMenu()
        self.initInputFile()
        self.initFilterData()
        self.initWaveletData()
        
        bcalc=tk.Button(self,text='   Run   💥 ',command=self.bcalcRun,
                        background='gold',
                        state="disabled",
                        font=self.__defFont__,width=50,height=2)
        bcalc.pack()
        
        self.buttons['bcalc']=bcalc
        
        
        
                  
    def openChild(self):
        child=wp.plotWindow(self)
        #child.grab_set()



        
    def dataReductionPlot(self):
        f,t=self.DataFromTo.get().split(':')
        f,t=int(f),int(t)
        
        fileName=self.InputFileName.get()
        if re.search('\.dat$',fileName):
            self.data2D=np.loadtxt(fileName)[f:t,:]
        else:
            if re.search('\.npy',fileName):
                self.data2D=np.load(fileName)[:,f:t].T
            else:
                self.data2D=np.loadtxt(fileName)[f:t,1:5:2]
            
        self.dataPlot()




    def dataReductionPlotSG(self):
        f,t=self.DataFromTo.get().split(':')
        f,t=int(f),int(t)
       
        fileName=self.InputFileName.get()
        if re.search('\.dat$',fileName):
            self.data2D=np.loadtxt(fileName)[f:t,:]
        else:
            if re.search('\.npy',fileName):
                self.data2D=np.load(fileName)[:,f:t].T
            else:
                self.data2D=np.loadtxt(fileName)[f:t,1:5:2]
                    
        filterType=self.FilterType.get()
        
        if filterType != 'None':
            npoints=self.FilterSize.get()
            if filterType == 'Savitzky-Golay':
                rank=self.FilterRank.get()                
                res=savgol_filter(self.data2D[:,1], npoints, rank)                
            else:
                kernel=np.ones((npoints,),float)/npoints
                res=np.convolve(kernel, self.data2D[:,1],'same')
                
            self.data2D[:,1]=res
            
        self.dataPlot()
        
        
        
    def plotWavelets(self):
        #if self.data2D is not None:    
        child=wpw.plotWindow(self)
        
        
        
        
        
    def readFilePlot(self):
        fileName=self.InputFileName.get()
                
        if re.search('\.dat$',fileName):
            self.data2D=np.loadtxt(fileName)
        else:
            if re.search('\.npy',fileName):
                self.data2D=np.load(fileName).T
            else:
                self.data2D=np.loadtxt(fileName)[:,1:5:2]
            
        self.DataFromTo.set("0:"+str(self.data2D.shape[0]-1))
        
        
        
        self.buttons['breplot']['state']=tk.ACTIVE
        self.buttons['bcalc']['state']=tk.ACTIVE
        self.buttons['breplotSG']['state']=tk.ACTIVE
        
        self.dataPlot()
        
        
                
        
    def dataPlot(self):        
        rtype=self.DataReductType.get()
        
        if rtype=='sqrt':
            indZero=np.where(self.data2D[:,1]<0)
            self.data2D[indZero,1]=0
            self.data2D[:,1]=self.data2D[:,1]**0.5
        else:
            if rtype=='log10':
                indOne=np.where(self.data2D[:,1]<1)
                self.data2D[indOne,1]=1
                self.data2D[:,1]=np.log10(self.data2D[:,1])
                            
        #if self.data2D is not None:    
        child=wp.plotWindow(self)
        child.data2D=self.data2D
        
        plt_args='-m'
        plt_kwargs={'label':  self.InputFileName.get()}
        
        #child.pltTitle=self.InputFileName.get()
        
        child.plot(plt_args,plt_kwargs)
        #child.grid()
        child.pltTitle(self.InputFileName.get())
        
        #child.legend()

        
                        
        
    def initMenu(self):               
        menubar = Menu(self)
        self.master.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open",command=self.openFileDialog)
        fileMenu.add_command(label="Save")
        fileMenu.add_command(label="Exit", command=self.onExit)
        
        optMenu =Menu(menubar)
        optMenu.add_command(label="abc")
        
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
        #app.attributes('-topmost', True)
#app.update()
#app.attributes('-topmost', False)
        
               
            
                
        
    def menuAuthors(self):
        see_more = messagebox.showinfo(title='Credits',
                    message='🤠 author: K.Skrobas',
                    detail='kskrobas@gmail.com',
                    )        
        #if not see_more:
        #    exit()        
        
        


    def initInputFile(self):                
        bgcolor='cornsilk'
        
        #fr=ttk.LabelFrame(self,bg=bgcolor,text='Input Data',font=self.__titFont__,width=550,height=125)
        fr=ttk.LabelFrame(self,text='Input Data',width=550,height=125)
        #fr.pack(anchor='e')
        #fr.pack(anchor='w')
        fr.pack()
        fr.pack_propagate(False)
        fr.grid_propagate(False)
        #fr.grid(row=0)
                       
        #---------------- first row ----------------------------
        self.InputFileName=tk.StringVar()
        #self.InputFileName.set("--empty--")
        if self.TEST:
            self.InputFileName.set("/home/fizyk/python/tloremover/A1.npy")            
        else:
            self.InputFileName.set("--- empty ---")
            
            
        inarg={'font': self.__defFont__, 
               'width': 35,
               'justify': 'center',}
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'}
        
        
        lf=le.LabelEdit(fr,label='file name  ',
                        input_class=ttk.Entry,
                        input_var=self.InputFileName,
                        input_args=inarg,
                        label_args=lbarg)
        lf.grid(row=1,column=0,columnspan=4)
        
        
        bt=tk.Button(fr,text='🡅',bg=bgcolor,command=self.openFileDialog)
        bt.grid(row=1,column=5,padx=10,pady=10)                
        #-------------------------------------------------------
        
        
        #------------------ second row -------------------------
        self.DataReductType=tk.StringVar()
        self.DataReductType.set("None")
        inarg={'font': self.__defFont__,
               'width': 10,
               'justify': 'center',
               'values': ['None','sqrt','log10']
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        

        lecm=le.LabelEdit(fr,label='reduction ',
                          input_class=ttk.Combobox,input_args=inarg,
                          input_var=self.DataReductType,
                          label_args=lbarg)
        lecm.grid(row=2,column=0,columnspan=2,padx=10,pady=10)


        self.DataFromTo=tk.StringVar()
        if self.TEST:
            self.DataFromTo.set("0:10000")
        else:
            self.DataFromTo.set(":")
            
        
        inarg={'font': self.__defFont__,
               'width': 12,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        eft=le.LabelEdit(fr,label='from:to  ',
                         input_class=ttk.Entry,
                         input_args=inarg,
                         input_var=self.DataFromTo,
                         label_args=lbarg)
        
        eft.grid(row=2,column=3,columnspan=2,padx=10,pady=10)
        #state="disabled"
        
        if self.TEST:
            state='active'
        else:
            state='disable'
            
        bta=tk.Button(fr,text='☢',bg=bgcolor,command=self.dataReductionPlot,state=state)
        bta.grid(row=2,column=5,padx=10,pady=10)
        self.buttons['breplot']=bta
        #-------------------------------------------------------
        
        
        
        
    def initFilterData(self):
        
        bgcolor='bisque2'
        
        fr=tk.LabelFrame(self,bg=bgcolor,text='Filter parameters',font=self.__titFont__,width=550,height=75)
        fr.pack()
        fr.pack_propagate(False)
        fr.grid_propagate(False)
        #fr.grid(row=1)
        
        self.FilterType=tk.StringVar()
        self.FilterType.set("None")
        inarg={'font': self.__defFont__, 
               'text': self.FilterType,
               'width': 16,
               'justify': 'center',
               'values': ['moving average','Savitzky-Golay','None']}
        lbarg={'font': self.__defFont__ , 'background' : bgcolor}
                
        cm=le.LabelEdit(fr,label='name',
                        input_class=ttk.Combobox,
                        input_args=inarg,
                        label_args=lbarg)
        cm.grid(sticky='w',row=0,columnspan=1,padx=10,pady=10)
        
        self.FilterRank=tk.IntVar()
        self.FilterRank.set(5)
        
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
                    
        btaSG=tk.Button(fr,text='☢',bg=bgcolor,command=self.dataReductionPlotSG,state="disabled")
        btaSG.grid(row=0,column=6,padx=10,pady=10)
        self.buttons['breplotSG']=btaSG


        
        
    def initWaveletData(self):
        bgcolor='bisque3'
        
        fr=tk.LabelFrame(self,bg=bgcolor,text='Wavelets',font=self.__titFont__,width=550,height=125)
        fr.pack()
        fr.pack_propagate(False)
        fr.grid_propagate(False)
        
        #--------------------- first row -------------------------------------
        self.WletFamily=tk.StringVar()
        self.WletFamily.set("Daubechies db");
        
    
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
        
        wlcollection=pywt.wavelist('db')
        
        self.WletType=tk.StringVar()
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
        #-----------------------------------------------------------
        btaWl=tk.Button(fr,text='☢',bg=bgcolor,command=self.plotWavelets)
        btaWl.grid(row=1,column=3,padx=10,pady=10)
        #btaWl.place(x=400,y=50)
        #self.buttons['breplotSG']=btaSG
        
        
        
        
    def eWlFamilyChanged(self,event):
        evalue=event.widget.get().split()        
        wlcollection=pywt.wavelist(evalue[-1])        
        self.comboBox['Wlname']['values']=wlcollection
        self.WletType.set(wlcollection[3]);
        
        
        
                
    def onExit(self):
        self.quit()                    
 
    
 
        
    def openFileDialog(self):
        filetypes = ( ('pixie files','*.npy'),('data files', '*.dat'),('diff files','*.diff'),('All files', '*.*') )
        inputFileName=fd.askopenfilename(title='Open a file',
                                            initialdir='/home/fizyk/python/pyt/tloremover',
                                            filetypes=filetypes)
        
        self.InputFileName.set(inputFileName)
        print (self.InputFileName.get())
        
        self.readFilePlot()
        
        
        
        
    def bcalcRun(self):
        wlevel=self.WletLevels.get()
        wname=self.WletType.get()
        
        f,t=self.DataFromTo.get().split(':')
        f,t=int(f),int(t)
        
        fileName=self.InputFileName.get()
        if re.search('\.dat$',fileName):
            self.data2D=np.loadtxt(fileName)[f:t,:]
        else:
            if re.search('\.npy',fileName):
                self.data2D=np.load(fileName)[:,f:t].T
            else:
                self.data2D=np.loadtxt(fileName)[f:t,1:5:2]
            
                        
        rtype=self.DataReductType.get()
        
        if rtype=='sqrt':
            indZero=np.where(self.data2D[:,1]<0)
            self.data2D[indZero,1]=0
            self.data2D[:,1]=self.data2D[:,1]**0.5
        else:
            if rtype=='log10':
                indOne=np.where(self.data2D[:,1]<1)
                self.data2D[indOne,1]=1
                self.data2D[:,1]=np.log10(self.data2D[:,1])
                        
        filterType=self.FilterType.get()
        
        if filterType != 'None':
            npoints=self.FilterSize.get()
            if filterType == 'Savitzky-Golay':
                rank=self.FilterRank.get()                
                res=savgol_filter(self.data2D[:,1], npoints, rank)                
            else:
                kernel=np.ones((npoints,),float)/npoints
                res=np.convolve(kernel, self.data2D[:,1],'same')
                
            self.data2D[:,1]=res
                                
        baseline=baseline_dwt(self.data2D[:,1],level=wlevel,wavelet=wname,max_iter=100)
                        
        child=wpr.plotWindow(self)
        child.inX=self.data2D[:,0]
        child.inY=self.data2D[:,1]
        child.baseline=baseline
        child.outY=self.data2D[:,1]-baseline
        
        plt_signal_args='.m'
        plt_signal_kwargs={'label':  'signal',
                           'markersize': 0.5}
                
        plt_baseline_args='-k'
        plt_baseline_kwargs={'label':  'baseline',
                           'linewidth': 0.5}
        
        plt_outY_args='-g'
        plt_outY_kwargs={'label':  'result',
                           'linewidth': 2}
                        
        child.plot(plt_signal_args,plt_signal_kwargs,
                   plt_baseline_args,plt_baseline_kwargs,
                   plt_outY_args,plt_outY_kwargs  )
        
        child.grid()
        child.legend()
        child.pltTitle(self.InputFileName.get())
                
            

    
    
class MyApp(ThemedTk):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.title("tloszum remover test")
            self.geometry("550x375+1000+250")
            self.resizable(True,True)
            
            #style=ttk.Style()
            #style.theme_use("winxpblue")
            #them=self.settings.get('theme').get()
            
            
            MF=MainFrame(self)
            
            MF.grid()
           

            
#https://ttkthemes.readthedocs.io/en/latest/themes.html
if __name__=='__main__':
    app=MyApp()
    app.set_theme('winxpblue')
    app.mainloop()
