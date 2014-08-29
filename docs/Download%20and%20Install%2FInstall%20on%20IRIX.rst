#format rst

Download and Install/Installation on IRIX
#########################################

`[[Navigation(siblings)]]`_

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   Installing the Vision Egg for SGI IRIX is similar to installing for
   linux. This document will covers mainly the differences from the linux
   installation process. I have installed the Vision Egg on IRIX64 6.5
   using SGI's cc compiler.

   Many of the tools used in the development of the Vision Egg are
   included on SGI's freeware distribution, so you might want to have
   that handy.  (Despite SGI's choice, ''freeware'' is not the best term
   for open source software.  ''Open source software'' has a couple more
   syllables, but is probably preferred by the authors of open source
   software, including the Vision Egg!)  This method makes extensive use
   of SGI's Software Manager to install as much of the basic software as
   possible. Undoubtedly, because all of this software is open source,
   you could compile it yourself, as well.

   Installing Python
   -----------------

   Python compiles without trouble from the source, but I've had troubles
   getting the Tkinter module compiled.  Therefore, I've been using
   precompiled Python from SGI's ''freeware'' distribution.

   Installing Python Imaging Library (PIL)
   ---------------------------------------

   I've had the following the error when building PIL::

     The source file "tk.h" is unavailable.
     1 catastrophic error detected in the compilation of "././_imagingtk.c".

   I've just edited the file ''Setup'' and commented out the lines involving
   _imagingtk.

   After building, my installation was::

     cp PIL.pth /usr/freeware/lib/python2.1/site-packages/
     mkdir /usr/freeware/lib/python2.1/site-packages/PIL
     cp *.so PIL/* /usr/freeware/lib/python2.1/site-packages/PIL

   Installing PyOpenGL
   -------------------

   I built from the PyOpenGL2 cvs repository checked out on 5 June 2002.

   I changed the following lines in config/irix.cfg::

     [General]
     build_togl=0
     include_dirs=/usr/include:/usr/include/X11:/usr/freeware/include

     [GLUT]
     libs=Xi:Xmu

   I had to regenerate (using swig1.3a5, which built just fine from
   source) the C interface files using ''python setup.py build_w''.  From
   there, it was ''python setup.py build'' and then, as root ''python
   setup.py install''.  After I wrote this document, I noticed that GLUT
   was not working, but I have not had a chance to go back and fix it.  I
   believe the solution is simply to point PyOpenGL to libGLUT in the
   irix.cfg file and re-build.

   Installing SDL
   --------------

   I installed from the ''freeware'' distribution. Make sure you install
   the subpackage ''SDL-1.2.3 full shared libraries'' from the package
   ''SDL-1.2.3 Simple DirectMedia Library''.

   Installing pygame
   -----------------

   Once I had SDL installed as above, installing pygame 1.5 was easy.
   The only quirk is to point pygame at SGI's default installation
   directory.  Set your environment variable LOCALBASE to
   ''/usr/freeware''.

   Installing the Vision Egg
   -------------------------

   This is a snap.  Get the Vision Egg, decompress, move to that
   directory, and run ''python setup.py install''.  You probably need to
   have root access.

   Check your installation with the ''check-config.py'' program.  Also
   run this script if you run into any installation errors.

