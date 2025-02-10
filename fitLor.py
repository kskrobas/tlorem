#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:38:26 2024

@author: fizyk
"""


from fitFunctions import *
import numpy as np
import matplotlib.pyplot as plt

import scipy as scp

#------------------------------------------------------------------------------
#ind=np.arange(415,545,1,dtype=int)
#ind=np.arange(687,747,1,dtype=int)
ind=np.arange(430,617,1,dtype=int)
datain=np.loadtxt('../inputData/wawa.out')
x,y=datain[ind,0],datain[ind,3]

#xnorm,ynorm=fitFunction().normalizeInput(x, np.array([0,2]), y, np.array([0,1]))

bi=np.log(16)/1.5**2
a=np.array([1.22,0.63])
b=np.array([bi,bi])
c=np.array([1,3])
d=np.array([0,0])
fitFunc=gaussABCD()
fitFunc.setInitial(a,b,c,d)
xnorm,ynorm=fitFunc.normalizeInput(x, np.array([0,4]), y, np.array([0,1]))

#y=fitFunc(xnorm,a,b,c,d)

'''
M=86
FWHM=27.35
a=np.array([M*FWHM**2])
b=np.array([FWHM])
c=np.array([815])
d=np.array([10])
'''


'''


print('ini ',M,FWHM,a,b,c)
#fitFunc=gaussABCD()
fitFunc=lorentzABCD()
fitFunc.setInitial(a,b,c,d)
'''
#plt.plot(x,fitFunc(x,np.zeros(4)))


bb=np.array([100,100,10,10,10,10,10,10])
#pop,cov,infod,mesg,ier=scp.optimize.curve_fit(fitFunc, xnorm,ynorm,p0=np.zeros(4),full_output=True)
pop,cov=scp.optimize.curve_fit(fitFunc, xnorm,ynorm,p0=np.zeros(8),bounds=(-bb,bb))
rpop=np.reshape(pop,(4,-1))
fita=a+rpop[0,:]
fitb=b+rpop[1,:]
fitc=c+rpop[2,:]
fitd=d+rpop[3,:]



print(fitFunc.getName())
print('ini ',fitFunc.getInitial())
print('pop ',pop)
print('abs(pop)-abs(ini)\n',np.abs(rpop)-np.abs(fitFunc.getInitial()))
print('fit: a , b, c, d', fita,fitb,fitc,fitd)
#,'  FWHM=', fitFunc.getFWHM(fitb))
#print(" M=",fita)

plt.figure(figsize=(12,8),dpi=150)
plt.subplot(211)
yfitted=fitFunc(xnorm,*pop)
resY=np.average((ynorm-yfitted)**2)**0.5
print('resY: ',resY)

plt.plot(xnorm,ynorm,'.k',xnorm,yfitted,'-r')
plt.title('fitting: '+fitFunc.getName())
plt.grid()

rvalues=fitFunc.getUnnormedInputParams(fita,fitb,fitc,fitd)
print('rvalues : ',*rvalues)

'''
for rvalue in fitFunc.getUnnormedInputParams(fita,fitb,fitc,fitd):
    print(rvalue)
'''

#print(fitFunc.__ay__,fitFunc.__by__,fitFunc.__ax__,fitFunc.__bx__)

plt.subplot(212)
funcPlot=gaussABCD()
funcPlot.setInitial(*rvalues)
yfitted=funcPlot(x,np.zeros(8))

resY=np.average((ynorm-yfitted)**2)**0.5
print('resY: ',resY)

plt.plot(x,y,'.b',x,yfitted,'-g')
plt.title('fitting: '+fitFunc.getName())
plt.grid()

'''
plt.plot(xnorm,ynorm,'.k',xnorm,fitFunc(xnorm,*pop),'-r')
plt.title('fitting: '+fitFunc.getName())

an,bn,cn,dn=fitFunc.getUnnormedInputParams(fita,fitb,fitc,fitd)
print(an,bn,cn,dn)

funcPlot=gaussABCD()
funcPlot.setInitial(an,bn,cn,dn)

plt.subplot(212)
plt.plot(x,y,'.b',x,funcPlot(x,np.zeros(4)),'-g')
plt.title('fitting: '+fitFunc.getName())
    
'''

'''
a=np.array([26])
b=np.array([0.001])
c=np.array([815])
d=np.array([8])
fitFunc=gaussABCD()
fitFunc.setInitial(a,b,c,d)

pop,cov=scp.optimize.curve_fit(fitFunc, x,y,p0=np.zeros(4))
rpop=np.reshape(pop,(4,-1))
fita=a+rpop[0,:]
fitb=b+rpop[1,:]
fitc=c+rpop[2,:]
fitd=d+rpop[3,:]

print(fitFunc.getName(),pop)
print(fita,fitb,fitc,fitd,'  FWHM=', fitFunc.getFWHM(fitb))
print(" M=",fita)

plt.subplot(212)


funcPlot=gaussABCD()
funcPlot.setInitial(fita,fitb,fitc,fitd) 
plt.plot(x,y,'.b',x,funcPlot(x,np.zeros(4)),'-g')
plt.title('fitting: '+funcPlot.getName())

'''

'''
xmin,xmax=x[0],x[-1]
dtx=(xmax-xmin)*0.5
xnorm=(x-xmin)/dtx

ymin,ymax=np.min(y),np.max(y)
dty=ymax-ymin
ynorm=(y-ymin)/dty
'''

'''

M=1
FWHM=0.3
a=np.array([1])
b=np.array([FWHM])
c=np.array([1])
d=np.array([0])

print('ini ',M,FWHM,a,b,c,d)

fitFunc=lorentzABCD()
fitFunc.setInitial(a,b,c,d)

xnorm,ynorm=fitFunc.normalizeInput(x, np.array([0,2]), y, np.array([0,1]))



pop,cov=scp.optimize.curve_fit(fitFunc, xnorm,ynorm,
                               p0=fitFunc.getP0(),bounds=fitFunc.getBounds())
rpop=np.reshape(pop,(4,-1))
fita=a+rpop[0,:]
fitb=b+rpop[1,:]
fitc=c+rpop[2,:]
fitd=d+rpop[3,:]
dtx=1/fitFunc.__ax__
dty=1/fitFunc.__ay__

print(fitFunc.getName(),pop)
print(fita,fitb,fitc,fitd,'  FWHM=', fitFunc.getFWHM(fitb)*dtx)
print(" M=",fita/fitb**2*dty)

plt.subplot(212)

#plt.plot(xnorm,ynorm,'.b',xnorm,fitFunc(xnorm,*pop),'-g')
#plt.title('fitting: '+fitFunc.getName())


an,bn,cn,dn=fitFunc.getUnnormedInputParams(fita,fitb,fitc,fitd)
print(an,bn,cn,dn)



funcPlot=lorentzABCD()
funcPlot.setInitial(an,bn,cn,dn)

plt.plot(x,y,'.b',x,funcPlot(x,np.zeros(4)),'-g')
plt.title('fitting: '+fitFunc.getName())


'''




