#!/usr/bin/env python

import sys
import Pyro
import Tkinter, tkMessageBox

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.PyroApps.EPhysGUI import client_list, AppWindow, get_server

# You can add your own controllers and GUIs to client_list

result = get_server()
if result:
    hostname,port = result
    app_window = AppWindow(client_list=client_list,
                           server_hostname=hostname,
                           server_port=port)

    app_window.winfo_toplevel().wm_iconbitmap()
    app_window.pack(expand=1,fill=Tkinter.BOTH)
    app_window.mainloop()
