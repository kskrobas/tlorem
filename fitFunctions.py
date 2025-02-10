


import abc
import numpy as np
from numpy import ndarray as array

#------------------------------------------------------------------------------
class fitFunction(abc.ABC):
    
    __X__=None
    __nOfpms__=0
    __size__=0
    __name__=''
    __p0__=None
    __bounds__=None    
    __ax__,__bx__=0,0
    __ay__,__by__=0,0
                
    
    def getName(self) ->str:
        return self.__name__
    
    
    
    def X(self,x: array):
        self.__X__=np.tile(x,(self.__size__,1))
        return self.__X__    
    
    
    
    @abc.abstractmethod
    def setInitial(self,*args :array) ->str:
        raise NotImplementedError()    
        
    
    # Xnorm = ax*X + bx ,  Ynorm= ay*Y + by  
    def normalizeInput(self, X :array, Xrange :array(2),
                             Y :array, Yrange :array(2) ):
             
        xmin,ymin=np.min(X),np.min(Y)
        xmax,ymax=np.max(X),np.max(Y)
        
        xwidth=xmax-xmin
        ywidth=ymax-ymin
        
        xrangeWidth=Xrange[1]-Xrange[0]
        yrangeWidth=Yrange[1]-Yrange[0]
        
        ax,ay=xrangeWidth/xwidth,yrangeWidth/ywidth
        bx,by=Xrange[0]-ax*xmin,Yrange[0]-ay*ymin
        
        self.__ax__,self.__ay__,self.__bx__,self.__by__=ax,ay,bx,by
        
        Xn=ax*X+bx
        Yn=ay*Y+by
        
        print('ax, ay, bx ,by ',ax,ay,bx,by)
        
        return Xn,Yn
        
    
    def xcoordConvert(self,X):
        return X*self.__ax__+self.__bx__
    
    def ycoordConver(self,Y):
        return Y*self.__ay__+self.__by__
            
    def getNumberOfPrms(self) :
        return self.__nOfpms__
    
    @abc.abstractmethod
    def getInitial(self) :
        raise NotImplementedError()   
        
    @abc.abstractmethod
    def getFWHM(self) :
        raise NotImplementedError()   
        
    @abc.abstractmethod
    def fwhm2b(self,fwhm) :
        raise NotImplementedError()    
        
    @abc.abstractmethod
    def Mfwhm2a(self,M,fwhm) :
        raise NotImplementedError() 
        
    @abc.abstractmethod
    def getP0(self) :
        raise NotImplementedError()
    
    @abc.abstractmethod
    def getBounds(self) :
        raise NotImplementedError()
                
    @abc.abstractmethod
    def __init__(self,*args :np.ndarray) ->None:
        raise NotImplementedError()
     
    @abc.abstractmethod    
    def __call__(self,x,*prms :np.ndarray)->float:
        raise NotImplementedError()

#------------------------------------------------------------------------------
class gaussABCD(fitFunction):
    
    def __init__(self):        
        self.__name__='4-prms gaussian func. a*exp(-b*(x-c))+d'  
        self.__nOfpms__=4
        
    # a*exp(-b(x-c)^2)+d
    def __call__(self,x, *prms :np.ndarray):
        prsh=np.reshape(prms, (self.__nOfpms__,-1))
        A=np.abs(self.a+prsh[0,:])
        B=np.abs(self.b+prsh[1,:])
        C=self.c+prsh[2,:]
        D=self.d+prsh[3,:]                
        pX=self.__X__ if self.__X__ is not None else self.X(x)        
        arg=B[:,np.newaxis]*(pX-C[:,np.newaxis])**2
        
        exparg=np.exp(-arg)
        y=A[:,np.newaxis]*exparg+D[:,np.newaxis]
                
        return np.sum(y,axis=0)
            
    
    
    def setInitial(self,*args: np.ndarray):
        if len(args)!=4:
            print('ERROR: gaussABCD requires 4 input arguments, given ',len(args))
            return

        self.a,self.b,self.c,self.d=args[0],args[1],args[2],args[3]        
        self.__size__=self.a.size
        
         
                         
    def getInitial(self):
        return ([self.a,self.b,self.c,self.d])
    
    
    
    def getFWHM(self,b):
        return (np.log(16)/np.abs(b[:,np.newaxis]))**0.5
    
    def fwhm2b(self,fwhm) :
        return np.log(16)/fwhm**2
    
    def Mfwhm2a(self,M,fwhm) :
        return M
    
    def getP0(self) :
        return np.zeros(4)
    
  
    def getBounds(self) :
        pbounds=np.array([100,1,10,100])
        return (-pbounds,pbounds)
    

    
        
#------------------------------------------------------------------------------
class lorentzABCD(fitFunction):
    
    
    def __init__(self,*args :np.ndarray):        
        self.__nOfpms__=4
        self.__name__='4-prms lorentzian func.'
       
        
        
    def __call__(self,x, *prms :np.ndarray):
        prsh=np.reshape(prms, (self.__nOfpms__,-1))
        A=np.abs(self.a+prsh[0,:])
        B=self.b+prsh[1,:]
        C=self.c+prsh[2,:]
        D=self.d+prsh[3,:]                
        pX=self.__X__ if self.__X__ is not None else self.X(x)                        
        arg=(pX-C[:,np.newaxis])**2+B[:,np.newaxis]**2

        return np.sum(A[:,np.newaxis]/arg+D[:,np.newaxis],axis=0)
    
    
    
    
    def setInitial(self,*args: np.ndarray):
        if len(args)!=4:
            print('ERROR: lorentzABCD requires 4 input arguments, given ',len(args))
            return

        self.a,self.b,self.c,self.d=args[0],args[1],args[2],args[3]
        self.__size__=self.a.size
        
        
        
    def getInitial(self):
        return ([self.a,self.b,self.c,self.d])    



    def getFWHM(self,b):
        return 2*b[:,np.newaxis]
    
    def fwhm2b(self,fwhm) :
        return fwhm*0.5
    
    def Mfwhm2a(self,M,fwhm) :
        return 0.5*fwhm*M**0.5
    
    def getP0(self) :
        return np.zeros(4)    
    
    
    
    def getBounds(self) :
        pbounds=np.array([1e5,100,5,1e5])
        return (-pbounds,pbounds)
    

    
    
#------------------------------------------------------------------------------
class gaussABC(fitFunction):
    
    def __init__(self):        
        self.__name__='3-prms gaussian func. a*exp(-b*(x-c))'  
        self.__nOfpms__=3
        
        
    def __call__(self,x, *prms :np.ndarray):
        prsh=np.reshape(prms, (self.__nOfpms__,-1))
        A=np.abs(self.a+prsh[0,:])
        B=-np.abs(self.b+prsh[1,:])
        C=self.c+prsh[2,:]        
        pX=self.__X__ if self.__X__ is not None else self.X(x)        
        arg=B[:,np.newaxis]*(pX-C[:,np.newaxis])**2
                
        return np.sum(np.exp(arg)*A[:,np.newaxis],axis=0)
            
    
    
    def setInitial(self,*args: np.ndarray):
        if len(args)!=self.__nOfpms__:
            print('ERROR: gaussABCD requires 3 input arguments, given ',len(args))
            return

        self.a,self.b,self.c=args[0],args[1],args[2]
        self.__size__=self.a.size
        
         
                         
    def getInitial(self):
        return ([self.a,self.b,self.c])
    
    
    
    def getFWHM(self,b):
        return (np.log(16)/np.abs(b[:,np.newaxis]))**0.5
    
    
    def Mfwhm2a(self,M,fwhm) :
        return M
    
    def fwhm2b(self,fwhm) :
        return np.log(16)/fwhm**2
    
    
    def getP0(self) :
        return np.zeros(3)
    
    
    
    def getBounds(self) :
        pbounds=np.array([100,1,5])
        return (-pbounds,pbounds)
    

          
#------------------------------------------------------------------------------    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
class lorentzABC(fitFunction):
    
    
    def __init__(self,*args :np.ndarray):        
        self.__nOfpms__=3
        self.__name__='3-prms lorentzian func.'
       
        
        
    def __call__(self,x, *prms :np.ndarray):
        prsh=np.reshape(prms, (self.__nOfpms__,-1))
        A=np.abs(self.a+prsh[0,:]**2)
        B=self.b+prsh[1,:]
        C=self.c+prsh[2,:]
        
        pX=self.__X__ if self.__X__ is not None else self.X(x)                        
        arg=(pX-C[:,np.newaxis])**2+B[:,np.newaxis]**2

        return np.sum(A[:,np.newaxis]/arg,axis=0)    
    
    
    
    def setInitial(self,*args: np.ndarray):
        if len(args)!=3:
            print('ERROR: lorentzABCD requires 3 input arguments, given ',len(args))
            return

        self.a,self.b,self.c=args[0],args[1],args[2]
        self.__size__=self.a.size
        
        
        
    def getInitial(self):
        return ([self.a,self.b,self.c])    


    def getFWHM(self,b):
        return 2*b[:,np.newaxis]
    
    def fwhm2b(self,fwhm) :
        return fwhm*0.5
    
    def Mfwhm2a(self,M,fwhm) :
        return 0.5*fwhm*M**0.5
    
    def getP0(self) :
        return np.zeros(4)            
    
    def getBounds(self) :
        pbounds=np.array([1e5,1e3,2])
        return (-pbounds,pbounds)

