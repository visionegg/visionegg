This directory contains several demonstration scripts for the Vision
Egg library.  Most of these demos are merely a feature overview of the
Vision Egg, are not meant to be used for experiments.

The closest example of a script that could be used for experiments is
the gratingTCP script in the tcp directory.  This can be controlled by
gratingGUI or your own program.  See trigger_out in the daq directory
to see how you could combine it with triggering for easy integration
into your current data acquisition system.

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

Pyro -- demo directory for remote control of Vision Egg programs
Pyro/simpleServer.py -- Very simple usage of Pyro (server)
Pyro/simpleClient.py -- Very simple usage of Pyro (client)
Pyro/gratingPyroServer.py -- Grating control with low-level Controllers (server)
Pyro/gratingPyroGUI.py -- Grating control with low-level Controllers (GUI client)
Pyro/metaPyroServer.py  -- Grating control with high-level meta-controller (server)
Pyro/metaPyroGUI.py -- Grating control with high-level meta-controller (GUI client)

calibrate -- demo directory with luminance calibration utilities
(own README.txt)

daq -- demo directory for data acquisition
daq/trigger_in.py -- Use an external device to trigger the Vision Egg.
daq/trigger_out.py -- Use the Vision Egg to trigger an external device.
daq/tcp/demo_gui_lab.py -- Integrated data acquisition/stimulus control

GUI -- demo directory for graphical user interfaces
GUI/drumDemoGUI.py -- Spinning drum with a graphical user interface (old).

tcp -- demo directory for control of Vision Egg over TCP
(own README.txt)