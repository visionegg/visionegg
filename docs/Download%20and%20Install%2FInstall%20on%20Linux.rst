#format rst

`[[Navigation(siblings)]]`_

Quickstart for Ubuntu Hardy Heron (8.04)
========================================

You can use my repository which includes a .deb package of the Vision Egg, integrated with the Ubuntu repositories for dependencies. See the  `"Ubuntu packages" instructions on the motmot wiki`_. (This wiki is generally about other software I wrote, but you can skip steps 8-10 and install python-visionegg instead.) Note that this package only installs the Vision Egg library. To get the demos or documentation, download the source package. -- Andrew Straw

More general instructions
=========================

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::


   Here are the all the steps in detail required to get the Vision Egg to
   run on your linux system.

   **This page details the build-from-source approach. Your linux
   distribution probably has these packages available to your package
   manager.**

   ======
   OpenGL
   ======

   OpenGL is probably already installed on your system.  If you're
   running linux, the tricky part may be getting hardware
   acceleration.  This is accomplished by getting your X Windows
   server into hardware accelerated mode.  This is beyond the scope of
   this document, but there are many good documents on the internet.

   =================
   Installing Python
   =================

   Python installation is straightforward, with ample documentation.
   Your particular distribution of linux probably comes with Python
   installed, but in case it doesn't, or if the Vision Egg doesn't work
   with your distribution's version of Python, these instructions detail
   building Python from the C source.  These instructions were written
   for Python 2.1.1, but Python 2.2.1 is nearly identical.

   The Python website is http://www.python.org

   To build from source, unpack using the usual gunzip and tar
   routine. In the expanded Python source directory run ''./configure''.
   Then type ''make''.  You can test Python by running ''make test''. If
   all goes well, type ''make install''.

   By default, building from the source does not compile Tkinter support.
   Tkinter is very useful for creating GUIs in Python, and the Vision
   Egg, especially a few demo programs, uses it.  The core functionality
   of the Vision Egg will work without Tkinter, but it's best to get it
   working at this stage. Edit the Modules/Setup file in the Python
   source directory, look for ''_tkinter'', and uncomment the various
   lines needed to get it to compile.  Run ''make'' again in the root of
   the source directory to get _tkinter to compile and then ''make
   install'' (again) to install it.

   ==========================
   Installing Python packages
   ==========================

   Installing Numeric Python
   -------------------------

   The Numeric Python website is http://numpy.sourceforge.net

   For Numeric-21.0, run ''python setup.py install''

   For Numeric-20.0, make sure to run ''setup_all.py''.  In addition to
   the basic Numeric modules, this command makes the FFT and other
   libraries, which are very useful, but not needed by the Vision Egg.
   (These extra modules are made by default in release 21.)

   Installing Python Imaging Library (PIL)
   ---------------------------------------

   The PIL download area is http://www.secretlabs.com/downloads/index.htm#pil

   Imaging-1.1.2 was used for development.

   Unfortunately, PIL can be tricky to install.
   The detailed instructions in the README are pretty good, but this package
   can be a bit tricky to install.

   The shell commands I use to build the Imaging packages are:

   ::

     cd Imaging-1.1.2/libImaging/
     ./configure
     make
     cd ..
     make -f Makefile.pre.in boot
     make

   If you have errors with the ''make'' step that say something like ''tk8.0''
   not found, open ''Makefile'' and change ''tk8.0'' to ''tk8.3'' and ''tcl8.0''
   to ''tcl8.3''.  Of course this assumes you have version 8.3 of tk and tcl.
   If you don't have tcl, open the ''Setup'' file and comment out the
   ''_imagingtk'' lines.

   If you have errors with the ''make'' step that say something like ''can't
   locate file: -ljpeg'', download and install those libraries or comment
   out the appropriate lines in ''Setup''.  I've had trouble trying to build
   with those lines removed from the ''Setup'' file, so I just downloaded
   and installed the libraries.  These libraries are very easy to compile
   and install.  Just run ''./configure'' and ''make install''.  Under Mac OS
   X, I couldn't get a static or shared library to compile from the sources,
   so I used the version that fink installed for me.

   If you have to edit ''Setup'', you'll have to run ''make -f Makefile.pre.in
   boot'' and ''make'' again.

   Now, Imaging is compiled, and you must copy the files to Python's local
   package directory.  (How to find out what it is?  It's usually
   ''/usr/lib/python2.1/site-packages'' or
   ''/usr/local/lib/python2.1/site-packages''.)

   ::

     cp PIL.pth /usr/lib/python2.1/site-packages
     mkdir /usr/lib/python2.1/site-packages/PIL
     cp *.so PIL/* /usr/lib/python2.1/site-packages/PIL

   Installing PyOpenGL
   -------------------

   PyOpenGL installation is well documented and straightforward in my
   experience in linux.  (Not necessarily so with other platforms!) I've
   had trouble getting the GL/ARB/texture_compression.i file to compile
   with the OpenGL headers that came with my nVidia card.  I have a patch
   that fixes this problem, if you're interested.

   Installing pygame
   -----------------

   The Vision Egg uses pygame as a Python binding to SDL.  SDL is used to
   initialize an OpenGL window in a cross platform way.  I have always
   had good fortune with distribution installed SDL, although building
   from source has always worked as well.

   Once SDL is installed, installation of pygame is straightforward using
   the Python distutils.  Just type ''python setup.py install'' from the
   pygame source directory.

   Install the Vision Egg
   ----------------------

   Install vision egg by changing to the base visionegg directory and
   execute ''python setup.py install''.  You will need appropriate
   privileges on your system to install.

   Check your installation with the ''check-config.py'' program.  Also
   run this script if you run into any installation errors.

.. ############################################################################

.. _"Ubuntu packages" instructions on the motmot wiki: http://code.astraw.com/projects/motmot#Ubuntupackages

