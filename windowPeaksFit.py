

from tkinter import ttk, Menu
import tkinter as tk
import tkinter.font as tkFont
#from tkinter import messagebox
from tkinter import filedialog as fd

import numpy as np
import scipy as scp
import pandas as pd
from datetime import datetime
import copy

import initsetRW as ini

import labelEdit as le
import scrolledText as stext
import dataProcessing as dpr
import windowPlotFitResults as wpfr


from fitFunctions import *
import xraylines as xr

#------------------------------------------------------------------------------
class CheckbuttonPicture(ttk.Frame):
    
    button=None
    picture=None
    
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        
        self.button=ttk.Checkbutton(self, width=75)
        self.button.pack(anchor='w')

#------------------------------------------------------------------------------    
# Based on
#   https://web.archive.org/web/20170514022131id_/http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=False)
        
        h=ttk.Scrollbar(self, orient='horizontal')
        h.pack(side=tk.BOTTOM, fill='x',expand=False)
        
        #hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        #hscrollbar.pack(fill=tk.X, side=tk.BOTTOM, expand=False)
        
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set,
                           xscrollcommand=h.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)        
        
        vscrollbar.config(command=canvas.yview)        
        h.config(command=canvas.xview)
        #hscrollbar.config(command=canvas.xview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,anchor=tk. NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)        
        
    #-----------------------------------------    




#------------------------------------------------------------------------------



class peaksFitWindow(tk.Toplevel):
    dataInfo={}
    data2D=None
    peaks=None
    __defFont__=None
    __titFont__=None
    __frwidth__=700
    __frheight__=600
    
    __saveFitData__=''
    #-----------------------------------------
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent,*args,**kwargs)
        
        self.initMenu()    
        self.geometry(str(self.__frwidth__)+'x'+str(self.__frheight__))
        #self.title(" script: "+__name__)
                
        self.iniDir=tk.StringVar()    
        self.iniDir.set(ini.getValue('default','inpath').rsplit('/',1)[0]) 
        
        fontName=ini.getValue('font.default', 'name')
        fontSize=ini.getValue('font.default', 'size')
        fontWeight=ini.getValue('font.default','weight')
        self.__defFont__=tkFont.Font(family=fontName,size=fontSize,weight=fontWeight)
        
        fontName=ini.getValue('font.title', 'name')
        fontSize=ini.getValue('font.title', 'size')
        fontWeight=ini.getValue('font.title','weight')
        self.__titFont__=tkFont.Font(family=fontName,size=fontSize,weight=fontWeight)
        
        
        #bgcolor='cornsilk'        
        self.fr=tk.LabelFrame(self,font=self.__titFont__,height=240,width=self.__frwidth__-20)
        
        self.fr.pack(fill='x')
        self.fr.pack_propagate(False)
        self.fr.grid_propagate(False)
        
        pName='Peaks'
        xName='X'
        yName='Y'
        tlabel=f' {pName:^3}     {xName:>20}     {yName:>20}'
        Lframe=ttk.Label(self.fr,text=tlabel, font=self.__titFont__,justify='left');
        Lframe.pack(side=tk.TOP,anchor='w')
        
        
        bgcolor='bisque3'
        self.frb=tk.LabelFrame(self,bg=bgcolor,text='Initial fitting parameters',font=self.__titFont__,height=150)
        
        self.frb.pack(fill='x')
        self.frb.pack_propagate(False)
        self.frb.grid_propagate(False)
        #self.frb.pack_propagate(False)
        #self.frb.grid_propagate(False)
        
        #----------------------------------
        self.peakSize=tk.IntVar()
        self.peakSize.set(15)
        
        inarg={'font': self.__defFont__,
               'width': 10,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }
        
        ehigh=le.LabelEdit(self.frb,label='Peak: neighbors  ',
                         input_class=ttk.Entry,
                         input_args=inarg,
                         input_var=self.peakSize,
                         label_args=lbarg)
        
        ehigh.grid(row=0,column=0,columnspan=2,padx=10,pady=10)
                
        
        fitFuncTypes=['3-prms gauss','3-prms lorentz','4-prms gauss','4-prms lorentz']
        self.fitFunctionType=tk.StringVar()
        self.fitFunctionType.set(fitFuncTypes[0])
        inarg={'font': self.__defFont__,
               'width': 20,
               'justify': 'center',
               'values': fitFuncTypes
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }

        
        lecm=le.LabelEdit(self.frb,label='name ',
                          input_class=ttk.Combobox,input_args=inarg,
                          input_var=self.fitFunctionType,
                          label_args=lbarg)
        lecm.grid(row=0,column=2,columnspan=2,padx=10,pady=10)
        
        #self.comboBox['fitfunc']=lecm.input
        
        '''
        #---------- A B C D -------------        
        self.iniABCD=tk.StringVar()
        #if self.TEST:
        #    self.iniABCD.set("d, d, d, 0")
        #else:
        self.iniABCD.set(" d, 1e-3, d, 0") 
        '''
        
        
        self.chBoxPixieOnOff=tk.IntVar()
        self.chBoxPixieOnOff.set(0)
        
        s=ttk.Style()
        s.configure('ChBoxPixie.TCheckbutton',
                    background=bgcolor,
                    font=self.__defFont__)
        
        chbox=ttk.Checkbutton(self.frb,text="show Pixie lines",
                              style='ChBoxPixie.TCheckbutton',variable=self.chBoxPixieOnOff,
                              )
        chbox.grid(row=1,column=0,padx=10,pady=10)
        
        
        self.Etol=tk.DoubleVar()
        self.Etol.set(0.05)
        inarg={'font': self.__defFont__, 
               'width': 5,
               'justify': 'center',}
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'}
        
        #  lecmFm.input.bind("<<ComboboxSelected>>",self.eWlFamilyChanged)
        lf=le.LabelEdit(self.frb,label='tol.',
                        input_class=ttk.Entry,
                        input_var=self.Etol,
                        input_args=inarg,
                        label_args=lbarg)
        lf.grid(row=1,column=1,columnspan=1,padx=10,pady=10)
        
            
        inarg={'font': self.__defFont__,
               'width': 20,
               'justify': 'center',
               }
        lbarg={'font': self.__defFont__ , 
               'background' : bgcolor,
               'justify': 'left'
               }

        s=ttk.Style()
        s.configure('Bfit.TButton',
                    font=self.__defFont__)
        
        Bfitpeaks=ttk.Button(self.frb,text="fit peaks",style='Bfit.TButton',command=self.fitPeaks)
        Bfitpeaks.grid(row=1,column=3,columnspan=2,padx=10,pady=10,sticky='ew')
        
        bgcolor='lime'
        fresults=tk.LabelFrame(self,bg=bgcolor,text='fitting results',font=self.__titFont__,height=240)
        fresults.pack(fill='x')
        
        h=stext.scrolledText(fresults)
        h.pack(fill=tk.BOTH)
        self.tInfo=h.text
        
        
        
        self.tInfo=h.text

        #----------------------------------
        
        

    
    def initMenu(self):               
        menubar = Menu(self)
        

        fileMenu = Menu(menubar)#font=("",14)
        #fileMenu.add_command(label="Open")
        fileMenu.add_command(label="Save",command=self.dataSave)
        fileMenu.add_command(label="Exit")
        
        optMenu =Menu(menubar)
        optMenu.add_command(label="data  to  clipboard",command=self.dataToClipboard)
        optMenu.add_command(label="data from clipboard",command=self.dataFromClipboard)
        
        
        helpMenu=Menu(menubar)
        helpMenu.add_command(label="Authors/Credits")
        
                
        menubar.add_cascade(label="File", menu=fileMenu)      
        menubar.add_cascade(label="Options",menu=optMenu)        
        menubar.add_cascade(label="Help",menu=helpMenu)        
        self.config(menu=menubar)  
        
    #-----------------------------------------

    def showPeaksList(self):        

        
        peakFrame=tk.LabelFrame(self.fr,font=self.__titFont__,height=170,width=self.__frwidth__-20)        
        peakFrame.pack(fill='x')
        peakFrame.pack_propagate(False)
        peakFrame.grid_propagate(False)
        
        vsf=VerticalScrolledFrame(peakFrame)        
        vsf.pack(fill='x')

        self.chbox = []                
        x=self.data2D[:,0]
        y=self.data2D[:,1]
        
        self.chboxOnOff=[]*self.peaks.size
        
        
        chboxStyle=ttk.Style()
        chboxStyle.configure('ChBox.TCheckbutton',
                    font=self.__titFont__)
        
        
        for ipeak, peak in enumerate(self.peaks):
            xpos,ypos=x[peak],y[peak]            
            tlabel=f' {ipeak+1:^3d}     {xpos:>20.2f}     {ypos:>20.2f}'
            #print(tlabel)
            
            chBoxOnOff=tk.IntVar()
            chBoxOnOff.set(1)
            
            chbox=ttk.Checkbutton(vsf.interior,text=tlabel,
                                  style='ChBox.TCheckbutton',variable=chBoxOnOff,
                                  width=75)
            chbox.pack(anchor='w')
            #self.chbox.append(chbox)
            self.chboxOnOff.append(chBoxOnOff)
            
        '''    
        buttonStyleAdd=ttk.Style()
        buttonStyleAdd.configure('ButtonAdd.TButton',
                              background='greenyellow',
                              font=self.__titFont__,height=50)
          
        Baddpeak=ttk.Button(self.fr,text='+ peak',style='ButtonAdd.TButton')
        Baddpeak.pack(side=tk.LEFT)
        
        buttonStyleDel=ttk.Style()
        buttonStyleDel.configure('ButtonDel.TButton',
                              background='lightcoral',
                              font=self.__titFont__,height=50)
          
        Bdelpeak=ttk.Button(self.fr,text='- peak',style='ButtonDel.TButton')
        Bdelpeak.pack(side=tk.LEFT)
        '''
            
    
    #-----------------------------------------
    
    def fitPeaks(self):
        
        #numFormat={'float_kind':lambda x: " %7.2f " % x}     
        numFormatB={'float_kind':lambda x: " %7.3e " % x}  
        
        saveFitData=''
        
        self.tInfo.delete(1.0,tk.END)
        self.tInfo.insert(tk.END,"Results:\n")
                
        fitName=self.fitFunctionType.get()

        if fitName=='4-prms lorentz':
            fitfunc=lorentzABCD()
            fx=lorentzABCD()                      
        else:
            if fitName=='4-prms gauss':
                fitfunc=gaussABCD()
                fx=gaussABCD()                
            else:
                if fitName=='3-prms gauss':
                    fitfunc=gaussABC()
                    fx=gaussABC()
                else:
                    if fitName=='3-prms lorentz':
                        fitfunc=lorentzABC()
                        fx=lorentzABC()
                    
            
        saveFitData=fitfunc.getName()                
        nOfParams=fitfunc.getNumberOfPrms()
                
        x,y=self.data2D[:,0],self.data2D[:,1]
        ifrom,ito=0,x.size
        
                      
        selPeaks=np.array([])
        for ich,chbox in enumerate(self.chboxOnOff):
            if chbox.get():
                selPeaks=np.append(selPeaks,self.peaks[ich])

        peakSize=self.peakSize.get()                        
        peakRanges=dpr.definePeakRanges(selPeaks, peakSize, ifrom, ito)
            
        
        child=wpfr.plotWindow(self)
        plt=child.__plt__
        plt.plot(x,y,'og',markersize=1.5)      
        
        pxlist=[]*len(selPeaks)
                        
        for rec in peakRanges:
                        
            #print('----------------------------')
            #print(rec)
            #initial peak positions
            iniPeakPos=np.array(rec[1])
            nOfpeaks=len(iniPeakPos)
            dfrom,dto=int(rec[2][0]),int(rec[2][1])   
            xdata=x[dfrom:dto]
            ydata=y[dfrom:dto]
            iniFWHM=(xdata[-1]-xdata[0])/nOfpeaks
            iniPeakHeights=np.take(y,iniPeakPos.astype(int))
            #print('iniPeaksHeights :', iniPeakHeights)
                        
            a=np.ndarray((nOfpeaks),float)
            b=np.ndarray((nOfpeaks),float)
            c=np.ndarray((nOfpeaks),float)                        
                        
            log='* '
            logHeader='  '  
            saveFitData+='\nft: '+str(rec[2][0])+' '+str(rec[2][1])
            
            if nOfParams==4:            
                                                           
                for ipeak, peak in enumerate(rec[1]):
                    dind=int(peak)
                    a[ipeak]=fitfunc.Mfwhm2a(iniPeakHeights[ipeak],iniFWHM)
                    b[ipeak]=fitfunc.fwhm2b(iniFWHM)
                    c[ipeak]=x[dind]
                    logHeader+=f'{x[dind]:6.1f} ' 
                                        
                d=np.zeros((nOfpeaks),float)                                  
                iniParams=[a,b,c,d]                                               
            else:                
                if nOfParams==3:
                    for ipeak, peak in enumerate(rec[1]):
                        dind=int(peak)
                        a[ipeak]=fitfunc.Mfwhm2a(iniPeakHeights[ipeak],iniFWHM)
                        b[ipeak]=fitfunc.fwhm2b(iniFWHM)
                        c[ipeak]=x[dind]
                        logHeader+=f'{x[dind]:6.1f} ' 
                                                      
                    iniParams=[a,b,c]
                else:
                    print('not implemented')
                    return
                               
            fitfunc.setInitial(*iniParams)
            fitfunc.X(xdata)
            iniParamsStr=[np.array2string(x) for x in iniParams]
            saveFitData+='  in='+str(iniParamsStr)
                                    
            fitboundsL,fitboundsR=fitfunc.getBounds()
            fitboundsL=np.tile(fitboundsL.reshape(-1,1),(1,nOfpeaks)).reshape(1,nOfpeaks*fitfunc.getNumberOfPrms())[0]
            fitboundsR=np.tile(fitboundsR.reshape(-1,1),(1,nOfpeaks)).reshape(1,nOfpeaks*fitfunc.getNumberOfPrms())[0]
            fitbounds=(fitboundsL,fitboundsR)
                        
            log+=fitfunc.getName()+logHeader
            #fitfunc.getBounds()       
            saveFitData+='  out='
            
            try:                
                #------------------------------------------------------
                
                pop,cov=scp.optimize.curve_fit(fitfunc, xdata,ydata,
                                               p0=np.zeros((nOfParams*nOfpeaks,),float),
                                               bounds=fitbounds)                
                               
                #------------- show RESULTS -------------------------
                rpop=   np.reshape(pop,      (nOfParams,-1))                                                
                fitPrms=np.reshape(iniParams,(nOfParams,-1))
                fitFinal=(fitPrms+rpop)
                saveFitData+='   '+str([np.array2string(x) for x in fitFinal])
                #print('final rpop ',rpop)
                #print('final fit+rpop',fitFinal)
                
                
                for iprm, prm in enumerate(fitFinal):
                    letter=' '+chr(iprm+97)+'='
                    sprm=np.array2string(prm,formatter=numFormatB)
                    log+=letter+sprm 
                log+='\n'
                
                fx.setInitial(*fitFinal)
                yfitted=fx(xdata,np.zeros((nOfParams*nOfpeaks,),float))                
                resY=np.average((ydata-yfitted)**2)**0.5
                
                
                #--------------------------------------------------------------
                
                plt.plot(xdata,yfitted,'-b',linewidth=2)           
                fwhm=fx.getFWHM((fitFinal[1]))
                log+='R='+f'{resY:8.6f}'+',   FWHM '+str(fwhm.reshape(1,-1))+'\n'  
                saveFitData+=' R='+f'{resY:8.6f}'
                                                                                  
                #-------------                
                fx.__X__=None
                cn=fitFinal[2]
                ycn=fx(cn,np.zeros(nOfParams*nOfpeaks))
                #print('  cn  , ycn ',cn,ycn)
                plt.plot(cn,ycn,'^r')           
                
                if self.chBoxPixieOnOff.get():
                    tol=self.Etol.get()
                    listOfLines=[]
                    saveFitData+=' pix: '
                    
                    for xElemName in xr.xray.keys():
                        for xElemLine in xr.xray[xElemName]:
                            xpixie=xr.xray[xElemName][xElemLine][0]
                            xpixP=xpixie+tol
                            xpixM=xpixie-tol
                            icn=np.where( (cn>xpixM) & (cn<xpixP))
                            
                            if len(icn[0]):
                                mlist=set()
                                mlistL=len(mlist)
                                for v in icn:    
                                                                        
                                    fx.__X__=None
                                    pX,pY=cn[v],fx(cn[v],np.zeros(nOfParams*nOfpeaks))
                                                                                              
                                    plt.plot(pX,pY,'|k',markersize=20)
                                                                                                            
                                    # draw/save the unique values only
                                    mlist.add(pX[0])
                                    ll=len(mlist)
                                    if ll>mlistL:                                        
                                        mlistL=ll                                                                                
                                        dup=-1
                                        for itr,listE in enumerate(listOfLines):
                                            if listE[0]==pX[0]:
                                                dup=itr
                                                break
                                        
                                        lineInfo=[pX[0],pY[0],xElemName,xElemLine,xpixie]
                                        
                                        if dup==-1:                                                
                                            listOfLines.append(lineInfo)
                                        else:                                            
                                            listOfLines[dup].extend(lineInfo)
                                            
                    #draw lines          
                    if len(listOfLines):                                                     
                        for line in listOfLines:
                            lenLine=len(line)
                            nOfItems=int(lenLine/5)
                            itext='   '
                            
                            saveFitData+=' '+str(nOfItems)
                            for i in range(0,nOfItems):
                                colNum=i*5
                                itext+=' '+line[colNum+2]+': '+line[colNum+3]+', '
                                
                            #itext=itext[]
                            plt.text(line[0],line[1],itext[:-2],fontsize=8,color='tab:orange',
                                     rotation='vertical',verticalalignment='bottom',horizontalalignment='right',)
                            saveFitData+=' '+str(line[0])+'  '+str(line[1])+'  '+itext[:-2]
                    else:
                        saveFitData+=' none'
                    
                    
                        


                #-------------------------------
                if nOfpeaks>1:                    
                    prms=fitFinal.T                    
                    if prms.shape[1]==nOfParams:                    
                        for iprm, prm in enumerate(prms):
                            fx.__X__=None
                            fx.setInitial(*prm)
                            plt.plot(xdata,fx(xdata,np.zeros(nOfParams)),'--b',linewidth=1)                                                                                        
                                
                            
                #plt.set_title('fitting with: '+fx.getName())
                
                self.tInfo.insert(tk.END,log)
                #--------------------------------------------------------

                fitfunc.__X__=None
                fx.__X__=None                
                                
                #--------------------------------------------------------
                                
            except Exception as elog:
                print('EXCEPTION ',elog)
                saveFitData+=' Exception: '+str(elog)
                self.tInfo.insert(tk.END,"Exception :"+str(elog))
                fitfunc.__X__=None
                fx.__X__=None
            
            
            self.__saveFitData__=copy.copy(saveFitData)
                                    
        
        
    #-----------------------------------------    
    
    def dataSave(self):
        filetypes = ( ('results','*.fit'),('All files', '*.*') )
        outputFileName=fd.asksaveasfilename(title='Save a file',
                              initialdir=self.iniDir,
                              filetypes=filetypes)
         
        if outputFileName=='':
            print('INFO: file name not given, fitting result will be not saved')
            

        fid=open(outputFileName,'w')
        fid.write('#ver: 0 \n')
        fid.write('#date: '+datetime.today().strftime('%Y-%m-%d')+'\n')
        fid.write('PROCESSING PARAMETERS\n')
        fid.write(str(self.dataInfo))        
        fid.write('\nFITTING IN/OUT PARAMETERS\n')
        fid.write(self.__saveFitData__)
        fid.write('\nINPUT DATA\n')
        for i,v in enumerate(self.data2D):
            vx,vy=v[0],v[1]
            vstr=f'{i:6d} {vx:10.6f} {vy:10.6f}\n'
            fid.write(vstr)
        
        fid.close()
        
        

           
        #self.data2D.savetxt(outputFileName)
        
    #-----------------------------------------    
                                    
    def dataToClipboard(self):
        df = pd.DataFrame(self.data2D)
        df.to_clipboard(sep='\t') 
        
    def dataFromClipboard(self):
        df=pd.read_clipboard().to_numpy()
        
        plt=self.__plt__
        plt.plot(df[:,0],df[:,1],'.k',markersize=0.5,label='data from clipboard')
        
        self.__fig__.canvas.draw()        


import findFitPeaks as ffp

class MyApp(tk.Tk):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            self.title("tloszum remover "+__name__)
            self.geometry("630x550+1000+250")
            self.resizable(True,True)
            
            
            MF=ffp.findFitWindow(self)       
            MF.grid()
                       
#------------------------------------------------------------------------------

if __name__=='__main__':    
    
    #build if not exists
    #ini.setDefaultIni()
          
    app=MyApp()
    app.mainloop()
