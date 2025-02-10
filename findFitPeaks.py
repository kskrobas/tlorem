
from tkinter import ttk, Tk, Frame,Menu
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import filedialog as fd
#from ttkthemes import themed_tk as tk

import labelEdit as le
import windowPeaksFit as wpf

import numpy as np
from matplotlib.figure import Figure 
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 

from scipy.signal import find_peaks
import initsetRW as ini
from tkinter import messagebox



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class ExtNavigationToolbar(NavigationToolbar2Tk):
    
    def __init__(self, canvas, parent=None):
        super(ExtNavigationToolbar, self).__init__(canvas, parent)
        
        self.parent=parent
        s=ttk.Style()
        s.configure('Bfromto.TButton')
                    #font=tkFont.Font(family="Helvetica",size=14),)
                    #borderwidth=0)
        BgraphLimits=ttk.Button(self,text="find&fit",style='Bfromto.TButton',command=self.showABC)
        BgraphLimits.pack(side=tk.LEFT,padx=5,pady=5)
        
        
        
    def showABC(self):
        print(' ------------- abc ------------------')
        
#------------------------------------------------------------------------------

class findFitWindow(tk.Toplevel):
    
    data2D=None
    peaks=None
    upeaks=np.array([],int)
    
    
    __plt__=None
    __fig__=None
    __dx__=None
    
    flabels={}
    dataInfo={}
    dataMetrics={}
    
    __addPeakOn__=False
    __plotPoints__=None
    
    __currPoint__=None
    __mouseMotionID__=None
    __userPoints__=[]
#------------------------------------------------------------------------------    
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        self.__defFont__=tkFont.Font(family="FreeMono",size=12)
        self.__titFont__=tkFont.Font(family="Helvetica",size=14,weight='bold')
        self.initMenu()        
        self.geometry("900x825+50+50")
        self.title('find & fit peaks '+__name__)
        
        
        appDir=ini.getValue('default','apath') 
        self.InputFileName=tk.StringVar()    
        self.InputFileName.set(ini.getValue('default','inpath'))   
        fileName=self.InputFileName.get()                          
                                                                         
        self.iniDir= appDir if not fileName else fileName.rsplit('/',1)[0]
        

        #self.logo0=tk.PhotoImage(file='logo0.png')
        #tk.Label(self,image=self.logo0,bg="red", height=400).pack(fill='x',expand=False)
        self.pltLabel=tk.LabelFrame(self,text="",height=700)
        #self.pltLabel.pack(fill='x',expand=False)
        self.pltLabel.pack(fill='both',side=tk.TOP,expand=True)
        

    
        bgcolor='bisque3'
        
        fr=tk.LabelFrame(self,bg=bgcolor,text='Searching options',font=self.__titFont__,height=135)
        fr.pack(fill='x')
        fr.pack_propagate(False)
        fr.grid_propagate(False)
        
           
        #----------------------------------
        self.peakHeight=tk.StringVar()
        self.peakHeight.set("1")
        
        inarg={'font': self.__defFont__,
               'width': 6,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        ehigh=le.LabelEdit(fr,label='Height',
                         input_class=ttk.Entry,
                         input_args=inarg,
                         input_var=self.peakHeight,
                         label_args=lbarg)
        
        ehigh.grid(row=0,column=0,columnspan=1,padx=10,pady=10)
        
        
        self.peakWidth=tk.StringVar()
        self.peakWidth.set("10")
        
        inarg={'font': self.__defFont__,
               'width': 6,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        ewid=le.LabelEdit(fr,label='Width',
                         input_class=ttk.Entry,
                         input_args=inarg,
                         input_var=self.peakWidth,
                         label_args=lbarg)
        
        ewid.grid(row=0,column=1,columnspan=1,padx=10,pady=10)
        
        self.peakTh=tk.StringVar()
        self.peakTh.set("0")
        
        inarg={'font': self.__defFont__,
               'width': 6,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        ehigh=le.LabelEdit(fr,label='Threshold',
                         input_class=ttk.Entry,
                         input_args=inarg,
                         input_var=self.peakTh,
                         label_args=lbarg)        
        ehigh.grid(row=0,column=2,columnspan=1,padx=10,pady=10)
        
        
        self.peakDist=tk.StringVar()
        self.peakDist.set("10")
        
        inarg={'font': self.__defFont__,
               'width': 6,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        edist=le.LabelEdit(fr,label='Distance',
                         input_class=ttk.Entry,
                         input_args=inarg,
                         input_var=self.peakDist,
                         label_args=lbarg)        
        edist.grid(row=0,column=3,columnspan=1,padx=10,pady=10)
        
                                    
        s=ttk.Style()
        s.configure('Bfromto.TButton',
                    font=self.__titFont__)
                    #borderwidth=0)
        
        Bfindpeaks=ttk.Button(fr,text="find peaks",style='Bfromto.TButton',command=self.findPeaks)
        Bfindpeaks.grid(row=0,column=4,padx=10,pady=10)
        
        Bshowlist=ttk.Button(fr,text="fit peaks",style='Bfromto.TButton',command=self.showWindowPeaksFit)
        Bshowlist.grid(row=0,column=5,padx=10,pady=10)
        #Bfindpeaks.pack(side=tk.LEFT,padx=5,pady=5)
        
        linfo=tk.Label(fr,text="no results",bg=bgcolor,fg='black',font=self.__titFont__)
        linfo.grid(row=1,column=0,columnspan=4,padx=10,pady=10)
        self.flabels['linfo']=linfo
        
        self.Baddpeak=tk.Button(fr,text="add peaks: off ",relief="raised",command=self.BaddpeakOnClick,bg='pink1')
        self.Baddpeak.grid(row=1,column=4,padx=10,pady=10)
        
        self.Brempeaks=tk.Button(fr,text="del. peaks",command=self.BrempeaksOnClick)
        self.Brempeaks.grid(row=1,column=5,padx=10,pady=10)
        
        
#------------------------------------------------------------------------------     
    def graphMouseMotion(self,event):
        
        if event.xdata is None or event.ydata is None:
            return
                
        eX=event.xdata
        #eY=event.ydata
        pointsPlot=self.__plotPoints__
        plotX=pointsPlot[0].get_xdata()
        plotY=pointsPlot[0].get_ydata()
        tol=self.__dx__*0.5
        xdiff=np.abs(plotX-eX)
        ind=np.argwhere(xdiff<tol)
                
        plt=self.__plt__
        
        if self.__currPoint__ is not None:
            self.__currPoint__.remove()
            
            
        sx,sy=plotX[ind],plotY[ind]        
        self.__currPoint__, =plt.plot(sx,sy,'b^')
                
        event.canvas.draw()        
                            
#------------------------------------------------------------------------------
    def graphOnClick(self,event):
        '''
        print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
         ('double' if event.dblclick else 'single', event.button,
          event.x, event.y, event.xdata, event.ydata))
        
        plt=self.__plt__
        xdata,ydata=event.xdata,event.ydata
        plt.plot(xdata,ydata,'ok')
        '''
        
        if event.xdata is None or event.ydata is None:
            return
        
        eX=event.xdata
        #eY=event.ydata
        pointsPlot=self.__plotPoints__
        plotX=pointsPlot[0].get_xdata()
        plotY=pointsPlot[0].get_ydata()
        tol=self.__dx__*0.5
        xdiff=np.abs(plotX-eX)
        ind=np.argwhere(xdiff<tol)              
            
        sx,sy=plotX[ind],plotY[ind]        
        pltPeak, =self.__plt__.plot(sx,sy,'^',color='tab:orange',markersize=5)
        
        self.upeaks=np.append(self.upeaks,[ind])        
        self.__userPoints__.append(pltPeak)
                                
        event.canvas.draw()

#------------------------------------------------------------------------------
  
    def BaddpeakOnClick(self):
        if self.data2D is None:
            print(' empty data2D buffer')
        
        if self.__addPeakOn__:
            self.Baddpeak.config(relief="raised",bg='pink1',text="add peaks: off ")
            self.__fig__.canvas.mpl_disconnect(self.__mouseMotionID__)
            self.__fig__.canvas.mpl_disconnect(self.__buttonPressed__)
            if self.__currPoint__ is not None:
                self.__currPoint__.remove()
        else:
            self.Baddpeak.config(relief="sunken",bg='pale green',text="add peaks: on ")
            self.__mouseMotionID__=self.__fig__.canvas.mpl_connect('motion_notify_event', self.graphMouseMotion)            
            self.__buttonPressed__=self.__fig__.canvas.mpl_connect('button_press_event', self.graphOnClick)
            
        self.__addPeakOn__= not self.__addPeakOn__
        self.__fig__.canvas.draw()
        
    
    
    
    def BrempeaksOnClick(self):
        
        for addUserPeaks in self.__userPoints__:
            addUserPeaks.remove()
            
        self.__userPoints__=[]
        self.upeaks=np.array([],int)
        
        self.__fig__.canvas.draw()
        
        
        
#------------------------------------------------------------------------------
        
    def initMenu(self):               
        menubar = Menu(self)
        
        fileMenu = Menu(menubar)#font=("",14)
        fileMenu.add_command(label="Open",command=self.openFile)
        fileMenu.add_command(label="Save")
        fileMenu.add_command(label="Exit")
        
        optMenu =Menu(menubar)
        
        helpMenu=Menu(menubar)
        helpMenu.add_command(label="Authors/Credits")
        
        plotMenu=Menu(menubar)
        
        self.menuLegend=tk.BooleanVar()
        self.menuLegend.set(False)
                
        menubar.add_cascade(label="File", menu=fileMenu)      
        menubar.add_cascade(label="Options",menu=optMenu)
        menubar.add_cascade(label="Plot",menu=plotMenu)
        menubar.add_cascade(label="Help",menu=helpMenu)
        
        self.config(menu=menubar)
        
        
#------------------------------------------------------------------------------        
        
    def openFile(self):
        filetypes = ( ('results','*.out'),('All files', '*.*') )
        inputFileName=fd.askopenfilename(title='Open a file',
                                            initialdir=self.iniDir,
                                            filetypes=filetypes)
        if inputFileName=='':
            print('no file selected')
            return    
        
        self.data2D=np.loadtxt(inputFileName)[:,0:4:3]
        self.plot()
        
        #self.title=inputFileName
        self.pltTitle(inputFileName)




    def plot(self):
        if self.data2D is None:
            return
        
        self.__fig__= Figure(figsize = (4, 4), dpi = 150) 
        fig=self.__fig__
       
        
        self.__plt__=fig.add_subplot(111)
        plt=self.__plt__
        
        
        canvas = FigureCanvasTkAgg(fig, master = self.pltLabel)         
        toolbar = ExtNavigationToolbar(canvas,self.pltLabel)
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH,expand=1)
                                
        x,y=self.data2D[:,0],self.data2D[:,1]
        self.__plotPoints__=plt.plot(x,y,'-g')
        
        self.__dx__=np.min(np.diff(x,1))
        
        plt.spines['top'].set_visible(False)
        plt.spines['right'].set_visible(False)
        
        dstr= "  Input Status:\n"
        for key, value in self.dataInfo.items():
            if key=='ifile' or key=='path':
                continue
            dstr+= f" {key}: {value}\n"
            
        plt.text(0.8,0.5,dstr,transform=plt.transAxes,fontsize=8)
                
        self.__fig__.canvas.draw()
        
    
    
#------------------------------------------------------------------------------        
        
    def findPeaks(self):       
        if self.__fig__ is None:
            return
        
        fig=self.__fig__
                
        for ax in fig.get_axes():
            ax.remove()
                                    
        self.__plt__=fig.add_subplot(111)    
        plt=self.__plt__
        
        x,y=self.data2D[:,0],self.data2D[:,1]
        #prominence=(None,0.6)
        height=float(self.peakHeight.get())
        width=float(self.peakWidth.get())
        thresh=float(self.peakTh.get())
        distance=float(self.peakDist.get())
        
        try:
            peaks,props=find_peaks(y,height=height,width=width,threshold=thresh,distance=distance)
        except Exception as x:
            self.flabels['linfo']['text']='Error: '+str(x)
            self.flabels['linfo']['fg']='red'
            return
            
        
        if peaks.shape[0]<1:
            print('no peaks have been found')
            self.flabels['linfo']['text']='no peaks have been found'
            self.flabels['linfo']['fg']='blue'
            return
        
        
        self.flabels['linfo']['text']=str(peaks.shape[0])+' peaks have been found'
        self.flabels['linfo']['fg']='green'
        
        plt.plot(x,y,'-g')
        plt.plot(x,y,'.k',markersize=1)
        plt.plot(x[peaks],y[peaks],'^r',markersize=4)
        plt.spines['top'].set_visible(False)
        plt.spines['right'].set_visible(False)
        
        self.__fig__.canvas.draw()
        self.peaks=peaks
        
        #print(peaks)
        #print(x[peaks])
        
        
#------------------------------------------------------------------------------        
                
    def  showWindowPeaksFit(self):
                
        nOfpeaks=self.peaks.size if self.peaks is not None else 0
        nOfpeaks+=self.upeaks.size
        
        if nOfpeaks==0:
            messagebox.showinfo(title='Warning',
                        message='no peaks selected')    
            return
                        
        child=wpf.peaksFitWindow(self)        
        child.data2D=self.data2D
        child.dataInfo=self.dataInfo
        
        if self.peaks is not None:
            if self.upeaks.size:
                child.peaks=np.sort(np.concatenate([self.peaks,self.upeaks]))
            else:
                child.peaks=self.peaks
        else:
            child.peaks=np.sort(self.upeaks)
            
                            
        child.showPeaksList()
        
#------------------------------------------------------------------------------        


    def pltTitle(self,ptitle='title'):
        self.__plt__.set_title(ptitle)