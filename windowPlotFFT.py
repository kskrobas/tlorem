

from tkinter import ttk, Tk, Frame,Menu
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import filedialog as fd
#from ttkthemes import themed_tk as tk

import labelEdit as le
import numpy as np
from numpy.fft import fft, ifft

from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
from matplotlib.backend_tools import ToolBase
import numpy as np
import pyperclip as pc

import pandas as pd



class ExtNavigationToolbar(NavigationToolbar2Tk):
    
    def __init__(self, canvas, parent=None,plt=None,data2D=None):
        super(ExtNavigationToolbar, self).__init__(canvas, parent)
        
        self.plt=plt
        self.data2D=data2D
        self.parent=parent
        
               
        s=ttk.Style()
        s.configure('Bfromto.TButton',
                    font=tkFont.Font(family="FreeMono",size=12),
                    borderwidth=0)
        BgraphLimits=ttk.Button(self,text="<--->",style='Bfromto.TButton',command=self.xlimCommand)
        BgraphLimits.pack(side=tk.LEFT,padx=5,pady=5)
        
        
        # Add "Graph Type" drop-down menu
        graph_types = ["Line Graph", "Bar Chart", "Scatter Plot"]
        self.GraphType=tk.StringVar()
        self.GraphType.set("Line Graph")
        CBgraphtypes=ttk.Combobox(self,values=graph_types,textvariable=self.GraphType)
        CBgraphtypes.bind("<<ComboboxSelected>>",self.cbgraphtypeCommand)
        CBgraphtypes.pack(side=tk.LEFT,padx=5,pady=5)
        

    
    
    def xlimCommand(self):
        self.parent.setXLim()
    
    def cbgraphtypeCommand(self,event):
        evalue=event.widget.get()       
        #wlcollection=pywt.wavelist(evalue[-1])        
        #self.comboBox['Wlname']['values']=wlcollection
        #self.WletType.set(wlcollection[3]);
        #print(evalue)
        
        fig = self.canvas.figure        
        for ax in fig.get_axes():
            ax.remove()
                                    
        self.plt=fig.add_subplot(111)                
            
        if self.GraphType.get()=="Scatter Plot":
            print("scatter")
            self.plt.scatter(self.data2D[:,0],self.data2D[:,1],color='magenta',s=0.5)
        else:
            print('else')
            self.plt.plot(self.data2D[:,0],self.data2D[:,1],'-m')
        
        fig.canvas.draw()
        



class plotWindow(tk.Toplevel):
    
    data2D=None
    #pltTitle=None
    
    __plt__=''
    __fig__=''
    __grid__=''
    
    __menuCheckButton__=''
    dataInfo={}
   
    
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        
        self.initMenu()        
        self.geometry("800x600")
        self.title('FFT')
        self.iniDir='/home/fizyk/python/tloremover-git/inputData/'
        self.parent=parent
        

        
        
    def initMenu(self):               
        menubar = Menu(self)
        

        fileMenu = Menu(menubar)#font=("",14)
        #fileMenu.add_command(label="Open")
        fileMenu.add_command(label="Save",command=self.dataSave)
        fileMenu.add_command(label="Exit")
        
        optMenu =Menu(menubar)
        optMenu.add_command(label="data  to  clipboard",command=self.dataToClipboard)
        optMenu.add_command(label="data from clipboard",command=self.dataFromClipboard)
                        
        self.menuXAxisLog=tk.BooleanVar()
        self.menuXAxisLog.set(False)
        
        optMenu.add_checkbutton(label="X-axis log",onvalue=1,offvalue=0,
                                command=self.eventXAxisLog,variable=self.menuXAxisLog)
        
        self.menuYAxisLog=tk.BooleanVar()
        self.menuYAxisLog.set(False)
        
        optMenu.add_checkbutton(label="Y-axis log",onvalue=1,offvalue=0,
                                command=self.eventYAxisLog,variable=self.menuYAxisLog)  
        
        
        
        
        helpMenu=Menu(menubar)
        helpMenu.add_command(label="Authors/Credits")
        
        plotMenu=Menu(menubar)
        
        self.menuLegend=tk.BooleanVar()
        self.menuLegend.set(False)
        
        plotMenu.add_checkbutton(label="Legend",onvalue=0,offvalue=0,command=self.pltLegend,variable=self.menuLegend)
        plotMenu.add_checkbutton(label="Grid",onvalue=1,offvalue=0,command=self.pltGrid)
        
        
        
        ##self.menuCheckButton['legend']=mlegend
                
        menubar.add_cascade(label="File", menu=fileMenu)      
        menubar.add_cascade(label="Options",menu=optMenu)
        menubar.add_cascade(label="Plot",menu=plotMenu)
        menubar.add_cascade(label="Help",menu=helpMenu)
        
        self.config(menu=menubar)
        
        
        
        
    def dataSave(self):
        filetypes = ( ('results','*.fft'),('All files', '*.*') )
        outputFileName=fd.asksaveasfilename(title='Save a file',
                              initialdir=self.iniDir,
                              filetypes=filetypes)
                    
        self.data2D.savetxt(outputFileName)
        
            
            
       #-------------------------------------------------- 
                
# sudo apt install xclip        
# pip install paperclip

    def dataToClipboard(self):
        df = pd.DataFrame(self.data2D)
        df.to_clipboard(sep='\t') 
        
    def dataFromClipboard(self):
        df=pd.read_clipboard().to_numpy()
        
        plt=self.__plt__
        plt.plot(df[:,0],df[:,1],'.k',markersize=0.5,label='data from clipboard')
        
        self.__fig__.canvas.draw()
    #--------------------------------------------------   
    
    def eventXAxisLog(self):
        if self.menuXAxisLog.get():
            self.__plt__.set_xscale('log',base=10)
        else:
            self.__plt__.set_xscale('linear')
            
        self.__fig__.canvas.draw()
            
            
            
    def eventYAxisLog(self):
        if self.menuYAxisLog.get():
            self.__plt__.set_yscale('log',base=10)
        else:
            self.__plt__.set_yscale('linear')        
            
        self.__fig__.canvas.draw()            
       


    def onExit(self):
        self.quit()         
    #--------------------------------------------------   


        
    def plot(self,plt_args=None,plt_kwargs=None): 
        
        if self.data2D is  None:
            return
        
        plt_args=plt_args or {}
        plt_kwargs=plt_kwargs or {}
        
        self.__fig__ = Figure(figsize = (4, 3), dpi = 150) 
        fig=self.__fig__
        fig.canvas.mpl_connect('button_press_event', self.graphOnClick)
        
        
        self.__plt__=fig.add_subplot(111)        
        plt=self.__plt__
        
        
        if  bool(self.dataInfo):
            fig.subplots_adjust(right=0.95)
              
        
        
        #x=self.data2D[:,0]
        y=self.data2D[:,1]
        L2=y.shape[0]*0.5
        #ts=1.0/x.shape[0]
        #fq=np.linspace(0,1,x.shape[0])
        fq=np.arange(0,y.shape[0])
        
        yfft=fft(y)
        print(yfft.shape)
        L2=int(yfft.shape[0]*0.5)
        
        plt.stem(fq[0:L2],np.abs(yfft[0:L2]),'b',markerfmt=" ",basefmt='-b')
        plt.set_ylabel('Amplitude')
        #plt.set_yscale('log')
        #plt.set_xscale('log')
        
 
                  
        canvas = FigureCanvasTkAgg(fig, master = self)         
        toolbar=ExtNavigationToolbar(canvas,self,self.__plt__,self.data2D)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH,expand=1)
    #--------------------------------------------------
        
        
                
    def pltGrid(self):        
        self.__plt__.grid()
        self.__fig__.canvas.draw()
        
        
    def pltLegend(self):          
        self.__plt__.legend().set_visible(self.menuLegend.get())            
        self.__fig__.canvas.draw()
        

    def pltTitle(self,ptitle='title'):
        self.__plt__.set_title(ptitle)
        
    
    
    def graphOnClick(self,event):
        return
    '''
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
         ('double' if event.dblclick else 'single', event.button,
          event.x, event.y, event.xdata, event.ydata))
        '''
            

        
        
