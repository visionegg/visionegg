#!/usr/bin/env python
"""Display quicktime movie."""

import os
import VisionEgg
from VisionEgg.Core import *
from VisionEgg.Text import *
from VisionEgg.Textures import *
from VisionEgg.QuickTime import *

screen = get_default_screen()
screen.set(bgcolor=(0,0,0))

filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","water.mov")
movie = Movie(filename)

left, bottom, right, top = movie.get_box()
width,height = abs(right-left), abs(top-bottom)

scale_x = screen.size[0]/float(width)
scale_y = screen.size[1]/float(height)
scale = min(scale_x,scale_y) # maintain aspect ratio

movie_texture = MovieTexture(movie=movie)

stimulus = TextureStimulus(
    texture=movie_texture,
    position = (screen.size[0]/2.0,screen.size[1]/2.0),
    anchor = 'center',
    mipmaps_enabled = False, # can't do mipmaps with QuickTime movies
    shrink_texture_ok = True,
    size = (width*scale, height*scale),
    )

text = Text( text = "Vision Egg QuickTime movie demo - Press any key to quit",
             position = (screen.size[0]/2,screen.size[1]),
             anchor = 'top',
             color = (1.0, 1.0, 1.0),
             )

viewport = Viewport(screen=screen,
                    stimuli=[stimulus, text])

movie.start()
frame_timer = FrameTimer()
while not pygame.event.peek((pygame.locals.QUIT,
                             pygame.locals.KEYDOWN,
                             pygame.locals.MOUSEBUTTONDOWN)):
    movie.task()
    screen.clear()
    viewport.draw()

    swap_buffers() # display the frame we've drawn in back buffer
    frame_timer.tick()
    if movie.is_done():
        movie.go_to_beginning()
        
frame_timer.print_histogram()
