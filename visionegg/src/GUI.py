"""Graphical user interface classes and functions"""

# Copyright (c) 2001-2002 Andrew Straw.  Distributed under the terms of the
# GNU Lesser General Public License (LGPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import VisionEgg
import os
import Tkinter
import string
import sys

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

class showexception(Tkinter.Frame):
    """A window that shows a string and has a quit button."""
    def __init__(self,exc_type, exc_value, traceback_str):
        title="Vision Egg: exception caught"
        try:
            self.winfo_toplevel().title(title)
            self.winfo_toplevel().protocol("WM_DELETE_WINDOW",self.close_window)
        except:
            VisionEgg.Core.message.add("Tkinter problems when trying to display exception. Continuing attempt to open dialog.",level=VisionEgg.Core.Message.INFO)
        first_str = "This program is terminating abnormally because\nan unhandled exception was caught."
        
        type_value_str = "%s: %s"%(str(exc_type),str(exc_value))
        Tkinter.Frame.__init__(self,borderwidth=20)
        self.pack()
        
        Tkinter.Label(self,text=first_str).pack()
        Tkinter.Label(self,text=type_value_str).pack()
        Tkinter.Label(self,text="Traceback (most recent call last):").pack()
        Tkinter.Label(self,text=traceback_str).pack()
        
        b = Tkinter.Button(self,text="Quit",command=self.close_window)
        b.pack()
        b.focus_force()
        b.bind('<Return>',self.close_window)
        self.mainloop()
    def close_window(self,dummy_arg=None):
        self.winfo_toplevel().destroy()
                
class AppWindow(Tkinter.Frame):
    """A GUI Window to be subclassed for your main application window"""
    def __init__(self,master=None,idle_func=lambda: None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)
        self.winfo_toplevel().title('Vision Egg')

        self.info_frame = InfoFrame(self)
        self.info_frame.pack()
        
        self.idle_func = idle_func
        self.after(1,self.idle) # register idle function with Tkinter

    def idle(self):
        self.idle_func()
        self.after(1,self.idle) # (re)register idle function with Tkinter

class OpenScreenDialog(Tkinter.Frame):
    """A GUI window to open an instance of Screen"""
    def __init__(self,master=None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)
        self.winfo_toplevel().title('Vision Egg - Graphics configuration')
        self.pack()

        row = 0
        Tkinter.Label(self,
                      text="Vision Egg - Graphics configuration",
                      font=("Helvetica",14,"bold")).grid(row=row,columnspan=2)
        row += 1

        Tkinter.Label(self,
                      text="The default value for these variables and the\npresence of this dialog window can be\ncontrolled via the Vision Egg config file.",
                      ).grid(row=row,columnspan=2)
        row += 1
        

        file_frame = Tkinter.Frame(self)
        file_frame.grid(row=row,columnspan=2,sticky=Tkinter.W+Tkinter.E)
        
        # Config file
        Tkinter.Label(file_frame,
                      text="Config file location:").grid(row=0,column=0,sticky=Tkinter.E)
        if VisionEgg.config.VISIONEGG_CONFIG_FILE:
            Tkinter.Label(file_frame,
                          text="%s"%(os.path.abspath(VisionEgg.config.VISIONEGG_CONFIG_FILE),)).grid(row=0,column=1,sticky=Tkinter.W)
        else:
            Tkinter.Label(file_frame,
                          text="(None)").grid(row=0,column=1,sticky=Tkinter.W)

        # Log file location
        
        Tkinter.Label(file_frame,
                      text="Log file location:").grid(row=1,column=0,sticky=Tkinter.E)
        if VisionEgg.config.VISIONEGG_LOG_FILE:
            Tkinter.Label(file_frame,
                          text="%s"%(os.path.abspath(VisionEgg.config.VISIONEGG_LOG_FILE),)).grid(row=1,column=1,sticky=Tkinter.W)
        else:
            Tkinter.Label(file_frame,
                          text="(stderr console)").grid(row=1,column=1,sticky=Tkinter.W)
        row += 1

        # Fullscreen
        self.fullscreen = Tkinter.BooleanVar()
        self.fullscreen.set(VisionEgg.config.VISIONEGG_FULLSCREEN)
        Tkinter.Checkbutton(self,
                            text='Fullscreen',
                            variable=self.fullscreen,
                            relief=Tkinter.FLAT).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1
        
        # Maximum priority
        self.maxpriority = Tkinter.BooleanVar()
        self.maxpriority.set(VisionEgg.config.VISIONEGG_MAXPRIORITY)
	try:
	    import _maxpriority
	    # Only display checkbutton if we have the module
	    Tkinter.Checkbutton(self,
                                text='Maximum priority',
                                variable=self.maxpriority,
                                relief=Tkinter.FLAT).grid(row=row,column=1,sticky=Tkinter.W)
            row += 1
	except:
	    pass


        # Sync swap
        self.sync_swap = Tkinter.BooleanVar()
        self.sync_swap.set(VisionEgg.config.VISIONEGG_SYNC_SWAP)
        Tkinter.Checkbutton(self,
                            text='Synchronize buffer swaps',
                            variable=self.sync_swap,
                            relief=Tkinter.FLAT).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # Record times
        self.record_times = Tkinter.BooleanVar()
        self.record_times.set(VisionEgg.config.VISIONEGG_RECORD_TIMES)
        Tkinter.Checkbutton(self,
                            text='Record frame timing information',
                            variable=self.record_times,
                            relief=Tkinter.FLAT).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

##        # texture compression
##        self.tex_compress = Tkinter.BooleanVar()
##        self.tex_compress.set(VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION)
##        Tkinter.Checkbutton(self,
##                            text='Texture compression',
##                            variable=self.tex_compress,
##                            relief=Tkinter.FLAT).grid(row=row,columnspan=2)
##        row += 1

        # frame rate
        Tkinter.Label(self,text="What will your monitor refresh's rate be (Hz):").grid(row=row,column=0,sticky=Tkinter.E)
        self.frame_rate = Tkinter.StringVar()
        self.frame_rate.set("%s"%str(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ))
        Tkinter.Entry(self,textvariable=self.frame_rate).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # width
        Tkinter.Label(self,text="Window width (pixels):").grid(row=row,column=0,sticky=Tkinter.E)
        self.width = Tkinter.StringVar()
        self.width.set("%s"%str(VisionEgg.config.VISIONEGG_SCREEN_W))
        Tkinter.Entry(self,textvariable=self.width).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # height
        Tkinter.Label(self,text="Window height (pixels):").grid(row=row,column=0,sticky=Tkinter.E)
        self.height = Tkinter.StringVar()
        self.height.set("%s"%str(VisionEgg.config.VISIONEGG_SCREEN_H))
        Tkinter.Entry(self,textvariable=self.height).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # color depth
        Tkinter.Label(self,text="Requested total color depth (bits per pixel):").grid(row=row,column=0,sticky=Tkinter.E)
        self.color_depth = Tkinter.StringVar()
        self.color_depth.set(str(VisionEgg.config.VISIONEGG_PREFERRED_BPP))
        Tkinter.Entry(self,textvariable=self.color_depth).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # red depth
        Tkinter.Label(self,text="Requested red bits per pixel:").grid(row=row,column=0,sticky=Tkinter.E)
        self.red_depth = Tkinter.StringVar()
        self.red_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_RED_BITS))
        Tkinter.Entry(self,textvariable=self.red_depth).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # green depth
        Tkinter.Label(self,text="Requested green bits per pixel:").grid(row=row,column=0,sticky=Tkinter.E)
        self.green_depth = Tkinter.StringVar()
        self.green_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_GREEN_BITS))
        Tkinter.Entry(self,textvariable=self.green_depth).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # blue depth
        Tkinter.Label(self,text="Requested blue bits per pixel:").grid(row=row,column=0,sticky=Tkinter.E)
        self.blue_depth = Tkinter.StringVar()
        self.blue_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_BLUE_BITS))
        Tkinter.Entry(self,textvariable=self.blue_depth).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        # alpha depth
        Tkinter.Label(self,text="Requested alpha bits per pixel:").grid(row=row,column=0,sticky=Tkinter.E)
        self.alpha_depth = Tkinter.StringVar()
        self.alpha_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_ALPHA_BITS))
        Tkinter.Entry(self,textvariable=self.alpha_depth).grid(row=row,column=1,sticky=Tkinter.W)
        row += 1

        if sys.platform == 'darwin':
            Tkinter.Label(self,text="If you want to check any buttons\n(Mac OS X Tk 8.4a4 bug workaround):").grid(row=row,column=0,sticky=Tkinter.E)
            Tkinter.Button(self,text="PRESS ME FIRST").grid(row=row,column=1,sticky=Tkinter.W)
            row += 1

        # Start button
        b = Tkinter.Button(self,text="start",command=self.start)
        b.grid(row=row,columnspan=2)
        b.focus_force()
        b.bind('<Return>',self.start)
       
    def start(self):
        
        VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = float(self.frame_rate.get())
        VisionEgg.config.VISIONEGG_FULLSCREEN = self.fullscreen.get()
        VisionEgg.config.VISIONEGG_MAXPRIORITY = self.maxpriority.get()
        VisionEgg.config.VISIONEGG_SYNC_SWAP = self.sync_swap.get()
        VisionEgg.config.VISIONEGG_RECORD_TIMES = self.record_times.get()
#        VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = self.tex_compress.get()
        VisionEgg.config.VISIONEGG_SCREEN_W = int(self.width.get())
        VisionEgg.config.VISIONEGG_SCREEN_H = int(self.height.get())
        VisionEgg.config.VISIONEGG_PREFERRED_BPP = int(self.color_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_RED_BITS = int(self.red_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_GREEN_BITS = int(self.green_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_BLUE_BITS = int(self.blue_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_ALPHA_BITS = int(self.alpha_depth.get())

        self.opened_screen = None

        try:
            self.opened_screen = VisionEgg.Core.Screen(size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                                                             VisionEgg.config.VISIONEGG_SCREEN_H),
                                                       fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                                                       preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                                                       bgcolor=(0.5,0.5,0.5,0.0),
                                                       maxpriority=VisionEgg.config.VISIONEGG_MAXPRIORITY)
        finally:
            for child in self.children.values():
                child.destroy()
            Tkinter.Tk.destroy(self.master) # OK, now close myself

class InfoFrame(Tkinter.Frame):
    def __init__(self,master=None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)

        Tkinter.Label(self,text="Vision Egg information:").pack()
        self.sub_frame = Tkinter.Frame(self,relief=Tkinter.GROOVE)
        self.sub_frame.pack()
        self.update()

    def update(self):
        for child in self.sub_frame.children.values():
            child.destroy()
        if VisionEgg.config.VISIONEGG_FULLSCREEN:
            Tkinter.Label(self.sub_frame,text="fullscreen mode").pack()
        else:
            Tkinter.Label(self.sub_frame,text="window mode").pack()
##        if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
##            Tkinter.Label(self.sub_frame,text="Texture compression on").pack()
##        else:
##            Tkinter.Label(self.sub_frame,text="Texture compression off").pack()

        #Tkinter.Button(self.sub_frame,text="Update information",command=self.update).pack()

class ToplevelDialog(Tkinter.Toplevel):
    """Base class for a dialog that runs on the top level."""
    def __init__(self,**kw):
        apply(Tkinter.Toplevel.__init__,(self,),kw)
        self.transient(self)
        self.frame = Tkinter.Frame(self)
        self.frame.pack(padx=100,pady=70,ipadx=20,ipady=10,expand=1)
        self.frame.focus_set()

    def destroy(self):
        Tkinter.Toplevel.destroy(self)

class GetKeypressDialog(ToplevelDialog):
    """Open a dialog box which returns when a valid key is pressed.

    Arguments are:
    master - a Tkinter widget (defaults to None)
    title - a string for the title bar of the widget
    text - a string to display as the text in the body of the dialog
    key_list - a list of acceptable keys, e.g. ['q','1','2','<Return>']

    The following example will print whatever character was pressed:
    d = GetKeypressDialog(key_list=['q','1','2','<Return>','<Escape>'])
    print d.result
    
    The implementation is somewhat obscure because a new Tk/Tcl
    interpreter may be created if this Dialog is called with no
    master widget."""
    def __init__(self,
                 title="Press a key",
                 text="Press a key",
                 key_list=[],
                 **kw):
        
        apply(ToplevelDialog.__init__,(self,),kw)
        self.title(title)
        self.result = None

        # The dialog box body
        Tkinter.Label(self.frame, text=text).pack()

        for key in key_list:
            self.bind(key,self.keypress)
        self.wait_window(self)
        
    def keypress(self,tkinter_event):
        self.result = tkinter_event.keysym
        self.destroy()

def get_screen_via_GUI():
    window = OpenScreenDialog()
    window.mainloop()
    if hasattr(window,"opened_screen"):
        return window.opened_screen
    else:
        # User trying to quit
        sys.exit()
