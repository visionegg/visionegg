#!/usr/bin/env python

import sys
import Pyro
import Tkinter, tkMessageBox
from VisionEgg.PyroApps.UberClientGUI import client_list, AppWindow

# You can add your own controllers and GUIs to client_list

try:
    app_window = AppWindow(client_list=client_list)
except Pyro.errors.ProtocolError, x:
    if str(x) == 'connection failed': # Can't find UberServer running on network
        try:
            tkMessageBox.showerror("Can't find UberServer","Can't find UberServer running on Pyro network.")
            sys.exit(1)
        except:
            raise # Can't find UberServer running on network
    else:
        raise
except Pyro.errors.PyroError, x:
    if str(x) in ["Name Server not responding","connection failed"]:
        try:
            tkMessageBox.showerror("Can't find Pyro Name Server","Can't find Pyro Name Server on network.")
            sys.exit(1)
        except:
            raise # Can't find Pyro Name Server on network
    else:
        raise
        
app_window.winfo_toplevel().wm_iconbitmap()
app_window.pack(expand=1,fill=Tkinter.BOTH)
app_window.winfo_toplevel().title("Vision Egg")
app_window.winfo_toplevel().minsize(1,1)
app_window.mainloop()
