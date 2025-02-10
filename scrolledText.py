


from tkinter import Scrollbar
from tkinter import ttk
import tkinter as tk


class scrolledText(ttk.Frame):
    
    

    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)
        
        h = ttk.Scrollbar(self, orient = 'horizontal')
        h.pack(side = tk.BOTTOM, fill = tk.X)

        v = Scrollbar(self)
        v.pack(side = tk.RIGHT, fill = tk.Y)

        t = tk.Text(self, wrap = tk.NONE,
                xscrollcommand = h.set, 
                yscrollcommand = v.set)
        
       
        t.pack(side=tk.TOP, fill=tk.BOTH,expand=True)

        h.config(command=t.xview)
        v.config(command=t.yview)
        
        self.text=t




