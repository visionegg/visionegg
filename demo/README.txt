This directory contains several demonstration scripts for the Vision
Egg library.  These scripts are not meant to be used for experiments,
but rather to demonstrate most of the features of the Vision Egg.

Contents:
---------

displayText.py -- Display text strings.
grating.py -- Sinusoidal grating calculated in realtime.
makeMovie.py -- Save movie of a black target moving across a white background.
mouseTarget.py -- Control a target with the mouse, get SDL/pygame events.
movingPOV.py -- 2 viewports, one with a changing perspective.
perspectiveGrating.py -- Perspective-distorted sinusoidal grating.
target.py -- A moving target.
targetBackground.py -- Moving target over a spinning drum.
texture.py -- Load a texture from a file.
textureDrum.py -- A texture-mapped spinning drum.

GUI -- demo directory for graphical user interfaces
GUI/drumDemoGUI.py -- Spinning drum with a graphical user interface (old).

Pyro -- demo directory for Python Remote Objects
Pyro/simpleServer.py -- Run a simple VisionEgg Pyro server (old).
XXX Pyro not done yet

daq -- demo directory for data acquisition
daq/trigger_in.py -- Use an external device to trigger the Vision Egg.
daq/trigger_out.py -- Use the Vision Egg to trigger an external device.

tcp -- demo directory for control of Vision Egg over TCP
tcp/gratingTCP.py -- Sinusoidal grating under network control.