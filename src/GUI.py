# This is the python source code for GUI bits of the Vision Egg package.
#
#
# Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

####################################################################
#
#        Import all the necessary packages
#
####################################################################

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import os
import Tkinter
import VisionEgg

####################################################################
#
#        StartGraphicsFrame
#
####################################################################

class StartGraphicsFrame(Tkinter.Frame):
    """A window to get the video parameters of Vision Egg initialized"""
    def __init__(self,master=None,callback=None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)
        self.winfo_toplevel().title('Vision Egg - Graphics configuration')
        self.pack()
        self.callback = callback

        # details frame
        self.detailsFrame = Tkinter.Frame(self,relief=Tkinter.RAISED)
        self.detailsFrame.pack(expand=1,fill=Tkinter.BOTH)

        # Fullscreen
        self.fullscreen = Tkinter.BooleanVar()
        Tkinter.Checkbutton(self.detailsFrame,
                            text='Fullscreen - use only with multiple displays',
                            variable=self.fullscreen,
                            relief=Tkinter.FLAT).pack()

        # vsync
        self.vsync = Tkinter.BooleanVar()
        Tkinter.Checkbutton(self.detailsFrame,
                            text='Retrace sync - currently only for nVidia cards (linux only?)',
                            variable=self.vsync,
                            relief=Tkinter.FLAT).pack()

        # realtime
        self.realtime = Tkinter.BooleanVar()
        Tkinter.Checkbutton(self.detailsFrame,
                            text='Maximum priority - currently linux only, superuser status required',
                            variable=self.realtime,
                            relief=Tkinter.FLAT).pack()

        # texture compression
        self.tex_compress = Tkinter.BooleanVar()
        self.tex_compress.set(VisionEgg.video_info.tex_compress)
        Tkinter.Checkbutton(self.detailsFrame,
                            text='Texture compression',
                            variable=self.tex_compress,
                            relief=Tkinter.FLAT).pack()

        # resolution
        Tkinter.Label(self.detailsFrame,text="Window size (pixels):").pack()
        self.resolution = Tkinter.StringVar()
        self.resolution.set("640x480")
        Tkinter.OptionMenu(self.detailsFrame,self.resolution,"640x480","800x600","1024x768").pack()

        # color depth
        Tkinter.Label(self.detailsFrame,text="Color depth (bits per pixel):").pack()
        self.color_depth = Tkinter.StringVar()
        self.color_depth.set("24")
        Tkinter.OptionMenu(self.detailsFrame,self.color_depth,"0 (Any)","16","24","32").pack()

        # Start button
        Tkinter.Button(self,text="start",command=self.start).pack()
        
    def start(self):
        
        VisionEgg.video_info.tex_compress = self.tex_compress.get()
        
        if self.resolution.get() == "640x480":
            width = 640
            height = 480
        elif self.resolution.get() == "800x600":
            width = 800
            height = 600
        elif self.resolution.get() == "1024x768":
            width = 1024
            height = 768
        else:
            raise RuntimeError("Unknown resolution %s"%(self.resolution.get(),))

        if self.color_depth.get() == "0 (Any)":
            preferred_bpp = 0
        elif self.color_depth.get() == "16":
            preferred_bpp = 16
        elif self.color_depth.get() == "24":
            preferred_bpp = 24
        elif self.color_depth.get() == "32":
            preferred_bpp = 32
        else:
            raise RuntimeError("Unknown color_depth %s"%(self.color_depth.get(),))

        try:
            # This stuff determines where things are displayed in X windows
            # Use to control stimulus from one computer while displaying
            # on another.
            GUI_display = os.environ["DISPLAY"]
            os.environ["DISPLAY"] = "localhost:0.0"
        except:
            pass
        VisionEgg.graphicsInit(width,height,
                               fullscreen=self.fullscreen.get(),
                               vsync=self.vsync.get(),
                               realtime_priority=self.realtime.get(),
                               preferred_bpp=preferred_bpp)
        try:
            os.environ["DISPLAY"] = GUI_display
        except:
            pass

        for child in self.children.values():
            child.destroy()

        self.callback()
#        Tkinter.Tk.destroy(self.master) # OK, now close myself

class VideoInfoFrame(Tkinter.Frame):
    def __init__(self,master=None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)
        self.pack()

        Tkinter.Label(self,text="Video information:").pack()
        self.sub_frame = Tkinter.Frame(self,relief=Tkinter.GROOVE)
        self.sub_frame.pack()
        self.update()

    def update(self):
        for child in self.sub_frame.children.values():
            child.destroy()
        if VisionEgg.video_info.initialized:
            if VisionEgg.video_info.fullscreen:
                Tkinter.Label(self.sub_frame,text="fullscreen: %d x %d, %d bpp"%(VisionEgg.video_info.width,VisionEgg.video_info.height,VisionEgg.video_info.bpp)).pack()
            else:
                Tkinter.Label(self.sub_frame,text="window: %d x %d, %d bpp"%(VisionEgg.video_info.width,VisionEgg.video_info.height,VisionEgg.video_info.bpp)).pack()
            if VisionEgg.video_info.tex_compress:
                Tkinter.Label(self.sub_frame,text="Texture compression: On").pack()
            else:
                Tkinter.Label(self.sub_frame,text="Texture compression: Off").pack()
        else:
            Tkinter.Label(self.sub_frame,text="Video system not initialized").pack()

#        Tkinter.Button(self.sub_frame,text="Update video info",command=self.update).pack()
