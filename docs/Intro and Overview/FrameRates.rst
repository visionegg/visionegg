Intro and Overview/FrameRates
#############################

`[[Navigation(siblings)]]`_

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   There are two different values which both get called ''frame rate''.
   The first is the number of frames a graphics card draws to its
   framebuffer per second.  The second is the number of frames per second
   drawn on a monitor from the graphics card.  The frame rate of the
   monitor is a constant set by video drivers, and the frame rate of
   drawing to the framebuffer is determined by how long it takes for a
   particular program to complete all the elements in a scene.
   Obviously, it is a waste of resources to draw more frames to the
   framebuffer than will be displayed on the monitor, although in some
   cases there may be reasons for doing so.  (For example, if program
   control and drawing are done in the same loop, the control latency
   will be shorter at faster frame rates. Benchmarking 3D games or
   graphics cards is another reason why one might want to do this.)  For
   the rest of this document, ''frame rate'' will refer to the refresh
   rate of the monitor.

   The absolute upper limit of the monitor's frame rate is specified by
   the ''maximum vertical refresh frequency''.  In typical professional
   displays this value may be 160 Hz. Several support 180 Hz, and a few
   (such as the LGE Flatron 915 FT Plus) go up to 200 Hz. Unfortunately,
   your video driver may only allow certain pre-defined frame rates.  See
   below and the installation details page of your platform for
   platform-specific information about setting monitor refresh rates.

   What frame rate do you want? If your stimulus involves high-speed
   motion, more frames per second is better, simply because it reduces
   temporal aliasing.  At a minimum, your monitor's flicker rate (equal
   to frame rate on a CRT) should exceed the flicker fusion frequency of
   your subject.

   If your stimulus involves slow motion and your system can only move
   on-screen objects in integer pixel increments (this is not the case
   with the Vision Egg), you again want a high frame rate to maximize the
   smoothness of motion if an object must alternately move an integer
   number of pixels and then remain in place.

   With these arguments in favor of high frame rates, why might you want
   slower frame rates?  It is easier on the (typically analog) electronic
   circuitry involved in the production and amplification of the video
   signal, and therefore square edges on waveforms will be closer to
   truly square, producing better spatial crispness.  You may be able to
   draw more pixels per frame at a slower frame rate because of
   limitations in your monitor's ''horizontal refresh frequency'' and
   ''pixel bandwidth'' in addition to your video card's ''RAMDAC/pixel
   clock''.

   Platform-specific tools to create custom video modes
   ----------------------------------------------------

   XFree86, the video driver for linux, lets the user specify exactly the
   timing parameters of the video signal in the ''modeline'' section of the
   XF86Config file.

   For Windows, RefreshForce_ (freeware) is very useful. PowerStrip_
   (shareware) allows arbitrary setting of video mode. Furthermore,
   `Refresh Rate Fixer`_ may be of use.

   On Mac OS X, switchResX_ may provide a way to set the frame rate other
   than the default values.

   SGI IRIX has its own video mode tools such as setmon which allow
   arbitrary video modes to be produced.

   The `XFree86 Video Timing HOWTO`_ is an excellent resource for
   understanding the intricacies of the timing of video signals, even if
   you don't use X windows.

   Multi-tasking operating systems and dropped frames
   --------------------------------------------------

   The simplest way to guarantee that your monitor is updated on every
   frame is to put the control and drawing routines in a loop which
   cannot be interrupted.  This can be done with special graphics cards
   which have an on-board processor separate from the computer's main
   CPU, or in operating systems which give programs complete control of
   the CPU.  Unfortunately, OpenGL graphics cards must be controlled from
   the CPU, and most modern operating systems have a kernel which can
   suspend any program. There is the (currently untried) possbility of
   running the Vision Egg on a system with a realtime OS which would also
   solve the problem completely.

   We believe the Vision Egg, or another OpenGL solution which has the
   ability to move objects in sub-pixel increments, provides the absolute
   best way to produce smooth motion.

   .. _RefreshForce: http://www.pagehosting.co.uk/rf
   .. _PowerStrip: http://www.entechtaiwan.com/ps.htm
   .. _`Refresh Rate Fixer`: http://www.radeon2.ru/refreshfix_eng.html
   .. _switchResX: http://www.madrau.com/html/SRX/indexSRX.html
   .. _`XFree86 Video Timing HOWTO`: http://www.tldp.org/HOWTO/XFree86-Video-Timings-HOWTO

