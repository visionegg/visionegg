This directory contains several demonstration scripts for the Vision
Egg library.  Most of these demos are merely a feature overview of the
Vision Egg, are not meant to be used for experiments.

You can rename the files from *.py to *.pyw so they don't open a
console window.  On Mac OS X this may be required (depending on how
Python is configured).

The metaPyroServer.py and metaPyroGUI.py scripts are the easiest place
to get started creating a complete experiment generation application
using a pure Python approach.  These demos are advanced and attempt to
"put it all together".  The ephys_server.py and ephys_gui.py
applications one step farther.

Another example of a script that could be used for experiments is the
gratingTCP script in the tcp directory.  This can be controlled by
gratingGUI, the LabView VIs contributed by Jamie Theobald, or your own
program.  See trigger_out in the daq directory to see how you could
combine it with triggering for easy integration into your current data
acquisition system.

Contents:
---------

color_grating.py -- Colored sine wave grating in circular mask
displayText.py -- Display text strings
dots.py -- Random dot stimulus
ephys_gui.py -- Client GUI application for electrophysiology experiments
ephys_server.py -- Server application for electrophysiology experiments
gabor.py -- Sinusoidal grating in a gaussian mask
gamma.py -- Test whether your video drivers support setting gamma ramps
grating.py -- Sinusoidal grating calculated in realtime
image_sequence_fast.py -- Display a sequence of images using a pseudo-blit routine
image_sequence_slow.py -- Display a sequence of images
lib3ds-demo.py -- Demonstrate the loading of .3ds file using the lib3ds library
makeMovie.py -- Save movie of a black target moving across a white background
mouseTarget.py -- Control a target with the mouse, get SDL/pygame events
movingPOV.py -- 2 viewports, one with a changing perspective
plaid.py -- Multiple sinusoidal gratings (with mask)
sphereGratingWindowed.py -- Perspective-distorted sin grating in gaussian window
sphereMap.py -- Mapping of texture onto sphere
target.py -- A moving target
targetBackground.py -- Moving target over a spinning drum
texture.py -- Load a texture from a file
textureDrum.py -- A texture-mapped spinning drum
visual_jitter.py -- Retinal slip demonstration

Pyro -- demo directory for remote control of Vision Egg programs
Pyro/simpleServer.py -- Very simple usage of Pyro (server)
Pyro/simpleClient.py -- Very simple usage of Pyro (client)
Pyro/gratingPyroServer.py -- Grating control with low-level Controllers (server)
Pyro/gratingPyroGUI.py -- Grating control with low-level Controllers (GUI client)
Pyro/metaPyroServer.py  -- Grating control with high-level meta-controller (server)
Pyro/metaPyroGUI.py -- Grating control with high-level meta-controller (GUI client)

daq -- demo directory for data acquisition
daq/trigger_in.py -- Use an external device to trigger the Vision Egg.
daq/trigger_out.py -- Use the Vision Egg to trigger an external device.

GUI -- demo directory for graphical user interfaces
GUI/drumDemoGUI.py -- Spinning drum with a graphical user interface (old).

tcp -- demo directory for control of Vision Egg over TCP
tcp/gratingTCP.py -- Start a Vision Egg TCPServer to control a grating
tcp/gratingGUI.py -- Python GUI to control gratingTCP