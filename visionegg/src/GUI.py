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
    def __init__(self,master=None,set_screen_callback=lambda s: None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)
        self.winfo_toplevel().title('Vision Egg - Graphics configuration')
        self.pack()
        self.set_screen_callback = set_screen_callback

        Tkinter.Label(self,
                      text="Vision Egg - Graphics configuration window").pack()

        # Config file
        if VisionEgg.config.VISIONEGG_CONFIG_FILE:
            Tkinter.Label(self,
                          text="Config file location: %s"%(os.path.abspath(VisionEgg.config.VISIONEGG_CONFIG_FILE),)).pack()
        else:
            Tkinter.Label(self,
                          text="Config file location: (None)").pack()

        # Log file location
        
        if VisionEgg.config.VISIONEGG_LOG_FILE:
            Tkinter.Label(self,
                          text="Log file location: %s"%(os.path.abspath(VisionEgg.config.VISIONEGG_LOG_FILE),)).pack()
        else:
            Tkinter.Label(self,
                          text="Log file location: (stderr console)").pack()

        # Fullscreen
        self.fullscreen = Tkinter.BooleanVar()
        self.fullscreen.set(VisionEgg.config.VISIONEGG_FULLSCREEN)
        Tkinter.Checkbutton(self,
                            text='Fullscreen',
                            variable=self.fullscreen,
                            relief=Tkinter.FLAT).pack()
        
        # Maximum priority
        self.max_priority = Tkinter.BooleanVar()
        self.max_priority.set(VisionEgg.config.VISIONEGG_MAXPRIORITY)
        Tkinter.Checkbutton(self,
                            text='Maximum priority',
                            variable=self.max_priority,
                            relief=Tkinter.FLAT).pack()

##        # texture compression
##        self.tex_compress = Tkinter.BooleanVar()
##        self.tex_compress.set(VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION)
##        Tkinter.Checkbutton(self,
##                            text='Texture compression',
##                            variable=self.tex_compress,
##                            relief=Tkinter.FLAT).pack()

        # frame rate
        Tkinter.Label(self,text="What will your monitor refresh's rate be (Hz):").pack()
        self.frame_rate = Tkinter.StringVar()
        self.frame_rate.set("%s"%str(VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ))
        Tkinter.Entry(self,textvariable=self.frame_rate).pack()

        # width
        Tkinter.Label(self,text="Window width (pixels):").pack()
        self.width = Tkinter.StringVar()
        self.width.set("%s"%str(VisionEgg.config.VISIONEGG_SCREEN_W))
        Tkinter.Entry(self,textvariable=self.width).pack()

        # height
        Tkinter.Label(self,text="Window height (pixels):").pack()
        self.height = Tkinter.StringVar()
        self.height.set("%s"%str(VisionEgg.config.VISIONEGG_SCREEN_H))
        Tkinter.Entry(self,textvariable=self.height).pack()

        # color depth
        Tkinter.Label(self,text="Requested total color depth (bits per pixel):").pack()
        self.color_depth = Tkinter.StringVar()
        self.color_depth.set(str(VisionEgg.config.VISIONEGG_PREFERRED_BPP))
        Tkinter.Entry(self,textvariable=self.color_depth).pack()

        # red depth
        Tkinter.Label(self,text="Requested red bits per pixel:").pack()
        self.red_depth = Tkinter.StringVar()
        self.red_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_RED_BITS))
        Tkinter.Entry(self,textvariable=self.red_depth).pack()
        # green depth
        Tkinter.Label(self,text="Requested green bits per pixel:").pack()
        self.green_depth = Tkinter.StringVar()
        self.green_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_GREEN_BITS))
        Tkinter.Entry(self,textvariable=self.green_depth).pack()
        # blue depth
        Tkinter.Label(self,text="Requested blue bits per pixel:").pack()
        self.blue_depth = Tkinter.StringVar()
        self.blue_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_BLUE_BITS))
        Tkinter.Entry(self,textvariable=self.blue_depth).pack()
        # alpha depth
        Tkinter.Label(self,text="Requested alpha bits per pixel:").pack()
        self.alpha_depth = Tkinter.StringVar()
        self.alpha_depth.set(str(VisionEgg.config.VISIONEGG_REQUEST_ALPHA_BITS))
        Tkinter.Entry(self,textvariable=self.alpha_depth).pack()

        # Start button
        b = Tkinter.Button(self,text="start",command=self.start)
        b.pack()
        b.focus_force()
        b.bind('<Return>',self.start)
       
    def start(self):
        
        VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = float(self.frame_rate.get())
        VisionEgg.config.VISIONEGG_FULLSCREEN = self.fullscreen.get()
        VisionEgg.config.VISIONEGG_MAXPRIORITY = self.maxpriority.get()
#        VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = self.tex_compress.get()
        VisionEgg.config.VISIONEGG_SCREEN_W = int(self.width.get())
        VisionEgg.config.VISIONEGG_SCREEN_H = int(self.height.get())
        VisionEgg.config.VISIONEGG_PREFERRED_BPP = int(self.color_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_RED_BITS = int(self.red_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_GREEN_BITS = int(self.green_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_BLUE_BITS = int(self.blue_depth.get())
        VisionEgg.config.VISIONEGG_REQUEST_ALPHA_BITS = int(self.alpha_depth.get())

        screen = VisionEgg.Core.Screen(size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                                             VisionEgg.config.VISIONEGG_SCREEN_H),
                                       fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                                       preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                                       bgcolor=(0.5,0.5,0.5,0.0),
                                       maxpriority=VisionEgg.config.VISIONEGG_MAXPRIORITY)

        for child in self.children.values():
            child.destroy()

        self.set_screen_callback(screen)
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
    def callback(screen):
        global opened_screen # Python doesn't support nested namespace, so this is a trick
        opened_screen = screen
    global opened_screen
    window = OpenScreenDialog(set_screen_callback=callback)
    window.mainloop()
    local_screen = opened_screen
    del opened_screen # Get rid of evil global variables!
    return local_screen
