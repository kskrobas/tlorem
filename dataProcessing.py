
import numpy as np
import re
from scipy.signal import savgol_filter




def readFile(fileName):
        
    if fileName=='':
        print('no file name given')
        return None
    
    data2D=None                        
    if re.search('\.dat$',fileName):
        data2D=np.loadtxt(fileName)
    else:
        if re.search('\.npy',fileName):
            data2D=np.load(fileName).T
        else:
            if re.search('\.spe',fileName):
                fin=open(fileName,'r')
                for _ in range(0,7): fin.readline()
                
                f,t=fin.readline().split()
                data2D=np.ndarray((int(t)-int(f),2),float)
                fpos=0

                for line in fin:
                    splitLine=line.split()
                    for v in splitLine:
                        data2D[fpos,0]=fpos
                        data2D[fpos,1]=float(v)
                        fpos+=1

                fin.close()                
            else: 
                if re.search('\.diff',fileName):
                    data2D=np.loadtxt(fileName)[:,1:5:2]
                else:
                    print('unknown extension')
                    return None
            
    return data2D
            
          
          
          
def selectData(data2D,fts=''):
    fts_split=fts.split(':')
    
    if fts_split[0]=='':  fts_split[0]='0'
    if fts_split[1]=='':  fts_split[1]='-1'
    
    f=int(fts_split[0])
    t=int(fts_split[1])
    
    if len(fts_split)==3:
        s=int(fts_split[2])
        return data2D[f:s:t]
    
    return data2D[f:t]            
    
    
    
    
def normData(data2D: np.ndarray, ntype='None'):
    if ntype=='sqrt':
        indZero=np.where(data2D[:,1]<0)
        data2D[indZero,1]=0
        data2D[:,1]=data2D[:,1]**0.5
    else:
        if ntype=='log10':
            indOne=np.where(data2D[:,1]<1)
            data2D[indOne,1]=1
            data2D[:,1]=np.log10(data2D[:,1])
            
    return data2D
    
    
    
    
def filteringData(data2D: np.ndarray, ftype,rank,size):                
    
    if ftype == 'Savitzky-Golay':        
        data2D[:,1]=savgol_filter(data2D[:,1], size, rank)                        
    else:
        if ftype =='moving average':
            kernel=np.ones((size,),float)/size
            data2D[:,1]=np.convolve(kernel, data2D[:,1],'same')
            
    return data2D
                
                
                
                
def definePeakRanges(peakIndices: np.ndarray, peakMinSpace,ifrom,ito):
    indSpace=peakMinSpace
    indSpaceDouble=indSpace*2
    ind=peakIndices
        
    lpr=[]    
    i,k=0,0
    #{
    while i<ind.shape[0]:        
        lpeaks=[]    
        
        pfirst=ind[i]
        peakIndMin=pfirst-indSpace            
        fm=peakIndMin if peakIndMin>=ifrom else ifrom            
        
        #-------------------------------
        #### testind distance to the next peak            
        #-------------------------------
        
        lpeaks.append(pfirst)    
        i+=1
            
        #{
        while True:
                                    
            if i==ind.shape[0]:
                peakIndMax=pfirst+indSpace            
                to=peakIndMax if peakIndMax<ito else ito                                              
                lprloc=[k,lpeaks,[fm,to]]            
                                    
                k+=1
                break
            
            psec=ind[i]           
                            
            #{
            if psec-pfirst>indSpaceDouble:            
                peakIndMax=pfirst+indSpace            
                to=peakIndMax if peakIndMax<ito else ito
                            
                fmto=[fm,to]                 
                lprloc=[k,lpeaks,fmto]
                            
                k+=1
                break
            else:                          
                pfirst=psec             
                lpeaks.append(psec)  
                i+=1
            #} if                                                  
        #} while True        
        lpr.append(lprloc)
    #}   while  
    
    return lpr
        
    
