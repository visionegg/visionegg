#!/usr/bin/env python

############################
#  Import various modules  #
############################

import VisionEgg
from VisionEgg.Core import *
from VisionEgg.Dots import DotArea2D
from VisionEgg.Gratings import SinGrating2D
from VisionEgg.MoreStimuli import Target2D
from VisionEgg.Textures import Mask2D, Texture, SpinningDrum, TextureStimulus
from VisionEgg.Text import Text
from math import sin, pi
import math
import pygame.locals
import RandomArray # Numeric

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # make black (RGBA)

x1 = screen.size[0]/4
x2 = 2*screen.size[0]/4
x3 = 3*screen.size[0]/4

y1 = screen.size[1]/3
y2 = 2*screen.size[1]/3

width = screen.size[0]/5
height = width
#height = screen.size[1]/4

#####################################
#  text                             #
#####################################

text = Text( text = "Vision Egg multi stimulus demo - Press any key to quit",
             position = (screen.size[0]/2,2),
             anchor = 'bottom',
             color = (1.0,1.0,1.0,1.0))

#####################################
#  Random dots                      #
#####################################


dots = DotArea2D( center                  = ( x1, y1),
                  size                    = ( width, height ),
                  )

#####################################
#  Color grating                    #
#####################################

try:
    circle_mask = Mask2D(function='circle',
                         radius_parameter=100,
                         num_samples=(256,256))
except Exception, x:
    message.add( "Exception while trying to create Mask2D for color grating: %s: %s"%(x.__class__,str(x)),
                 level=Message.WARNING)
    circle_mask = None

color_grating = SinGrating2D(color1           = (0.5, 0.25, 0.5, 0.0), # RGBA, Alpha ignored
                             color2           = (1.0, 0.5,  0.1, 0.0), # RGBA, Alpha ignored
                             contrast         = 0.2,
                             pedestal         = 0.1,
                             mask             = circle_mask,
                             center           = (x1,y2),
                             size             = (width,width), # must be square for circle shape
                             spatial_freq     = 20.0/ screen.size[0],
                             temporal_freq_hz = 1.0,
                             orientation      = 270.0)

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

drum = SpinningDrum(texture=texture,shrink_texture_ok=1)

def angle_as_function_of_time(t):
    return 90.0*t % 360.0 # rotate at 90 degrees per second (wrap at 360)

def projection_matrix_f(t):
    projection = SimplePerspectiveProjection(fov_x=55.0,aspect_ratio=float(width)/height)
    eye = (0.0,sin(t*0.3)+2.0,-2.0)
    camera_look_at = (0.0,0.0,0.0)
    camera_up = (0.0,1.0,0.0)
    projection.look_at( eye, camera_look_at, camera_up)
    return projection.get_matrix()

drum_projection = SimplePerspectiveProjection() # Parameters set in realtime, so no need to specify here

##########
#  Gabor #
##########


try:
    gaussian_mask = Mask2D(function='gaussian',
                           radius_parameter=25,
                           num_samples=(256,256))
except Exception, x:
    message.add( "Exception while trying to create Mask2D for gabor: %s: %s"%(x.__class__,str(x)),
                 level=Message.WARNING)
    gaussian_mask = None

gray_rect = Target2D( center           = ( x2, y1 ),
                      size             = ( width, height ),
                      color            = (0.5, 0.5, 0.5, 1.0),
                      )

gabor = SinGrating2D(mask             = gaussian_mask,
                     center           = ( x2, y1 ),
                     size             = ( width, height ),
                     spatial_freq     = 40.0 / screen.size[0], # units of cycles/pixel
                     temporal_freq_hz = 2.0,
                     orientation      = 45.0 )

#########################
#  Copy of framebuffer  #
#########################

# setup Texture instance for proper size and scaling, etc.
framebuffer_copy_texture = Texture( texels=screen.get_framebuffer_as_image() )

framebuffer_copy = TextureStimulus( texture = framebuffer_copy_texture,
                                    mipmaps_enabled=0,
                                    size=(width,height),
                                    texture_min_filter=gl.GL_LINEAR,
                                    position=(x3,y1),
                                    anchor='center' )

framebuffer_texture_object = framebuffer_copy.parameters.texture.get_texture_object()

# OpenGL textures must be power of 2
def next_power_of_2(f):
    return math.pow(2.0,math.ceil(math.log(f)/math.log(2.0)))
fb_width_pow2  = int(next_power_of_2(screen.size[0]))
fb_height_pow2  = int(next_power_of_2(screen.size[1]))
def copy_framebuffer():
    "Replace contents of texture object with new texture copied from framebuffer"
    framebuffer_texture_object.put_new_framebuffer(size=(fb_width_pow2,fb_height_pow2))

########################################
#  Create viewports                    #
########################################

viewport_2d = Viewport( screen=screen, stimuli=[dots,
                                                color_grating,
                                                gray_rect,
                                                gabor,
                                                text,
                                                framebuffer_copy] )

drum_viewport = Viewport(screen=screen,
                         lowerleft=(x2-width/2,y2-height/2),
                         size=(width,height),
                         projection=drum_projection,
                         stimuli=[drum])

#####################################################
#  Main loop (non VisionEgg.Core.Presentation way)  #
#####################################################

# quit on any of these events
while not pygame.event.peek((pygame.locals.QUIT,
                             pygame.locals.KEYDOWN,
                             pygame.locals.MOUSEBUTTONDOWN)):
    t = VisionEgg.time_func()
    
    # update parameters (can be done with VisionEgg.Core.Controllers)
    color_grating.parameters.pedestal = pedestal_func(t)
    drum.parameters.angular_position = angle_as_function_of_time(t)
    drum_projection.parameters.matrix = projection_matrix_f(t)

    # do drawing, etc.  (can be done with Presentation.go() method)
    screen.clear() # clear the back buffer
    drum_viewport.draw() # draw spinning drum
    viewport_2d.draw() # draw 2D stimuli

    copy_framebuffer() # make copy of framebuffer in texture for draw on next frame
    
    pixels =  RandomArray.randint(0,256,(20,20,3)).astype(Numeric.UnsignedInt8)
    screen.put_pixels(pixels,
                      scale_x=5.0,
                      scale_y=5.0,
                      position=(x3,y2),
                      anchor='center',
                      )
    swap_buffers() # display the frame we've drawn in back buffer
