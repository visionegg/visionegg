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

        self.vid_info_frame = VisionEgg.GUI.VideoInfoFrame(self)
        self.vid_info_frame.pack()

        self.tex_compression = Tkinter.BooleanVar()
        self.tex_compression.set(VisionEgg.video_info.tex_compress)
        Tkinter.Checkbutton(self,
                            text="Texture compression",
                            variable=self.tex_compression,
                            command=self.set_tex_compression).pack()

        Tkinter.Label(self,text="Texture width:").pack()
        self.tex_width = Tkinter.StringVar()
        self.tex_width.set("512")
        Tkinter.OptionMenu(self,self.tex_width,"1","2","4","8","16","32","64","128","256","512","1024","2048","4096").pack()

        Tkinter.Label(self,text="Texture height:").pack()
        self.tex_height = Tkinter.StringVar()
        self.tex_height.set("512")
        Tkinter.OptionMenu(self,self.tex_height,"1","2","4","8","16","32","64","128","256","512","1024","2048","4096").pack()

        Tkinter.Label(self,text="image file to use as texture:").pack()
        self.image_file = Tkinter.StringVar()
        self.image_file.set("(none - generate own)")
        Tkinter.Entry(self,textvariable=self.image_file).pack()

        Tkinter.Button(self,text="do glTexSubImage2D ('blit') speed test",command=self.do_blit_speed).pack()
        Tkinter.Button(self,text="get maximum number of resident textures",command=self.do_resident_textures).pack()

    def do_blit_speed(self):
        glEnable( GL_TEXTURE_2D )
        print "Using texture from file: %s (Not really, yet)"%self.image_file.get()
        VisionEgg.video_info.tex_compress = self.tex_compression.get()
        
        tex1 = VisionEgg.Texture(size=(int(self.tex_width.get()),int(self.tex_height.get())))
        tex_id = tex1.load() # initialize the original texture
        tex_buf = tex1.get_texture_buffer()

        # show the texture first
        VisionEgg.OrthographicProjection().set_GL_projection_matrix()
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, tex1.buf_bf)
        glVertex3f(-1.0,-1.0,-6.0)
        glTexCoord2f(1.0, tex1.buf_bf)
        glVertex3f(1.0,-1.0,-6.0)
        glTexCoord2f(1.0, tex1.buf_tf)
        glVertex3f(1.0,1.0,-6.0)
        glTexCoord2f(0.0, tex1.buf_tf)
        glVertex3f(-1.0,1.0,-6.0)
        glEnd()
        VisionEgg.swap_buffers()

        texture_dest = tex1.get_texture_buffer()
        texture_source = tex1.get_pil_image()

        num = 10
        start = time.time()
        for i in range(num):
            print "BROKEN!!!"
#            texture_dest.put_sub_image(texture_source,(0,0),(texture_source.size[0],texture_source.size[1]))
        stop = time.time()

        print "Did %d calls to glTexSubImage2D in %f seconds."%(num,stop-start)
        
        print "blit speed!"
        tex_buf.free()

    def do_resident_textures(self):
        print "Not implemented yet!"
        glEnable( GL_TEXTURE_2D )
        print "Using texture from file: %s (Not really, yet)"%self.image_file.get()
        VisionEgg.video_info.tex_compress = self.tex_compression.get()
        orig =  VisionEgg.Texture(size=(int(self.tex_width.get()),int(self.tex_height.get()))) 

        texs = []
        tex_ids = []
        tex_bufs = []
        
        done = 0
        counter = 0
        while not done:
            counter = counter + 1
            tex_ids.append( orig.load() ) 
            tex_bufs.append( orig.get_texture_buffer() )

            answers = glAreTexturesResident( tex_ids )
            if type(answers) != type([1,2]):
                answers = list([answers])
            for answer in answers:
                if answer == 0:
                    done = 1 # loop until one of the textuers isn't resident
            max_within_reason = 50
            if counter > max_within_reason:
                print "Stopping glAreTexturesResident() test -- Over %d textures are reported resident!"%max_within_reason
                done = 1
        print "%d textures were reported resident, but %d were not."%(counter-1,counter)
        for buf in tex_bufs:
            buf.free()

    def set_tex_compression(self):
        """Callback for tick button"""
        VisionEgg.video_info.tex_compress = self.tex_compression.get()
        self.vid_info_frame.update()
    
app_window = []
def start_texture_test_menu():
    app_window.texture_test_frame = TextureTestFrame(app_window)
    app_window.texture_test_frame.pack()

if __name__ == '__main__':
    app_window = VisionEgg.GUI.StartGraphicsFrame(callback = start_texture_test_menu)
    app_window.mainloop()

