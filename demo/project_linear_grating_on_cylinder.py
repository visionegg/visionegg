"""

project a linear grating onto a cylinder

This script draws a linear sinusoidal grating (on a rectangle
positioned in 3D space). The grating is then viewed through many
individual viewports approximating the appearance of being projected
onto a cylinder.

Details on the coordinate transforms are given below.

This script does not make use of the VisionEgg.FlowControl module but
rather performs the flow control itself.

This is a demo script for the Vision Egg realtime visual stimulus
generation library.

"""

from __future__ import division
import VisionEgg
VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()

from VisionEgg.Core import get_default_screen, Viewport,\
    SimplePerspectiveProjection, FrameTimer, swap_buffers
import pygame
from pygame.locals import QUIT, KEYDOWN, MOUSEBUTTONDOWN
from VisionEgg.Text import Text
from VisionEgg.Gratings import SinGrating3D
from math import pi, sin, cos
import numpy

screen = get_default_screen()
screen.parameters.bgcolor = (0.0,0.0,0.0) # black (RGB)

stimulus = SinGrating3D(
    spatial_freq=20.0,
    temporal_freq_hz=1.0,
    upperleft=(-5,  .25, -1),
    lowerleft=(-5, -.25, -1),
    lowerright=(5, -.25, -1),
    upperright=(5,  .25, -1),
    )

text = Text( text = "Vision Egg project_linear_grating_on_cylinder demo.",
             position = (screen.size[0]/2,2),
             anchor = 'bottom',
             color = (1.0,1.0,1.0))

# use default 2D pixel-coordinate projection for text
overlay_viewport = Viewport(screen=screen,
                            stimuli=[text])


num_viewports = 20
arc_degrees = 150 # angle of display

D2R = pi/180.0
arc = arc_degrees*D2R
arc_center = arc/2
viewport_arc = arc/num_viewports
eye = (0,0,0)
camera_up = (0,1,0)
viewports = []

# The center of the screen is looking, in 3D world coordinates, at -z,
# with +y up and +x right. In cylindrical coordinates, the -z axis
# corresponds with theta = 0 and the +y axis corresponds with +h, and
# theta increases from right to left. In screen coordinates, 0,0 is
# the lower left.

# Computer lower left corner of viewports (in screen coordinates).
lowerlefts = numpy.linspace(0,screen.size[0],num=(num_viewports+1))[::-1]
lowerlefts.astype(int)
height = screen.size[1]
fov_x = viewport_arc/D2R
fov_y = 30.0
aspect_ratio = fov_x/fov_y
# setup the projections and viewports
for i in range(num_viewports):
    
    # Compute viewport coordinates (in cylindrical coordinates).
    theta1 = i*viewport_arc - arc_center
    theta2 = (i+1)*viewport_arc - arc_center
    theta = (theta1 + theta2)/2

    # Compute camera coordinates (in 3D world coordinates).
    x = -sin(theta)
    z = -cos(theta)
    camera_look_at = (x,0,z)

    # Now setup the projection and the viewport.
    ll = int(lowerlefts[i+1])
    width = int(lowerlefts[i]-ll)
    projection = SimplePerspectiveProjection(fov_x=fov_x,
                                             aspect_ratio=aspect_ratio)
    projection.look_at( eye, camera_look_at, camera_up )
    viewport = Viewport(screen=screen,
                        projection=projection,
                        stimuli=[stimulus],
                        anchor='lowerleft',
                        position=(ll,0),
                        size=(width,height))
    viewports.append(viewport)
# list of viewports, drawn in order, so overlay viewport goes last
viewports.append( overlay_viewport )

frame_timer = FrameTimer()
quit_now = False
while not quit_now:
    for event in pygame.event.get():
        if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
            quit_now = True
    screen.clear()
    for v in viewports:
        v.draw()
    swap_buffers()
    frame_timer.tick()
frame_timer.log_histogram()

im = screen.get_framebuffer_as_image(buffer='front')
im.save('project_linear_grating_on_cylinder.png')
