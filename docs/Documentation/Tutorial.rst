Documentation/Tutorial
######################

`[[Navigation(siblings)]]`_

.. contents::

Overview
========

This page describes a few of the many of the demo scripts included with the Vision Egg.  Click on the images to see a 320x240 12 frame per second QuickTime_ movie of the output of the Vision Egg.  Note that this is very small and slow compared to what you would see running the same demo on your computer, especially in fullscreen mode.  These demos and many more are a DownloadAndInstall_ away.

grating.py
==========

The grating demo is a simple Vision Egg application script to show basic operation.  First, the screen is initialized, which opens the OpenGL window. Second, a grating object is created with specified parameters of size, position, spatial frequency, temporal frequency, and orientation. Next, a viewport object is created, which is an intermediary between stimuli and screens.  Finally, a presentation object is created, which controls the main loop and realtime behavior of any Vision Egg script.

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   .. image:: grating-small.jpg
      :width: 320
      :height: 240
      :alt: grating.py screenshot
      :target: http://visionegg.org/movies/grating.mov

::

   #!/usr/bin/env python
   """Sinusoidal grating calculated in realtime."""
   ############################
   #  Import various modules  #
   ############################
   import VisionEgg
   VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
   from VisionEgg.Core import *
   from VisionEgg.FlowControl import Presentation
   from VisionEgg.Gratings import *
   #####################################
   #  Initialize OpenGL window/screen  #
   #####################################
   screen = get_default_screen()
   ######################################
   #  Create sinusoidal grating object  #
   ######################################
   stimulus = SinGrating2D(position         = ( screen.size[0]/2.0, screen.size[1]/2.0 ),
                           anchor           = 'center',
                           size             = ( 300.0 , 300.0 ),
                           spatial_freq     = 10.0 / screen.size[0], # units of cycles/pixel
                           temporal_freq_hz = 1.0,
                           orientation      = 45.0 )
   ###############################################################
   #  Create viewport - intermediary between stimuli and screen  #
   ###############################################################
   viewport = Viewport( screen=screen, stimuli=[stimulus] )
   ########################################
   #  Create presentation object and go!  #
   ########################################
   p = Presentation(go_duration=(5.0,'seconds'),viewports=[viewport])
   p.go()

target.py
=========

The target demo creates a small target which moves across the screen.  The target is spatially anti-aliased by default, meaning that the edges can have colors intermediate between the target and the background to reduce *jaggies*.  This demo also introduces the concept of *controllers* which allow realtime control of a Vision Egg stimulus through any number of means, including a data acquisition device, a network connection, or software control.

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   .. image:: target-small.jpg
      :width: 320
      :height: 240
      :alt: target.py screenshot
      :target: http://visionegg.org/movies/target.mov

::

   #!/usr/bin/env python
   """A moving target."""
   ############################
   #  Import various modules  #
   ############################
   import VisionEgg
   VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
   from VisionEgg.Core import *
   from VisionEgg.FlowControl import Presentation, Controller, FunctionController
   from VisionEgg.MoreStimuli import *
   from math import *
   #################################
   #  Initialize the various bits  #
   #################################
   # Initialize OpenGL graphics screen.
   screen = get_default_screen()
   # Set the background color to white (RGBA).
   screen.parameters.bgcolor = (1.0,1.0,1.0,1.0)
   # Create an instance of the Target2D class with appropriate parameters.
   target = Target2D(size  = (25.0,10.0),
                     color      = (0.0,0.0,0.0,1.0), # Set the target color (RGBA) black
                     orientation = -45.0)
   # Create a Viewport instance
   viewport = Viewport(screen=screen, stimuli=[target])
   # Create an instance of the Presentation class.  This contains the
   # the Vision Egg's runtime control abilities.
   p = Presentation(go_duration=(10.0,'seconds'),viewports=[viewport])
   #######################
   #  Define controller  #
   #######################
   # calculate a few variables we need
   mid_x = screen.size[0]/2.0
   mid_y = screen.size[1]/2.0
   max_vel = min(screen.size[0],screen.size[1]) * 0.4
   # define position as a function of time
   def get_target_position(t):
       global mid_x, mid_y, max_vel
       return ( max_vel*sin(0.1*2.0*pi*t) + mid_x , # x
                max_vel*sin(0.1*2.0*pi*t) + mid_y ) # y
   # Create an instance of the Controller class
   target_position_controller = FunctionController(during_go_func=get_target_position)
   #############################################################
   #  Connect the controllers with the variables they control  #
   #############################################################
   p.add_controller(target,'position', target_position_controller )
   #######################
   #  Run the stimulus!  #
   #######################
   p.go()

targetBackground.py
===================

The targetBackground demo illustrates how easy it is to combine multiple stimuli. A spatially anti-aliased small target is drawn as before, but this occurs over a spinning drum.

This demo also introduces more power of OpenGL -- coordinate transforms that occur in realtime via projections. In the Vision Egg, a projection is a parameter of the viewport.  In the default case (such as for the small target), the viewport uses pixel coordinates to create an orthographic projection. This allows specification of stimulus position and size in units of pixels. However, a projection also allows other 3D to 2D projections, such as that used to draw the spinning drum.  This drum, which is defined in 3D, is drawn using a perspective projection.  Because the drum uses a different projection than the small target, it needs its another viewport to link it to the screen.

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

    .. image:: targetBackground-small.jpg
       :width: 320
       :height: 240
       :alt: targetBackground.py screenshot
       :target: http://visionegg.org/movies/targetBackground.mov

::

   #!/usr/bin/env python
   """Moving target over a spinning drum."""
   ############################
   #  Import various modules  #
   ############################
   from VisionEgg import *
   start_default_logging(); watch_exceptions()
   from VisionEgg.Core import *
   from VisionEgg.FlowControl import Presentation, Controller, FunctionController
   from VisionEgg.MoreStimuli import *
   from VisionEgg.Textures import *
   import os
   from math import *
   # Initialize OpenGL graphics screen.
   screen = get_default_screen()
   #######################
   #  Create the target  #
   #######################
   # Create an instance of the Target2D class with appropriate parameters
   target = Target2D(size  = (25.0,10.0),
                     color      = (1.0,1.0,1.0,1.0), # Set the target color (RGBA) black
                     orientation = -45.0)
   # Create a viewport for the target
   target_viewport = Viewport(screen=screen, stimuli=[target])
   #####################
   #  Create the drum  #
   #####################
   # Get a texture
   filename = os.path.join(config.VISIONEGG_SYSTEM_DIR,"data","panorama.jpg")
   texture = Texture(filename)
   # Create an instance of SpinningDrum class
   drum = SpinningDrum(texture=texture,shrink_texture_ok=1)
   # Create a perspective projection for the spinning drum
   perspective = SimplePerspectiveProjection(fov_x=90.0)
   # Create a viewport with this projection
   drum_viewport = Viewport(screen=screen,
                            projection=perspective,
                            stimuli=[drum])
   ##################################################
   #  Create an instance of the Presentation class  #
   ##################################################
   # Add target_viewport last so its stimulus is drawn last. This way the
   # target is always drawn after (on top of) the drum and is therefore
   # visible.
   p = Presentation(go_duration=(10.0,'seconds'),viewports=[drum_viewport,target_viewport])
   ########################
   #  Define controllers  #
   ########################
   # calculate a few variables we need
   mid_x = screen.size[0]/2.0
   mid_y = screen.size[1]/2.0
   max_vel = min(screen.size[0],screen.size[1]) * 0.4
   # define target position as a function of time
   def get_target_position(t):
       global mid_x, mid_y, max_vel
       return ( max_vel*sin(0.1*2.0*pi*t) + mid_x , # x
                max_vel*sin(0.1*2.0*pi*t) + mid_y ) # y
   def get_drum_angle(t):
       return 50.0*math.cos(0.2*2*math.pi*t)
   # Create instances of the Controller class
   target_position_controller = FunctionController(during_go_func=get_target_position)
   drum_angle_controller = FunctionController(during_go_func=get_drum_angle)
   #############################################################
   #  Connect the controllers with the variables they control  #
   #############################################################
   p.add_controller(target,'position', target_position_controller )
   p.add_controller(drum,'angular_position', drum_angle_controller )
   #######################
   #  Run the stimulus!  #
   #######################
   p.go()

put_pixels.py
=============

The put_pixels demo puts arbitrary array data to the screen.  For the sake of simplicity this example uses only solid, uniformly colored arrays. The screen is updated with a new array on every frame, which will reveal tearing artifacts if you do not have buffer swaps synchronized to VSync.

This demo also illustrates an alternative to using the FlowControl_ module by using pygame's event handling.

::

   #!/usr/bin/env python
   import VisionEgg
   VisionEgg.start_default_logging(); VisionEgg.watch_exceptions()
   from VisionEgg.Core import *
   import pygame
   from pygame.locals import *
   screen = get_default_screen()
   screen.set( bgcolor = (0.0,0.0,0.0) ) # black (RGB)
   white_data = (Numeric.ones((100,200,3))*255).astype(Numeric.UnsignedInt8)
   red_data = white_data.copy()
   red_data[:,:,1:] = 0 # zero non-red channels
   blue_data = white_data.copy()
   blue_data[:,:,:-1] = 0 # zero non-blue channels
   frame_timer = FrameTimer() # start frame counter/timer
   count = 0
   quit_now = 0
   # This style of main loop is an alternative to using the
   # VisionEgg.FlowControl module.
   while not quit_now:
       for event in pygame.event.get():
           if event.type in (QUIT,KEYDOWN,MOUSEBUTTONDOWN):
               quit_now = 1
       screen.clear()
       count = (count+1) % 3
       if count == 0:
           pixels = white_data
       elif count == 1:
           pixels = red_data
       elif count == 2:
           pixels = blue_data
       screen.put_pixels(pixels=pixels,
                         position=(screen.size[0]/2.0,screen.size[1]/2.0),
                         anchor="center")
       swap_buffers() # display what we've drawn
       frame_timer.tick() # register frame draw with timer
   frame_timer.log_histogram()

Many more demos are included!
=============================

.. ############################################################################

.. _QuickTime: http://www.apple.com/quicktime/

