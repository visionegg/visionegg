#!/usr/bin/env python

# Make a movie of a black target moving across a white background.

fps = 12.0 # frames per second

########################################################
#  Import various modules from the Vision Egg package  #
########################################################

from VisionEgg.Core import *
from VisionEgg.AppHelper import *
from VisionEgg.MoreStimuli import *

#################################
#  Initialize the various bits  #
#################################

# Initialize OpenGL graphics screen
screen = get_default_screen()

# Set the background color (RGBA) white
screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)

# Create an orthographic projection that so that OpenGL object
# coordinates are equal to window (pixel) coordinates.
pixel_coords = OrthographicProjection(left=0,right=screen.size[0],
                                      bottom=0,top=screen.size[1])

# Create a viewport on the screen
viewport = Viewport(screen,
                    size=screen.size,
                    projection=pixel_coords)

# Create an instance of the Target2D class with appropriate parameters
target = Target2D(size  = (25.0,10.0), 
                  color = (0.0,0.0,0.0,1.0)) # Set the target color (RGBA) black

# Tell the viewport to draw the target
viewport.add_stimulus(target)

# Create an instance of the Presentation class
p = Presentation(duration=(60,'frames'),viewports=[viewport])

#################################
#  Define controller functions  #
#################################

# A few variables used to calculate postion based on screen size
mid_x = screen.size[0]/2.0
mid_y = screen.size[1]/2.0
if screen.size[0] < screen.size[1]:
    max_vel = screen.size[0] * 0.4
else:
    max_vel = screen.size[1] * 0.4

def xy_as_function_of_frame(frame):
    t = float(frame) / fps
    return (max_vel*sin(0.1*2.0*math.pi*t) + mid_x,  # x
            max_vel*sin(0.1*2.0*math.pi*t) + mid_y ) # y

def orientation(dummy_argument):
    return 135.0

def on_during_experiment(t):
    if t < 0.0:
        return 0 # off between stimuli
    else:
        return 1 # on during stimulus presentation

#############################################################
#  Connect the controllers with the variables they control  #
#############################################################

p.add_realtime_frame_controller(target,'center', xy_as_function_of_frame)
p.add_transitional_controller(target,'orientation', orientation)
p.add_transitional_controller(target,'on', on_during_experiment)

#######################
#  Run the stimulus!  #
#######################

save_directory = os.path.join(VisionEgg.config.VISIONEGG_STORAGE,'movie')
if not os.path.isdir(save_directory):
    print "Error: cannot save movie, because directory '%s' does not exist."%save_directory
else:
    p.export_movie_go(frames_per_sec=fps,path=save_directory)
