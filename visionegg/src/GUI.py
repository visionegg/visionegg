"""GUI bits of the Vision Egg package."""

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
import VisionEgg
import string

__version__ = VisionEgg.release_name
__cvs__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

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

        # Fullscreen
        self.fullscreen = Tkinter.BooleanVar()
        self.fullscreen.set(VisionEgg.config.VISIONEGG_FULLSCREEN)
        Tkinter.Checkbutton(self,
                            text='Fullscreen',
                            variable=self.fullscreen,
                            relief=Tkinter.FLAT).pack()

        # texture compression
        self.tex_compress = Tkinter.BooleanVar()
        self.tex_compress.set(VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION)
        Tkinter.Checkbutton(self,
                            text='Texture compression',
                            variable=self.tex_compress,
                            relief=Tkinter.FLAT).pack()

        # frame rate
        Tkinter.Label(self,text="What is your monitor refresh (Hz):").pack()
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
        Tkinter.Label(self,text="Color depth (bits per pixel):").pack()
        self.color_depth = Tkinter.StringVar()
        default_bpp_string = "%d"%VisionEgg.config.VISIONEGG_PREFERRED_BPP
        self.color_depth.set(default_bpp_string)
        Tkinter.OptionMenu(self,self.color_depth,default_bpp_string,"0 (Any)","16","24","32").pack()

        # Start button
        Tkinter.Button(self,text="start",command=self.start).pack()
        
    def start(self):
        
        VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ = float(self.frame_rate.get())
        VisionEgg.config.VISIONEGG_FULLSCREEN = self.fullscreen.get()
        VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION = self.tex_compress.get()
        VisionEgg.config.VISIONEGG_SCREEN_W = int(self.width.get())
        VisionEgg.config.VISIONEGG_SCREEN_H = int(self.height.get())
        VisionEgg.config.VISIONEGG_PREFERRED_BPP = int(string.split(self.color_depth.get(),' ')[0])

        screen = VisionEgg.Core.Screen(size=(VisionEgg.config.VISIONEGG_SCREEN_W,
                                             VisionEgg.config.VISIONEGG_SCREEN_H),
                                       fullscreen=VisionEgg.config.VISIONEGG_FULLSCREEN,
                                       preferred_bpp=VisionEgg.config.VISIONEGG_PREFERRED_BPP,
                                       bgcolor=VisionEgg.config.VISIONEGG_SCREEN_BGCOLOR)

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
        if VisionEgg.config.VISIONEGG_TEXTURE_COMPRESSION:
            Tkinter.Label(self.sub_frame,text="Texture compression on").pack()
        else:
            Tkinter.Label(self.sub_frame,text="Texture compression off").pack()

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
