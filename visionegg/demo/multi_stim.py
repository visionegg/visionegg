#!/usr/bin/env python
"""
multiple stimulus demo

"""

############################
#  Import various modules  #
############################

import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import *
from VisionEgg.Dots import DotArea2D
from VisionEgg.Gratings import SinGrating2D
from VisionEgg.MoreStimuli import Target2D
from VisionEgg.Textures import Mask2D, Texture, SpinningDrum, TextureStimulus
from VisionEgg.Textures import TextureTooLargeError
from VisionEgg.Text import Text
from math import sin, pi
import math
from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN
import numpy

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # make black (RGBA)
# display loading screen ASAP
screen.clear()
loading_text = Text( text     = "Vision Egg multi stimulus demo - Loading...",
                     position = (screen.size[0]/2,screen.size[1]/2),
                     anchor   = 'center',
                     color    = (1.0, 1.0, 1.0),
                     )
viewport_2d = Viewport( screen  = screen,
                        stimuli = [loading_text],
                        )
viewport_2d.draw()
swap_buffers()


x1 = screen.size[0]/4
x2 = 2*screen.size[0]/4
x3 = 3*screen.size[0]/4

y1 = screen.size[1]/3
y2 = 2*screen.size[1]/3

width = screen.size[0]/5
height = width

warning_stimuli = [] # display known errors
warning_color = (1.0, 0.0, 0.0) # RGB
warning_font_size = 20

legends = [] # display legends
legend_color = (1.0, 1.0, 1.0) # RGB
legend_font_size = 20

#####################################
#  text                             #
#####################################

text = Text( text = "Vision Egg multi stimulus demo - Press any key to quit",
             position = (screen.size[0]/2,screen.size[1]),
             anchor = 'top',
             color = (1.0, 1.0, 1.0),
             )

#####################################
#  Random dots                      #
#####################################

dots = DotArea2D( position = ( x1, y1),
                  anchor   = 'center',
                  size     = ( width, height ),
                  )
legends.append(
    Text( text = "DotArea2D",
          position           = (x1,y1-height/2+2),
          anchor             = 'top',
          color = legend_color,
          font_size = legend_font_size,
          )
    )

#####################################
#  Color grating                    #
#####################################

try:
    circle_mask = Mask2D(function='circle',
                         radius_parameter=100,
                         num_samples=(256,256))
except Exception, x:
    circle_mask = None
    warning_stimuli.append(
        Text( text      = "Texture Mask",
              position  = (x1,y2),
              anchor    = 'center',
              color     = warning_color,
              font_size = warning_font_size,              
              )
        )
    print "Exception while trying to create circle_mask: %s: %s"%(x.__class__,str(x))
    
color_grating = SinGrating2D(color1           = (0.5, 0.25, 0.5), # RGB, Alpha ignored if given
                             color2           = (1.0, 0.5,  0.1), # RGB, Alpha ignored if given
                             contrast         = 0.2,
                             pedestal         = 0.1,
                             mask             = circle_mask,
                             position         = (x1,y2),
                             anchor           = 'center',
                             size             = (width,width), # must be square for circle shape
                             spatial_freq     = 20.0/ screen.size[0],
                             temporal_freq_hz = 1.0,
                             orientation      = 270.0)

legends.append(
    Text( text = "SinGrating2D (color)",
          position           = (x1,y2-height/2+2),
          anchor             = 'top',
          color = legend_color,
          font_size = legend_font_size,
          )
    )

def pedestal_func(t):
    # Calculate pedestal over time. (Pedestal range [0.1,0.9] and
    # contrast = 0.2 limits total range to [0.0,1.0])
    temporal_freq_hz = 0.2
    return 0.4 * sin(t*2*pi * temporal_freq_hz) + 0.5

#####################################
#  Spinning drum with moving POV    #
#####################################

# Get a texture
filename = os.path.join(VisionEgg.config.VISIONEGG_SYSTEM_DIR,"data","panorama.jpg")
texture = Texture(filename)

drum = SpinningDrum(texture=texture,shrink_texture_ok=True)
legends.append(
    Text( text = "SpinningDrum",
          position           = (x2,y2-height/2+2),
          anchor             = 'top',
          color = legend_color,
          font_size = legend_font_size,
          )
    )

def angle_as_function_of_time(t):
    return 90.0*t % 360.0 # rotate at 90 degrees per second (wrap at 360)

def cam_matrix_f(t):
    cam_matrix = ModelView()
    eye = (0.0,sin(t*0.3)+2.0,-2.0)
    camera_look_at = (0.0,0.0,0.0)
    camera_up = (0.0,1.0,0.0)
    cam_matrix.look_at( eye, camera_look_at, camera_up)
    return cam_matrix.get_matrix()

drum_camera_matrix = ModelView()

##########
#  Gabor #
##########

gray_rect = Target2D( position = ( x2, y1 ),
                      anchor   = 'center',
                      size     = ( width, height ),
                      color    = (0.5, 0.5, 0.5, 1.0),
                      )

try:
    gaussian_mask = Mask2D(function='gaussian',
                           radius_parameter=25,
                           num_samples=(256,256))
except Exception, x:
    gaussian_mask = None
    warning_stimuli.append(
        Text( text      = "Texture Mask",
              position  = (x2,y1),
              anchor    = 'center',
              color     = warning_color,
              font_size = warning_font_size,              
              )
        )
    print "Exception while trying to create gaussian_mask: %s: %s"%(x.__class__,str(x))
    
gabor = SinGrating2D(mask             = gaussian_mask,
                     position         = ( x2, y1 ),
                     anchor           = 'center',
                     size             = ( width, height ),
                     spatial_freq     = 40.0 / screen.size[0], # units of cycles/pixel
                     temporal_freq_hz = 2.0,
                     orientation      = 45.0 )
legends.append(
    Text( text = "SinGrating2D (gabor)",
          position           = (x2,y1-height/2+2),
          anchor             = 'top',
          color = legend_color,
          font_size = legend_font_size,
          )
    )

#########################
#  Copy of framebuffer  #
#########################

# setup Texture instance for proper size and scaling, etc.
framebuffer_copy_texture = Texture( texels=screen.get_framebuffer_as_image(format=gl.GL_RGBA) )

try:
    framebuffer_copy = TextureStimulus( texture            = framebuffer_copy_texture,
                                        internal_format    = gl.GL_RGBA,
                                        mipmaps_enabled    = False,
                                        size               = (width,height),
                                        texture_min_filter = gl.GL_LINEAR,
                                        position           = (x3,y1),
                                        anchor             = 'center',
                                        shrink_texture_ok  = False, # settting to True causes massive slowdowns
                                        )
    framebuffer_copy_works = True
except Exception, x:
    warning_stimuli.append(
        Text( text      = "Framebuffer copy",
              position  = (x3,y1),
              anchor    = 'center',
              color     = warning_color,
              font_size = warning_font_size,              
              )
    )
    framebuffer_copy_works = False
    print "Exception while trying to create framebuffer_copy: %s: %s"%(x.__class__,str(x))

legends.append(
    Text( text = "put_new_framebuffer()",
          position           = (x3,y1-height/2+2),
          anchor             = 'top',
          color = legend_color,
          font_size = legend_font_size,
          )
    )

legends.append(
    Text( text = "put_pixels()",
          position           = (x3,y2-height/2+2),
          anchor             = 'top',
          color = legend_color,
          font_size = legend_font_size,
          )
    )

if framebuffer_copy_works:
    framebuffer_texture_object = framebuffer_copy.parameters.texture.get_texture_object()

# OpenGL textures must be power of 2
def next_power_of_2(f):
    return math.pow(2.0,math.ceil(math.log(f)/math.log(2.0)))
fb_width_pow2  = int(next_power_of_2(screen.size[0]))
fb_height_pow2  = int(next_power_of_2(screen.size[1]))
def copy_framebuffer():
    "Replace contents of texture object with new texture copied from framebuffer"
    framebuffer_texture_object.put_new_framebuffer(size=(fb_width_pow2,fb_height_pow2),
                                                   internal_format=gl.GL_RGB,
                                                   buffer='back',
                                                   )

########################################
#  Create viewports                    #
########################################

stimuli_2d = [dots, gray_rect, gabor, text, color_grating]

if framebuffer_copy_works:
    stimuli_2d.append(framebuffer_copy)

if len(warning_stimuli):
    warning_stimuli.append(
        Text( text = "WARNING: This video system has incomplete OpenGL support. Errors in red.",
              position = (screen.size[0]/2,5),
              anchor = 'bottom',
              color = warning_color,
              font_size = warning_font_size,              
              )
        )
    stimuli_2d.extend(warning_stimuli)
stimuli_2d.extend(legends)

viewport_2d.set(stimuli = stimuli_2d) # give viewport_2d our stimuli

drum_viewport = Viewport( screen     = screen,
                          position   = (x2-width/2,y2-height/2),
                          anchor     = 'lowerleft',
                          size       = (width,height),
                          projection = SimplePerspectiveProjection(
    fov_x=55.0,
    aspect_ratio=float(width)/height),
                          camera_matrix = drum_camera_matrix,
                          stimuli    = [drum])

##############################################################
#  Main loop (not using VisionEgg.FlowControl.Presentation)  #
##############################################################

# save time
frame_timer = VisionEgg.Core.FrameTimer()

quit_now = 0
while not quit_now:
    for event in pygame.event.get():
        if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            quit_now = 1
    t = VisionEgg.time_func()
    
    # update parameters (could also be done with VisionEgg.FlowControl.Controllers)
    color_grating.parameters.pedestal = pedestal_func(t)
    drum.parameters.angular_position = angle_as_function_of_time(t)
    drum_camera_matrix.parameters.matrix = cam_matrix_f(t)

    # do drawing, etc.  (can be done with Presentation.go() method)
    screen.clear() # clear the back buffer
    drum_viewport.draw() # draw spinning drum
    viewport_2d.draw() # draw 2D stimuli

    pixels =  numpy.random.randint(0,256,size=(20,20,3)).astype(numpy.uint8)
    screen.put_pixels(pixels,
                      scale_x=5.0,
                      scale_y=5.0,
                      position=(x3,y2),
                      anchor='center',
                      )

    if framebuffer_copy_works:
        copy_framebuffer() # make copy of framebuffer in texture for draw on next frame
    
    swap_buffers() # display the frame we've drawn in back buffer
    frame_timer.tick()

frame_timer.log_histogram()
    
