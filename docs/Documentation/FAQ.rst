Documentation/FAQ
#################

`[[Navigation(siblings)]]`_

.. contents::

I enter my desired framerate in the "What will your monitor refresh's rate be (Hz)" field of the Vision Egg startup GUI, but I get a different refresh rate.  Why?
==================================================================================================================================================================

The Vision Egg does not set your refresh rate, only the resolution. The refresh rate is determined automatically by your video drivers for the specified resolution.  So, you must tell your video drivers what the "proper" refresh rate for that resolution is.  In Windows, try switching to that resolution, change your refresh rate for that resolution, and go back to your original resolution, start the Vision Egg and see what happens. Also, PowerStrip_ from Entech may help significantly.

Unfortunately, setting the refresh rate would is OS and video driver dependent and is not something the Vision Egg does.  I think PowerStrip_ does a fantastic job on Windows, Mac OS X only seems to have a handful of video modes, and on linux and IRIX you can generate your own arbitrary modes, albeit not as easily as with PowerStrip_.

I am unable to open a graphics window.  I get the following exception: "pygame.error: Couldn't find matching GLX visual"
========================================================================================================================

An attempt was made to open a graphics window, but the requested mode was not found.  Try setting the total bit depth to 0 and each RGBA component to 0 to allow automatic matching.  Start with a small window (e.g. 640x480) and do not try fullscreen initially.

How to start without the configuration GUI appearing?
=====================================================

You have 2 options to start the VE without the configuration GUI. The first way is to replace the line  ``screen = get_default_screen()`` with the line ``screen = VisionEgg.Core.Screen( size = (600,600) )``. You may wish to specify more arguments as listed in the `Reference manual`_. The second is to set the environment variable VISIONEGG_GUI_INIT to 0.

I can not get the demos to work.  The GUI Graphics configuration launches correctly when I try grating.py but when I click "ok" a new gray window opens for a few seconds and then closes.  Can anyone help???
==============================================================================================================================================================================================================

Your version of Numeric may not be matched to the version with which PyOpenGL was built.  Install the Numeric version with which PyOpenGL was built, or rebuild PyOpenGL with your current version of Numeric.

How do I turn off the configuration window?
===========================================

Pick your method:

* Edit your config file.  The location of this file is in the window itself.

* Set the environment variable VISIONEGG_GUI_INIT=0.

* Add the following to your script before you create the screen:

    ``import VisionEgg; VisionEgg.config.VISIONEGG_GUI_INIT = 0`` (or ``from VisionEgg import *; config.VISIONEGG_GUI_INIT = 0``)

Note that all variables in VisionEgg_.config can be modified this way. Please see the documentation for the Configuration module for more information.

I have set up my PC with a dual boot and have been gradually getting used to Linux.  I would like to make the transition solely to Linux and the open source movement.  However, I am running into one dependency problem after another and have tried RPM and tar.gz files.  I even have a few experienced Linux users around and we still can not get all the dependencies installed.
=======================================================================================================================================================================================================================================================================================================================================================================================

Even though I like the package manager of my preferred linux distribution (Debian), I often install Python packages myself, particularly when I run into trouble like this. Also, experience on a number of platforms has convinced me that it allows me to be most platform-independent to use Python's distutils (simple command-line interface) for installing Python packages.  Python's distutils system is the same across all Python platforms and versions back to 1.5.7, and there are countless Python packages you'll find in source form but won't be packaged for individual operating systems.

I do use the binary package manager of my linux system for the python executable and sometimes other packages if they're available.  If they're not immediately available (or functioning) I use Python's distutils.

If you have issues with a particular dependency, try sending a message to the appropriate mailing list.

How do I specify where on my screen the display should go?  If I  create a window, I know how to direct the graphics to a certain location within that window, but how do I set the position of the window itself?
==================================================================================================================================================================================================================

The screen position is determined automatically by the OS, I think. SDL (which is wrapped by pygame, which is wrapped by the Vision Egg) has some environment variables which are supposed to allow specification of screen position. see: http://www.freelists.org/archives/visionegg/08-2003/msg00000.html

Unfortunately, I think these environment variables aren't "officially supported" in SDL, and thus are subject to future non inclusion.  (In fact, a recent build of pygame/SDL on Windows XP seems to ignore them, which I was planning on following up... Wait, it looks like it's discussed here: http://www.devolution.com/pipermail/sdl/2005-April/068395.html )

When using certain stimuli, including the demo versions of the moving grating and put_pixels, I sometimes see an artifact that travels from the bottom of the window to the top.  It usually looks like a slightly jagged line, and usually travels across the entire screen slowly to the top.  I'm not sure if this is a programming issue or something that is specific to my monitor.  It's an LCD monitor running at 60Hz, and that's what vision egg is set to use.
=========================================================================================================================================================================================================================================================================================================================================================================================================================================================================

This is the well-known 'tearing' artifact. Googling that should give you a better idea of what the problem is. You can either try to fix it by clicking the "sync buffer swaps to vertical retrace" button on the Vision Egg initial GUI popup window, or by forcing this (often called "VSync") in your video drivers. If you need further help, let us know, and be sure to specify your OS and video card.

When I run a stand-alone VisionEgg windows executable created with py2exe, I get the error "IOError: [Errno 2] No such file or directory: '...library.zip\\OpenGL\\version'
===========================================================================================================================================================================

The problem is that distutils does not copy non-python resources, and pyOpenGL expects a "version" file to be installed next to ``OpenGL\__init__.py``. The most straight-forward solution is to patch ``OpenGL\__init__.py`` with a try/except block around the code that opens the version file, as described here: `Mike Fletcher post to python-list`_

Line 13:17 of ``OpenGL.__init__.py``, replace with:

::

   try:
        filename = os.path.join(os.path.dirname(__file__), 'version')
        __version__ = string.strip(open(filename).read())
   except Exception, err:
        __version__ = '2.0.2.02'

After applying this patch rebuild the application with py2exe.

What are my anti-aliased points appearing as squares (instead of circles)?
==========================================================================

Support for antialiased points is driver dependent. The details on this web page are extremely helpful:

http://homepage.mac.com/arekkusu/bugs/invariance/HWAA.html

An alternative is  the `gluDisk()`_ utility function:

::

           quad = gluNewQuadric()
           gluQuadricDrawStyle(quad, GLU_FILL)
           ...
           gluDisk(quad, 0, 0.1, 50, 1)
           ...
           gluDeleteQuadric(quad)

This creates a disk with zero inner radius, 0.1 outer radius, 50 slices, one loop. Note that the radius dimension is in world dimensions, whereas the glPointSize() call uses pixel dimensions.

You can use this construct in conjunction with display lists to improve rendering efficiency:

::

       def initDisk(self):
           """ Call this function from your constructor or other initialization code. """
           quad = gluNewQuadric()
           gluQuadricDrawStyle(quad, GLU_FILL)

           # Construct representative disk
           self.diskList = glGenLists(1)
           glNewList(self.diskList, GL_COMPILE)
           gluDisk(quad, 0, 0.1, 50, 1)
           glEndList()
           gluDeleteQuadric(quad)

       def draw(self):
           ...
           # Move to the place where you want your disk/point
           glTranslate(x, y, 0)
           # Render disk
           glCallList(self.diskList)
           ...

.. ############################################################################

.. _PowerStrip: http://www.entechtaiwan.com/ps.htm

.. _Reference manual: http://visionegg.org/reference/VisionEgg.Core.Screen-class.html

.. _Mike Fletcher post to python-list: http://mail.python.org/pipermail/python-list/2005-September/300801.html

.. _gluDisk(): http://pyopengl.sourceforge.net/documentation/manual/gluDisk.3G.html

