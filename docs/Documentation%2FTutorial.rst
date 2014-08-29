#format rst

`[[Navigation(siblings)]]`_

.. contents::

Overview
========

This page describes a few of the many of the demo scripts included with the Vision Egg.  Click on the images to see a 320x240 12 frame per second QuickTime_ movie of the output of the Vision Egg.  Note that this is very small and slow compared to what you would see running the same demo on your computer, especially in fullscreen mode.  These demos and many more are a DownloadAndInstall_ away.

grating.py
==========

The grating demo is a simple Vision Egg application script to show basic operation.  First, the screen is initialized, which opens the OpenGL window. Second, a grating object is created with specified parameters of size, position, spatial frequency, temporal frequency, and orientation. Next, a viewport object is created, which is an intermediary between stimuli and screens.  Finally, a presentation object is created, which controls the main loop and realtime behavior of any Vision Egg script.

