#format rst

.. contents:: :depth: 1

Frontiers in Neuroscience commentary - 2009-10-05
=================================================

Rolf Kötter wrote `A primer of visual stimulus presentation software`_ about the Vision Egg and PsychoPy_ for *Frontiers in Neuroscience*.

talk at SciPy 09 (video available online) - 2009-08-20
======================================================

AndrewStraw_ gave a talk on the Vision Egg and another piece of his software, Motmot_, at `SciPy 09`_. See the talk at http://www.archive.org/details/scipy09_day1_05-Andrew_Straw . The Vision Egg part starts at 25:18.

talk and tutorial at CNS*2009 - 2009-07-22
==========================================

AndrewStraw_ is giving a talk and demo/tutorial on the Vision Egg and another piece of his software, `the Motmot camera utilities`_ at `CNS*2009`_ at the `Python for Neuroinformatics Workshop`_.

Vision Egg 1.2.1 released - 2009-07-21
======================================

Get it from PyPI_ while it's hot.

Vision Egg article in Frontiers in Neuroinformatics - 2008-10-08
================================================================

An article about the Vision Egg has now been accepted for publication. The citation is:

* Straw, Andrew D. (2008) Vision Egg: An Open-Source Library for Realtime Visual Stimulus Generation. *Frontiers in Neuroinformatics*. doi: 10.3389/neuro.11.004.2008 link_

This article covers everything from descriptions of some of the high-level Vision Egg features, to low-level nuts-and-bolts descriptions of OpenGL and graphics hardware relevant for vision scientists. Also, there is an experiment measuring complete latency (from USB mouse movement to on-screen display). In the best configuration (a 140Hz CRT with vsync off), this latency averaged about 12 milliseconds.

If you use the Vision Egg in your research, I'd appreciate citations to this article.

BCPy2000, using the Vision Egg, released - 2008-10-01
=====================================================

The Vision Egg has found another application: Brain-Computer Interfaces.

Dr. Jeremy Hill (Max Planck Institute for Biological Cybernetics) announced the release of BCPy2000_, a framework for realtime biosignal analysis in python, based on the modular, popular (but previously pythonically challenged) BCI2000 project.

Vision Egg 1.1.1 released - 2008-09-18
======================================

This is primarily a bug fix release to Vision Egg 1.1.

Changes for 1.1.1
-----------------

* Various small bugfixes and performance improvements:

- Removed old CVS cruft from `VisionEgg/PyroClient`_.py `VisionEgg/PyroHelpers`_.py

- Fix trivial documentation bugs to have the correct version number.

- Workaraound pygame/SDL issue when creating Font objects. (r1491, reported by Jeremy Hill)

- bugfix: allow 4D as well as 3D vectors to specify vertices (r1472, r1474)

- fix comments: improve description of coordinate system transforms (r1473)

- Use standard Python idiom (r1475)

- Further removal of 'from blah import *' (r1476, r1501)

- Minor performance improvement (r1486)

- Remove unintended print statement (r1487 thanks to Jeremy Hill)

- properly detect String and Unicode types (r1470, reported by Dav Clark)

- update license to mention other code (r1502)

Vision Egg 1.1 released - 2008-06-07
====================================

This release brings the Vision Egg up to date with numpy and the new ctypes-based PyOpenGL, and includes lots of smaller bugfixes and removes old cruft that had been accumulating.

Changes for 1.1
---------------

* Explicitly require Python 2.3 by removing duplicate of Python standard library's logging module and assume the "True" and False" are defined. There were probably other assumptions depending on 2.3 creeping into the code, as well.

* Removed Lib3DS module.

* Workaround PyOpenGL 3.0.0a and 3.0.0b1 bug in glLoadMatrixf().

* Fix SphereMap_.AzElGrid_() to properly draw iso elevation and azimuth lines at specified intervals.

* Change to use numpy at the core instead of Numeric. (Require numpy, no longer require Numeric.)

* Require setuptools

* No longer supporting Python 2.2

* Update Textures to accept numpy arrays as data source (by Martin Spacek)

* Update to work with PyOpenGL 3

* Changes so to reflect standard idioms on Python project layouts: src/ directory renamed to VisionEgg/ (but .c files need to be moved back to src/), use 'package_data' distutils argument. This enables setuptools to work with the Vision Egg.

* QuickTime_ movies work in Windows (need to check on OS X).

* FilledCircle_ stimulus is now anti-aliased. Thanks to Peter Jurica and Gijs Plomp.

* Added demo/texture3D_alpha.py

Vision Egg 1.0 released - 2006-01-03
====================================

Changes for 1.0
---------------

* Major enhancements to the ephys server/GUI code to use normal (or slightly modified) demo scripts in this environment were one by Imran Ali and Lachlan Dowd in the lab of David O'Carroll at the University of Adelaide.

* An initial patch for stereo support sent by Yuichi Sakano and Kevin J. MacKenzie at York University.

* Parallel port enhancements by Hubertus Becker, University of Tübingen.

* Arrow and FilledCircle stimuli by Hubertus Becker, University of Tübingen.

* DaqKeyboard and ResponseControl by Hubertus Becker, University of Tübingen.

* Full screen anti-aliasing support (FSAA) by Mark Halko, Boston University.

* Various patches by Tony Arkles (University of Saskatchewan),  including a suggestion to separate camera motions from the GL_PROJECTION matrix and put them in the GL_MODELVIEW matrix, where they belong.

* Patch for VISIONEGG_SYSTEM_DIR by Nick Knouf, MIT. 

* Added win32_vretrace.WaitForRetrace() (but it's not used for much, yet)

* Enhancements to EPhys Server/GUI sequencer

* Added 'lat-long rectangle' to available 3D masking windows

* Moved controller.CONSTANTS into FlowControl module namespace

* Numerous bugfixes

Quest.py announced - 2005-04-08
===============================

The popular QUEST algorithm by Denis Pelli has been ported to Python. See the Quest_ page for more details.

Pylink (by SR Research) - Eye tracking in Python - 2004-02-25
=============================================================

`SR Research`_, the makers of eye tracking hardware and software, have released Pylink_.

Pylink can be used with the Vision Egg!

According to SR Research:

::

   Pylink allows for tracker control, real-time data access, and
   external synchronization with eye data via custom messaging.

   Many people find Python to be a simpler, yet still powerful,
   alternative to C.  Pylink can also be used in combination with the
   excellent third party open source Vision Egg software; providing a
   combined visual presentation and eye tracking scripting package.

Distributed with Pylink is a modified Vision Egg demo using realtime tracker data to move a Gaussian-windowed grating in a gaze-contingent fashion. Following this example, it should be easy to create other !VisionEgg/Pylink scripts for a variety of vision experiments involving eye tracking.

Release 0.9.9 - 2003-09-19
==========================

The Vision Egg 0.9.9 is here!

There are several major improvements. (The few changes that may break old code are detailed in the release notes included in this email).

There is nothing more I intend to add before I release Version 1.0 -- this is a release candidate subject to final testing and bug fixing, so I would appreciate all the abuse you can put it through. In particular, test/conform.py runs many tests on your system and reports the output.

Changes for 0.9.9:

* Screen.put_pixels() method for blitting of raw pixel data

* Support for QuickTime movies (currently Mac OS X only)

* Redesign of type check system for accuracy and clarity

* TrueType font rendering with SDL_ttf2

* Textures with alpha--bugfixes and examples

* Positioning of viewports and 2D stimuli can use relative positioning anchors

* Now requires Python 2.2 -- new style classes used to restrict attribute acccess

* Now requires pygame 1.5

* Renamed timing_func() to time_func()

* EPhysGUI saves absolute time a trial was started (to recontruct all stimuli)

* Allow use of pygame Surfaces as source of texture data

* Mipmaps of sphere-mapped sinusoidal grating to prevent spatial aliasing

* De-emphasis on Presentation and Controller classes (moved to FlowControl module)

* Changed orientations such that 0 degrees is right and 90 degrees is up.

* Bugfix in S!phereMap module -- gaussian formula produced windows too wide by 2/sqrt(2)

* Allow conversion of 3D vertices into 2D screen coordinates

* Added wireframe azimuth/elevation grid with text labels

* Allow arbitrary orientation of textures and text with angle parameter

* FrameTimer class now available for use in your own main loops

* Use Python 2.3 logging module (copy included for use with Python 2.2)

* No installation of demos or documentation (get source or demo package)

* Many small enhancements and bugfixes 

New tests:

* high-voltage regulation test for displays (Brainard et al., 2002)

* incomplete DC restoration test for displays (Brainard et al., 2002)

* unit-test suite: among many other things, pixel accuracy of textures 

New demos:

* mpeg.py plays MPEG movies (currently seeking a free movie to include)

* quicktime.py plays QuickTime movies (currently Mac OS X only)

* convert3d_to_2d.py converts 3D positions to 2D positions

* dots_simple_loop.py uses own loop rather than Presentation class

* makeMovie2.py makes a movie with get_framebuffer_as_image() function

* mouse_gabor_2d.py shows a gabor wavelet under mouse and keyboard control

* mouse_gabor_perspective.py is sphereGratingWindowed.py improved and renamed

* mouseTarget_user_loop.py uses own loop rather than Presentation class

* multi_stim.py shows many stimuli at once

.. ############################################################################

.. _A primer of visual stimulus presentation software: http://www.frontiersin.org/neuroscience/paper/10.3389/neuro.01/021.2009/

.. _PsychoPy: http://www.psychopy.org/

.. _AndrewStraw: ../AndrewStraw

.. _Motmot:
.. _the Motmot camera utilities: http://code.astraw.com/projects/motmot

.. _SciPy 09: http://conference.scipy.org/schedule

.. _CNS*2009: http://www.cnsorg.org/2009/

.. _Python for Neuroinformatics Workshop: http://www.cnsorg.org/2009/workshops/WS12_09_Muller_Web_announcement.pdf

.. _PyPI: http://pypi.python.org/pypi/visionegg

.. _link: http://frontiersin.org/neuroinformatics/paper/10.3389/neuro.11/004.2008/

.. _BCPy2000: http://bci2000.org/downloads/BCPy2000/

.. _VisionEgg/PyroClient: ../VisionEgg/PyroClient

.. _VisionEgg/PyroHelpers: ../VisionEgg/PyroHelpers

.. _SphereMap: ../SphereMap

.. _AzElGrid: ../AzElGrid

.. _QuickTime: ../QuickTime

.. _FilledCircle: ../FilledCircle

.. _Quest: ../Quest

.. _SR Research: http://www.eyelinkinfo.com/

.. _Pylink: http://www.eyelinkinfo.com/mount_software.php#Python

