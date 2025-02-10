

from tkinter import ttk, Tk, Frame,Menu
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from tkinter import filedialog as fd

import labelEdit as le
import numpy as np
import pywt

from matplotlib.figure import Figure 
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 


class plotWindow(tk.Toplevel):
    
    inX,inY=None,None
    baseline=None
    outY=None
    
    __plt__=''
    __fig__=''
    __grid__=''
    

    
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        self.__defFont__=tkFont.Font(family="FreeMono",size=12)
        self.__titFont__=tkFont.Font(family="Helvetica",size=14)
        self.initMenu()        
        self.geometry("1200x800")
        self.title('wavelets gallery')
        
      
        #self.logo0=tk.PhotoImage(file='logo0.png')
        #tk.Label(self,image=self.logo0,bg="red", height=400).pack(fill='x',expand=False)
        self.pltLabel=tk.LabelFrame(self,text="",height=700)
        #self.pltLabel.pack(fill='x',expand=False)
        self.pltLabel.pack(fill='both',side=tk.TOP,expand=True)
        
        self.__fig__= Figure(figsize = (4,3), dpi = 150) 
        fig=self.__fig__
        
        
        
        canvas = FigureCanvasTkAgg(fig, master = self.pltLabel) 
        toolbar = NavigationToolbar2Tk(canvas, self.pltLabel) 
        toolbar.update()
        canvas._tkcanvas.pack(fill=tk.BOTH,expand=1)
        
        self.comboBox={}
                
        self.initWaveletData()
        
        
        
        
    def initMenu(self):               
        menubar = Menu(self)
        

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open")
        fileMenu.add_command(label="Save")
        fileMenu.add_command(label="Exit")
        
        optMenu =Menu(menubar)
        
        self.menuXAxisLog=tk.BooleanVar()
        self.menuXAxisLog.set(True)
        
        optMenu.add_checkbutton(label="X-axis log",onvalue=1,offvalue=0,
                                command=self.eventXAxisLog,variable=self.menuXAxisLog)
        
        self.menuYAxisLog=tk.BooleanVar()
        self.menuYAxisLog.set(False)
        
        optMenu.add_checkbutton(label="Y-axis log",onvalue=0,offvalue=0,
                                command=self.eventYAxisLog,variable=self.menuYAxisLog)  
        
        #command=self.pltGrid
        optMenu.add_checkbutton(label="Grid",onvalue=1,offvalue=0,command=self.pltGrid)
        
        
        
        helpMenu=Menu(menubar)
        helpMenu.add_command(label="Authors/Credits")
                
        menubar.add_cascade(label="File", menu=fileMenu)      
        menubar.add_cascade(label="Options",menu=optMenu)
        menubar.add_cascade(label="Help",menu=helpMenu)
        
        self.config(menu=menubar)
        
        
        
        
    def eventXAxisLog(self):
        if self.menuXAxisLog.get():
            self.a1.set_xscale('log',base=2)
            self.a3.set_xscale('log',base=2)
        else:
            self.a1.set_xscale('linear')
            self.a3.set_xscale('linear')
            
        self.__fig__.canvas.draw()
            
        
        
        
        
    def eventYAxisLog(self):
        if self.menuYAxisLog.get():
            self.a1.set_yscale('log')
            self.a1.set_ylabel('Gain [dB]')
            self.a3.set_yscale('log')
            self.a3.set_ylabel('Gain [dB]')
        else:
            self.a1.set_yscale('linear')  
            self.a1.set_ylabel('Gain')
            self.a3.set_yscale('linear')  
            self.a3.set_ylabel('Gain')
            
        self.__fig__.canvas.draw()
        
        
        
        
    def pltGrid(self):        
        self.a0.grid()
        self.a1.grid()
        self.__fig__.canvas.draw()
        
                 
        
        
    def initWaveletData(self):
         bgcolor='bisque3'
         
         fr=tk.LabelFrame(self,bg=bgcolor,text='Wavelets',font=self.__titFont__,height=125)
         fr.pack(fill='x')
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
         self.WletType.set(wlcollection[5]); #db8
                     
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
                 
             
         self.WletLevels=tk.StringVar()
         self.WletLevels.set("1:2:9");
         
     
         inarg={'font': self.__defFont__,
                'width': 10,
                'justify': 'center',
                }
         lbarg={'font': self.__defFont__ , 
                'background' : bgcolor,
                'justify': 'left'
                }
         
         elev=le.LabelEdit(fr,label='level(s)',
                           input_class=ttk.Entry,
                           input_args=inarg,
                           input_var=self.WletLevels,
                           label_args=lbarg)
         elev.grid(row=1,column=1,padx=10,pady=10)
         #-----------------------------------------------------------
         btaWl=tk.Button(fr,text=' ↷',bg=bgcolor,command=self.plot,width=5,height=2)
         btaWl.grid(row=1,column=3,padx=10,pady=10)
         btaWl.place(x=400,y=25)        
        
         self.plot()
        
    #def initUI(self):
    #    bb=ttk.Button(self,text='wykres',command=self.plot)
    #    bb.pack()
        #bb.grid(row=0,column=0)        


    def onExit(self):
        self.quit()         
        
        
    def plot(self):                 
        
        fig=self.__fig__        
        fig.clear()
        
        self.a0=fig.add_subplot(2,2,1)
        a0=self.a0
        
        self.a2=fig.add_subplot(2,2,2)
        a2=self.a2
        
        self.a1=fig.add_subplot(2,2,3)
        a1=self.a1
        a1.set_xscale('log',base=2)
        
        self.a3=fig.add_subplot(2,2,4)
        a3=self.a3
        a3.set_xscale('log',base=2)

        
        name=self.WletType.get()
        wlev=self.WletLevels.get().split(':')
        #print(wlev)
        #f,t=int(wlev[0]),int(wlev[1])
        
        if len(wlev)==3:
            f,s,t=int(wlev[0]),int(wlev[1]),int(wlev[2])+1
        else:
            f,s,t=int(wlev[0]),1,int(wlev[1])+1

        kolors=list(mcolors.TABLEAU_COLORS.keys())
        
                        
        
        #nlev=10
        for i,nlev in enumerate(range(f,t,s)):
            
            kolor=kolors[np.mod(i,10)]
            
            wavp=pywt.Wavelet(name).wavefun(level=nlev)
            wavpx=wavp[-1][:]
            wavpy=wavp[-2][:]
            wavps=wavp[-3][:]
                                                           
            a2.plot(wavpx,wavps+i,'o',markersize=1,label=str(nlev),color=kolor)
            a0.plot(wavpx,wavpy+i,'o',markersize=1,label=str(nlev),color=kolor)
                                    
            L2=int(wavpx.shape[0]*0.5)
            H=np.abs(np.fft.fft(wavpy))[0:L2+1]
            
            lenH=len(H)
            #tit='name='+name+', level='+str(nlev)+',  length='+str(lenH)            
            a1.plot(np.linspace(0,0.5,lenH),np.sqrt(H),label=str(nlev),color=kolor)
            
            
            L=np.abs(np.fft.fft(wavps))[0:L2+1]                       
            a3.plot(np.linspace(0,0.5,lenH),np.sqrt(L),label=str(nlev),color=kolor)

        
        a0.set_axis_off()
        a2.set_axis_off()
        #a0.spines['top'].set_visible(False)
        #a0.spines['right'].set_visible(False)
        #a0.legend(fontsize=8,loc='upper right').set_visible(True)
        a2.set_title('scaling functions')
        a0.set_title('wavelet functions')
        
        
        a1.spines['top'].set_visible(False)
        a1.spines['right'].set_visible(False)
        a1.set_xlim([2**(-15),0.9])
        a1.legend(fontsize=8).set_visible(True)
        a1.set_xlabel('Normalized frequency')
        a1.set_ylabel('Gain')
        
        
        a3.spines['top'].set_visible(False)
        a3.spines['right'].set_visible(False)
        a3.set_xlim([2**(-15),0.9])
        a3.legend(fontsize=8).set_visible(True)
        a3.set_xlabel('Normalized frequency')
        a3.set_ylabel('Gain')
                
        
        fig.suptitle(self.WletFamily.get())
        fig.canvas.draw()
        
        
   



        
    def grid(self):
        self.__plt__.grid()
    def legend(self):
        self.__plt__.legend()
    def pltTitle(self,ptitle='title'):
        self.__plt__.set_title(ptitle)   
        
    def eWlFamilyChanged(self,event):
        evalue=event.widget.get().split()        
        wlcollection=pywt.wavelist(evalue[-1])        
        self.comboBox['Wlname']['values']=wlcollection
        self.WletType.set(wlcollection[3]);        
        
        
        	# placing the toolbar on the Tkinter window 
        	#canvas.get_tk_widget().pack()    
        	#canvas.get_tk_widget().grid()
