#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 10:59:58 2025

@author: fizyk
"""

import matplotlib.pyplot as plt
import numpy as np



pointClick=[]
dX=0.25
tmpPoints=None

def graphOnClick(event):
    global tmpPoints
    '''
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
     ('double' if event.dblclick else 'single', event.button,
      event.x, event.y, event.xdata, event.ydata))
    '''
    
    if event.xdata is None or event.ydata is None:
        return
    
    eX=event.xdata
    #eY=event.ydata
    plotX=pointsPlot[0].get_xdata()
    plotY=pointsPlot[0].get_ydata()
    tol=dX*0.5
    xdiff=np.abs(plotX-eX)
    ind=np.argwhere(xdiff<tol)
    
    if ind is not None:
        print(ind)        
        
    sx,sy=plotX[ind],plotY[ind]
    ax=plt.gca()
    ax.plot(sx,sy,'og',markersize=10)
    #ax.annotate('point clicked',(sx,sy),color='Red')
    
    event.canvas.draw()
    
def graphMouseMotion(event):
    global tmpPoints
    if event.xdata is None or event.ydata is None:
        return
    
    #print(event.xdata,event.ydata)
    
    eX=event.xdata
    #eY=event.ydata
    plotX=pointsPlot[0].get_xdata()
    plotY=pointsPlot[0].get_ydata()
    tol=dX*0.5
    xdiff=np.abs(plotX-eX)
    ind=np.argwhere(xdiff<tol)
    
    if ind is not None:
        print(ind)
        
    if tmpPoints is not None:
        tmpPoints.remove()
        
    sx,sy=plotX[ind],plotY[ind]
    ax=plt.gca()
    tmpPoints, =ax.plot(sx,sy,'b^')
    #ax.annotate('point clicked',(sx,sy),color='Red')
    
    event.canvas.draw()


f=plt.figure(dpi=150)
f.canvas.mpl_connect('button_press_event', graphOnClick)
f.canvas.mpl_connect('motion_notify_event', graphMouseMotion)

x=np.arange(0,11,dX )
y=np.sin(x)

pointsPlot=plt.plot(x,y,'ok',x,y,'-r')

plt.show()

