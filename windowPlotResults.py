

from tkinter import ttk, Tk, Frame,Menu
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import filedialog as fd

import labelEdit as le
import numpy as np

from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 

from datetime import datetime

import findFitPeaks as ffp



#------------------------------------------------------------------------------

class ExtNavigationToolbar(NavigationToolbar2Tk):
    
    def __init__(self, canvas, parent=None):
        super(ExtNavigationToolbar, self).__init__(canvas, parent)
        
        self.parent=parent
        s=ttk.Style()
        s.configure('Bfromto.TButton')
                    #font=tkFont.Font(family="Helvetica",size=14),)
                    #borderwidth=0)
        BgraphLimits=ttk.Button(self,text="find&fit",style='Bfromto.TButton',command=self.callFindFit)
        BgraphLimits.pack(side=tk.LEFT,padx=5,pady=5)
        
        
        
    def callFindFit(self):
        self.parent.findAndFitWindow()
                    
#------------------------------------------------------------------------------        
        

class plotWindow(tk.Toplevel):
    
    inX,inY=None,None
    baseline=None
    outY=None
    dataInfo={}
    dataMetrics={}
    
    __plt__=''
    __fig__=''
    __grid__=''
    
    
    
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
                
        self.initMenu()        
        self.geometry("1200x600")
        self.title('')

        

        
    def initMenu(self):               
        menubar = Menu(self)
        

        fileMenu = Menu(menubar)
        #fileMenu.add_command(label="Open")
        fileMenu.add_command(label="Save",command=self.saveResults)
        fileMenu.add_command(label="Exit")
        
        optMenu =Menu(menubar)
        optMenu.add_command(label="abc")
        
        plotMenu=Menu(menubar)
        
        self.menuLegend=tk.BooleanVar()
        self.menuLegend.set(True)
        
        plotMenu.add_checkbutton(label="Legend",onvalue=1,offvalue=0,command=self.pltLegend,variable=self.menuLegend)
        plotMenu.add_checkbutton(label="Grid",onvalue=1,offvalue=0,command=self.pltGrid)
        
        
        helpMenu=Menu(menubar)
        helpMenu.add_command(label="Authors/Credits")
                
        menubar.add_cascade(label="File", menu=fileMenu)      
        menubar.add_cascade(label="Options",menu=optMenu)
        menubar.add_cascade(label="Plot",menu=plotMenu)
        menubar.add_cascade(label="Help",menu=helpMenu)
        
        self.config(menu=menubar)
        
        
                
        
    def saveResults(self):
        filetypes = ( ('results','*.out'),('All files', '*.*') )
        outputFileName=fd.asksaveasfilename(title='Save a file',
                                          initialdir='/home/fizyk/python/pyt/',
                                          filetypes=filetypes)

        fid=open(outputFileName,'w')
        fid.write('#ver: 0 \n')
        fid.write('#date: '+datetime.today().strftime('%Y-%m-%d')+'\n')
        fid.write('#path: '+self.dataInfo['path']+'\n')
        fid.write('#file: '+self.dataInfo['ifile']+'\n')
        fid.write('#reduction: '+self.dataInfo['r. type']+'\n')
        fid.write('#range: '+self.dataInfo['r. range']+'\n')
        fid.write('#filter: '+self.dataInfo['f. name']+'\n')
        fid.write('#rank: '+str(self.dataInfo['f. rank'])+'\n')
        fid.write('#size: '+str(self.dataInfo['f. size'])+'\n')
        fid.write('#wavelet: '+self.dataInfo['waveletname']+'\n')
        fid.write('#levels: '+str(self.dataInfo['waveletlevels'])+'\n')
        fid.write('#---- x ---- input ---- baseline ---- output ----\n')

        for i in range(0,self.inX.shape[0]):
            x,y,b,o=self.inX[i],self.inY[i],self.baseline[i],self.outY[i]
            dstr=f'{x:10.6f}  {y:10.6f}  {b:10.6f}  {o:10.6f}\n'
            fid.write(dstr)

        fid.close();




    def onExit(self):
        self.quit()         
        
        
    def plot(self,
             plt_signal_args=None,
             plt_signal_kwargs=None,
             plt_baseline_args=None,
             plt_baseline_kwargs=None,
             plt_outY_args=None,
             plt_outY_kwargs=None): 
        
        plt_signal_args=plt_signal_args or {}
        plt_baseline_args=plt_baseline_args or {}
        plt_outY_args=plt_outY_args or {}
        
        plt_signal_kwargs=plt_signal_kwargs or {}
        plt_baseline_kwargs=plt_baseline_kwargs or {}
        plt_outY_kwargs=plt_outY_kwargs or {}
        
        self.__fig__ = Figure(figsize = (5, 3), dpi = 150) 
        fig=self.__fig__
        self.__plt__=fig.add_subplot(111)
        plt=self.__plt__
        
        #--------------------------------------------------
        if  bool(self.dataInfo) or bool(self.dataMetrics):            
            fig.subplots_adjust(left=0.1,right=0.8)
            plt.spines['top'].set_visible(False)
            plt.spines['right'].set_visible(False)
        #--------------------------------------------------    
            
        if  bool(self.dataInfo):
            dstr= "  Input Status:\n"
            for key, value in self.dataInfo.items():
                if key=='ifile' or key=='path':
                    continue
                dstr+= f" {key}: {value}\n"
                
            plt.text(1.0,0.5,dstr,transform=plt.transAxes,fontsize=8)
        #--------------------------------------------------    
            
        if bool(self.dataMetrics):                                      
            mstr= "  Metrics:\n"+"\n".join(f' {k}={v:5.3f}' for k,v in self.dataMetrics.items())
            plt.text(1.0,0.25,mstr, transform=plt.transAxes,fontsize=8)
        #--------------------------------------------------   
        
        inX,inY,baseline,outY=self.inX,self.inY,self.baseline,self.outY
        
        
        if self.inX is not None:
            plt.plot(inX,inY,plt_signal_args,**plt_signal_kwargs)
            
        if self.baseline is not None:
            plt.plot(inX,baseline,plt_baseline_args,**plt_baseline_kwargs)
            
        if self.outY is not None:
            plt.plot(inX,outY,plt_outY_args,**plt_outY_kwargs)
                                     
        canvas = FigureCanvasTkAgg(fig, master = self) 
        #toolbar = NavigationToolbar2Tk(canvas, self) 
        toolbar=ExtNavigationToolbar(canvas,self)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH,expand=1)



        
    def pltGrid(self):
        self.__plt__.grid()
        self.__fig__.canvas.draw()
        
    def pltLegend(self):
        self.__plt__.legend().set_visible(self.menuLegend.get()) 
        self.__fig__.canvas.draw()
        
    def pltTitle(self,ptitle='title'):
        self.__plt__.set_title(ptitle)        
        
        
    def findAndFitWindow(self):
        
        child=ffp.findFitWindow(self)      
        xlim=self.__plt__.get_xlim()        
        xmin,xmax=xlim[0],xlim[1]
        ind=np.argwhere( (self.inX>xmin) & (self.inX<xmax) )        
        imin,imax=int(ind[0]),int(ind[-1])
        isize=int(imax-imin)
        
        child.data2D=np.ndarray((isize,2),float)
        child.data2D[:,0]=self.inX [imin:imax]
        child.data2D[:,1]=self.outY[imin:imax]
        child.dataInfo=self.dataInfo
        child.plot()
        
        

        
        
