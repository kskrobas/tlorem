#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 12:05:47 2024

@author: fizyk
"""

import numpy as np
import scipy as scp
import matplotlib.pyplot as plt

#------------------------------------------------------------------------------

def fgauss(x,a,b,c,d):
    return a*np.exp(-b*(x-c)**2)+d

#------------------------------------------------------------------------------

class cfgauss:
    def __init__(self, pa,pb,pc,pd):
        self.a=pa
        self.b=pb
        self.c=pc
        self.d=pd
        
    def __call__(self,x,a,b,c,d):
        return (a+self.a)*np.exp(-(b+self.b)*(x-c-self.c)**2)+d+self.d
#------------------------------------------------------------------------------

class cfgaussMulti:
    def __init__(self,
                 pa: np.ndarray,
                 pb: np.ndarray,
                 pc: np.ndarray,
                 pd: np.ndarray):
        
        self.a,self.b,self.c,self.d=pa,pb,pc,pd
        self.size=pa.size
      
    '''     
    def __call__(self,x,a,b,c,d):
        A=self.a+a
        B=self.b+b
        C=self.c+c
        D=self.d+d
        #X=np.ones((self.size,x.size),float)*x        
        X=np.tile(x,(self.size,1))        
        arg=(X-C[:,np.newaxis])*B[:,np.newaxis]
        ya=np.exp(-arg**2)*A[:,np.newaxis]+D[:,np.newaxis]
        
        return np.sum(ya,axis=0)
    '''
    
    def __call__(self,x,*prms):
        prsh=np.reshape(prms, (4,-1))
        A=self.a+prsh[0,:]
        B=self.b+prsh[1,:]
        C=self.c+prsh[2,:]
        D=self.d+prsh[3,:]
        
        X=np.tile(x,(self.size,1))        
        arg=(X-C[:,np.newaxis])*B[:,np.newaxis]
        ya=np.exp(-arg**2)*A[:,np.newaxis]+D[:,np.newaxis]
        
        return np.sum(ya,axis=0)
        
        
            

#------------------------------------------------------------------------------


x=np.linspace(0,10,201)

pa=np.array([3.5,3.25,2.5])
pb=np.array([2,1,0.5])
pc=np.array([3.25, 4.5,7.5])

pd=np.array([0,0,0])

mfunc=cfgaussMulti(pa, pb, pc, pd)

yrand=mfunc(x,np.zeros((12,),float))+0.00625*np.random.default_rng().normal(size=x.size)

pao=np.array([4,3,2])
pbo=np.array([1.5,1.5,1.5])
pco=np.array([3.7, 4.9,7.6])
ffunc=cfgaussMulti(pa, pbo, pco, pd)

pop,cov=scp.optimize.curve_fit(ffunc, x,yrand,p0=np.zeros((12,),float),bounds=(-1,1))

#plt.plot(x,yini,'--r',linewidth=3)
plt.plot(x,ffunc(x,*pop),'-b',linewidth=2)
plt.plot(x,yrand,'.k')

rpop=np.reshape(pop,(4,-1))

print('results of fitting \n', np.array2string(rpop,formatter={'float_kind':lambda x: " %.3f" % x}))

'''
inivec=np.array([0.975,1.25,4.95,0])

ifunc=cfgauss(*inivec)

x=np.linspace(0,10,101)
yini=fgauss(x,1,1,5,0)
yrand=yini+0.125*np.random.default_rng().normal(size=x.size)


pop,cov=scp.optimize.curve_fit(ifunc, x,yrand,p0=[0.5, 1, 0.125, 0.125],bounds=(-1,1))

plt.plot(x,yini,'--r',linewidth=3)
plt.plot(x,ifunc(x,*pop),'-b',linewidth=2)
plt.plot(x,yrand,'.k')

rpop=pop+inivec
#print('results : ',np.array2string(rpop,precision=3,prefix='....',separator='----',suppress_small=True))
print('results of fitting ', np.array2string(rpop,formatter={'float_kind':lambda x: " %.3f " % x}))
'''

'''
pop,pco=scp.optimize.curve_fit(fgauss, x,yrand,p0=[0.75,1.25,4.75,0.125],bounds=([0.5, 0.5,4,0],[2,2,6,1]))

plt.plot(x,fgauss(x,*pop),'-b',linewidth=2)
plt.plot(x,yrand,'.k')
'''


