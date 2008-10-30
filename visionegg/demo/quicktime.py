#!/usr/bin/env python
"""Display a quicktime movie in the Vision Egg.

See also mpeg.py, which plays MPEG movies.
"""

import os, sys
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.Text import *
from VisionEgg.Textures import *
from VisionEgg.QuickTime import new_movie_from_filename, MovieTexture
from pygame.locals import *

screen = get_default_screen()
screen.set(bgcolor=(0,0,0))

if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","water.mov")
movie = new_movie_from_filename(filename)
bounds = movie.GetMovieBox()
height = bounds.bottom-bounds.top
width = bounds.right-bounds.left

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
quit_now = 0
while not quit_now:
    for event in pygame.event.get():
        if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            quit_now = 1
    movie.MoviesTask(0)
    screen.clear()
    viewport.draw()

    swap_buffers() # display the frame we've drawn in back buffer
    frame_timer.tick()
    if movie.IsMovieDone():
        movie.GoToBeginningOfMovie()

frame_timer.log_histogram()
