#!/usr/bin/env python
#
# This is the python source code for a little app that lets you
# test various aspects of texturing in OpenGL.
#
# It is part of the Vision Egg package.
#
# Copyright (c) 2002 Andrew Straw.  Distributed under the terms of the
# GNU General Public License (GPL).

import string
__version__ = string.split('$Revision$')[1]
__date__ = string.join(string.split('$Date$')[1:3], ' ')
__author__ = 'Andrew Straw <astraw@users.sourceforge.net>'

import time

import pygame
from pygame.locals import *

from OpenGL.GL import * # PyOpenGL packages
from Numeric import *
import Tkinter

import VisionEgg
import VisionEgg.GUI

class TextureTestFrame(Tkinter.Frame):
    def __init__(self,master=None,**cnf):
        apply(Tkinter.Frame.__init__,(self,master),cnf)
        self.winfo_toplevel().title('Texture Test')
        self.pack()

        vid_info_frame = VisionEgg.GUI.VideoInfoFrame(self)
        vid_info_frame.pack()

        self.tex_compression = Tkinter.BooleanVar()
        Tkinter.Checkbutton(self,
                            text="Texture compression",
                            variable=self.tex_compression,
                            command=vid_info_frame.update).pack()

        Tkinter.Label(self,text="Texture width:").pack()
        self.tex_width = Tkinter.StringVar()
        self.tex_width.set("512")
        Tkinter.OptionMenu(self,self.tex_width,"1","2","4","8","16","32","64","128","256","512","1024","2048","4096").pack()

        Tkinter.Label(self,text="Texture height:").pack()
        self.tex_height = Tkinter.StringVar()
        self.tex_height.set("512")
        Tkinter.OptionMenu(self,self.tex_height,"1","2","4","8","16","32","64","128","256","512","1024","2048","4096").pack()

        Tkinter.Button(self,text="do glTexSubImage2D ('blit') speed test",command=self.do_blit_speed).pack()
#        Tkinter.Button(self,text="get maximum number of resident textures",command=do_resident_textures).pack()

    def do_blit_speed(self):
        VisionEgg.video_info.tex_compress = self.tex_compression.get()
        
        tex1 = VisionEgg.Texture(size=(int(self.tex_width.get()),int(self.tex_height.get())))
        tex1.load() # initialize the original texture

        texture_dest = tex1.get_texture_buffer()
        texture_source = tex1.get_pil_image()

        num = 10
        start = time.time()
        for i in range(num):
            texture_dest.put_sub_image(texture_source,(0,0),(texture_source.size[0],texture_source.size[1]))
        stop = time.time()

        print "Did %d calls to glTexSubImage2D in %f seconds."%(num,stop-start)
        
        print "blit speed!"
    
app_window = []
def start_texture_test_menu():
    app_window.texture_test_frame = TextureTestFrame(app_window)
    app_window.texture_test_frame.pack()

if __name__ == '__main__':
    app_window = VisionEgg.GUI.StartGraphicsFrame(callback = start_texture_test_menu)
    app_window.mainloop()

