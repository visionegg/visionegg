  .. _screenshots:

  Screenshots
  ###########

   All of the screenshots below were produced with demos that come with
   the Vision Egg.

   Multiple stimulus demo
   ----------------------

   multi_stim.py shows a color sinusoidal grating (viewed through a
   circular mask), a random dot stimulus, a perspective-distorted drum
   from the perspective of a moving camera, a gaussian-windowed
   sinusoidal grating (gabor wavelet), ''blitting'' of arbitrary pixels
   from a numeric array, and a (recursive) copy of the framebuffer.

   .. image:: multi_stim.jpg
      :width: 640
      :height: 480
      :alt: multi_stim.py screenshot

   QuickTime demo
   --------------

   You can use the Vision Egg to play QuickTime (currently Mac OS X only)
   and MPEG (all platforms) movies.  You can place them as normal
   textures, allowing you to reshape them, warp them with various
   distortions, or superimpose other graphics or text.

   .. image:: quicktime.jpg
      :width: 640
      :height: 480
      :alt: quicktime.py screenshot

   mouse_gabor_2d demo
   -------------------

   mouse_gabor_2d.py illustrates that stimuli are generated in realtime.
   Parameters such as spatial frequency and orientation can be updated
   without skipping a frame.

   .. image:: mouse_gabor_2d.jpg
      :width: 640
      :height: 480
      :alt: mouse_gabor_2d.py screenshot

   mouse_gabor_perspective demo
   ----------------------------

   mouse_gabor_perspective.py shows perspective distortion along with
   realtime stimulus generation.  Such wide fields of view are important
   for research on insects, for example, because many insects have a very
   large visual vield of view.  A grid of iso-azimuth and iso-elevation
   lines is superimposed on the grating in this screenshot.  This grid
   represents visual coordinates of a fixed observer looking at the
   middle of the screen.  A second, dimmer grid shows the reference
   coordinates system for the grating.

   .. image:: mouse_gabor_perspective.png
      :width: 640
      :height: 480
      :alt: mouse_gabor_perspective.py screenshot

   other demos
   -----------

   +-------------------------------------+-----------------------------------------+
   | lib3ds-demo                         | convert3d_to_2d                         |
   +=====================================+=========================================+
   |                                     |                                         |
   | 3D models in the .3ds (3D           | Coordinates given in 3D can be          |
   | Studio Max) format can be           | calulated to 2D screen coordinates.     |
   | loaded.  See the future_ page       | This may be useful for a number of      |
   | for more information regarding      | reasons, incluing pasting text over     |
   | complex 3D models.                  | important parts of a 3D scene.          |
   |                                     |                                         |
   | .. _future: future.html             |                                         |
   |                                     |                                         |
   +-------------------------------------+-----------------------------------------+
   |                                     |                                         |
   | .. image:: lib3ds-demo.jpg          | .. image:: convert3d_to_2d.jpg          |
   |    :width: 320                      |    :width: 320                          |
   |    :height: 240                     |    :height: 240                         |
   |    :alt: lib3ds-demo.py screenshot  |    :alt: convert3d_to_2d.py screenshot  |
   |                                     |                                         |
   +-------------------------------------+-----------------------------------------+

   Electrophysiology GUI
   ---------------------

   The ephys_gui and ephys_server are your gateway to electrophysiology
   experiments using the Vision Egg.  Because I am an
   electrophysiologist, this is where I have optimized the user
   interface.  There is a modular design which allows you to copy any of
   the existing experiment ''modules'' and use them as a template for
   generating your own experiment using any of the built-in stimulus
   types.

   The first screenshot shows the stimuli included by default, the main
   window with parameter entry for the spinning drum experiment, and the
   stimulus onset timing calibration window.

   .. image:: ephys_gui.png
      :width: 762
      :height: 632
      :alt: ephys_gui.pyw screenshot 1

   The screenshot below shows the perspective-distored sinusoidal grating
   experiment and the sequencer in use.

   .. image:: ephys_gui2.png
      :width: 710
      :height: 910
      :alt: ephys_gui.pyw screenshot 2

   The screenshot below shows that you have the ability to load parameter
   files and re-play them.  Also a particular trial can be (re)played as
   an image sequence so you can turn it into a movie.

   .. image:: ephys_gui3.png
      :width: 702
      :height: 534
      :alt: ephys_gui.pyw screenshot 3

   Starting the Vision Egg
   -----------------------

   This is the introductory window for any Vision Egg program.  (It's
   appearance can also be turned off.)

   .. image:: init_gui.png
      :width: 761
      :height: 631
      :alt: init window
