#!/usr/bin/env python

############################
#  Import various modules  #
############################

import VisionEgg
from VisionEgg.Core import *
from VisionEgg.Dots import DotArea2D
from VisionEgg.Gratings import SinGrating2D
from VisionEgg.MoreStimuli import Target2D
from VisionEgg.Textures import Mask2D, Texture, SpinningDrum
from VisionEgg.Text import BitmapText
from math import sin, pi
import pygame.locals

#####################################
#  Initialize OpenGL window/screen  #
#####################################

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0,0.0) # make black (RGBA)

x1 = screen.size[0]/4.0
x2 = 3*screen.size[0]/4.0

y1 = screen.size[1]/4.0
y2 = 3*screen.size[1]/4.0

width = screen.size[0]/3.0
height = screen.size[1]/3.0

#####################################
#  text                             #
#####################################

text = BitmapText( text = "Vision Egg multi stimulus demo -- Press Esc to quit",
                   lowerleft = (0,5),
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
                             size             = (width,width), # must be squre for circle shape
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
    return 90.0*t # rotate at 90 degrees per second

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
                      size             = ( width, width ),
                      color            = (0.5, 0.5, 0.5, 1.0),
                      )

gabor = SinGrating2D(mask             = gaussian_mask,
                     center           = ( x2, y1 ),
                     size             = ( width, width ),
                     spatial_freq     = 40.0 / screen.size[0], # units of cycles/pixel
                     temporal_freq_hz = 2.0,
                     orientation      = 45.0 )

########################################
#  Create viewports                    #
########################################

viewport_2d = Viewport( screen=screen, stimuli=[dots,
                                                color_grating,
                                                gray_rect,
                                                gabor,
                                                text] )

drum_viewport = Viewport(screen=screen,
                         lowerleft=(x2-width/2,y2-height/2),
                         size=(width,height),
                         projection=drum_projection,
                         stimuli=[drum])

########################################
#  Presentation object and events      #
########################################

p = Presentation(go_duration=('forever',),
                 viewports=[viewport_2d, drum_viewport])

def quit(dummy_arg=None):
    p.parameters.go_duration = (0,'frames')
    
def keydown(event):
    if event.key == pygame.locals.K_ESCAPE:
        quit()
    
p.parameters.handle_event_callbacks=[(pygame.locals.QUIT, quit),
                                     (pygame.locals.KEYDOWN, keydown)]

########################################
#  Add controllers and go              #
########################################

p.add_controller(color_grating,'pedestal',FunctionController(during_go_func=pedestal_func))
p.add_controller(drum,'angular_position', FunctionController(during_go_func=angle_as_function_of_time))
p.add_controller(drum_projection,'matrix', FunctionController(during_go_func=projection_matrix_f))

p.go()
