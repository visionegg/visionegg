#!/usr/bin/env python
"""Display quicktime movie."""

import os, sys
import VisionEgg
from VisionEgg.Core import *
from VisionEgg.Text import *
from VisionEgg.Textures import *
from VisionEgg.QuickTime import new_movie_from_filename, MovieTexture

screen = get_default_screen()
screen.set(bgcolor=(0,0,0))

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","water.mov")
movie = new_movie_from_filename(filename) # movie is type Carbon.Qt.Movie
bounds = movie.GetMovieBox()
width = bounds[2]-bounds[0]
height = bounds[3]-bounds[1]

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

movie.StartMovie()
frame_timer = FrameTimer()
while not pygame.event.peek((pygame.locals.QUIT,
                             pygame.locals.KEYDOWN,
                             pygame.locals.MOUSEBUTTONDOWN)):
    movie.MoviesTask(0)
    screen.clear()
    viewport.draw()

    swap_buffers() # display the frame we've drawn in back buffer
    frame_timer.tick()
    if movie.IsMovieDone():
        movie.GoToBeginningOfMovie()
        
frame_timer.log_histogram()
