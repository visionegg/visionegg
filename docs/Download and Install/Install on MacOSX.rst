Download and Install/Install on MacOSX
######################################

`[[Navigation(siblings)]]`_

Snow Leopard, OS X 10.6, VisionEgg1.2.1
=======================================

I (`Alex Holcombe`_) installed Vision Egg on an Intel IMac. I needed to:

Install Pygame(1.9.1), PyOpenGL(3.0.0), and PIL (Imaging-1.1.7), and VisionEgg_ (1.2.1) from source by in terminal typing

python2.6 setup.py install

in the directory of each.  The python2.6 is because the default installation of python, python2.5, had a problem (can't remember what it was now). Only in the case of PIL, I had to preface the above command with 'sudo', otherwise it didn't have permission to copy some scripts to the appropriate place.

-------------------------



From an email_ by Jens Kremkow:

::

   Dear Andrew, David,

   I managed to get it running on Snow Leopard. There were some issues with pygame.
   This was the way I got VisionEgg to run.

   1. I use MacPorts to install python2.6 and the dependencies.
   http://www.macports.org

   2. Problems started when I tried to install py-game with MacPorts, it wanted to install a full python2.4 for that. So I stopped the installation of py-game with MacPorts

   3. I downloaded pygame from the svn and installed it from source
   http://www.pygame.org/wiki/cvs

   4. In pygame/Setup.in I changed the SDL path to the one of MacPorts (/opt/local/include/SDL)
   # SDl
   SDL = -I/opt/local/include/SDL -D_REENTRANT -lSDL

   and I had to comment this line, because the camera resulted in a building error
   # _camera src/_camera.c src/camera_v4l2.c src/camera_v4l.c $(SDL) $(DEBUG

   5. In pygame/config_darwin.py I also had to add the MacPort path
   line 32: BASE_DIRS = '/', os.path.expanduser('~/'), '/opt/local/'
   line 113: incdirs = ['/opt/local/include', '/opt/local/include/freetype2/freetype','/opt/local/include/SDL']
   line 114: libdirs = ['/opt/local/lib']

   Maybe some of these path settings are redundant, but this way it compiled.

   I think that was all the trouble I had. I hope it helps.

   Best,
   Jens

And `another email`_ from John Christie:

::

   Maybe I did something special but I got python 2.6.3 and pygame 1.9.1 dmg installers, the PIL installer,  and did the rest through setuptools (pyopengl, numpy, aggdraw, visionegg)  with no hitches whatsoever.  pygame doesn't install with setuptools for me.

Leopard, OSX 10.5.x, VisionEgg 1.2.x
====================================

**The easy way (These instructions are finished)**

This is a short version of more verbose instructions here: http://www.scidav.org/installs

1. Get the appropriate version of XCode from http://developer.apple.com/mac

#. Get the Enthought Python Distribution from http://www.enthought.com/products/epd.php

   * Includes almost all dependencies you'll want (good)

   * Not free to non-academics (but you're probably an academic)

#. Make a link to trick installers into thinking you have python.org 2.5 installed:

   * *cd /Library/Frameworks/Python.framework/Versions; sudo ln -s 5.0.0 2.5*

   * replace "5.0.0" with whatever your EPD version is, and if your EPD contains a newer python  (e.g. 2.6), use that as the second argument.

#. Run the installer (for your version of python) from http://pygame.org/download.shtml

#. Install the VisionEgg_ source from http://sourceforge.net/projects/visionegg/files/visionegg/

   * *tar xzvf visionegg-1.2.1.tar.gz*

   * *cd visionegg-1.2.1*

   * *python setup.py install*

Note: the VisionEgg_ seems to work fine with pygame 1.9. Since this is only used to obtain the OpenGL context, I am not too concerned with testing this. Pygame 1.9 doesn't rely on pyobjc. If you insist on pygame 1.8 or earlier, you can easy_install pyobjc.

**The hard way (These instructions are not yet finished)**

* Get Python from `python.org`_

* Install libjpeg according to http://simonwilder.wordpress.com/2009/06/17/fixing-pil-ioerror-decoder-jpeg-not-available/

* Install PIL from source from http://effbot.org/downloads/Imaging-1.1.6.tar.gz

* Install pygame from http://www.pygame.org/ftp/pygame-1.8.1release-py2.5-macosx10.5.zip

* Install PyOpenGL from http://downloads.sourceforge.net/sourceforge/pyopengl/PyOpenGL-3.0.0.tar.gz?use_mirror=superb-west

Installing from source with v1.1
--------------------------------

* Download the source package from the sourceforge site

* Install all the necessary packages (numpy, PIL, PyOpenGL, pygame, pyobjc) from here_. The preferred version of python currently is 2.4, so ensure that when you type "python" at a Terminal, you get 2.4. If that command starts a different version, install MacPython2_.4 and change the "Current" aliases in the Frameworks directory (probably /Library/Frameworks/Python.framework/Versions/2.4/lib/python2.4/site-packages/) to 2.4. Note that /System/Library has its own version of Python that you can ignore

* If you don't have it, get Xcode from apple.com so that you can compile the source code

* Install by typing "python setup.py install" from the "visionegg-1.1" directory.

Instructions for Tiger, 10.4
============================

I (`Alex Holcombe`_) installed Vision Egg using the following procedure. Each of the following packages were downloaded from here_ . These are Universal versions, and worked on my 2.33 GHz Intel MacBook_ Pro, as well as a G5 non-Intel PowerPC.

1. I installed `Xcode 2.4`_ (free Apple compiler)

2. "Universal-MacPython_-2.4.3-2006-04-07" was installed by double-clicking.

3. I removed all Python 2.3 references that were on my machine (this step should be unnecessary)

4. "numpy-1.0.1-py2.4-macosx10.4-2006-12-12.dmg"  installed by double-clicking.

5. "PIL-1.1.5-py2.4-macosx10.4"  installed by double-clicking.

6. "PyOpenGL-2.0.2.01-py2.4-macosx10.4" installed by double-clicking.

7. "pygame-1.8.0pre-py2.4-macosx10.4a" installed by double-clicking.

8. "pyobjc-1.4-python2.4-macosx10.4.dmg" installed by double-clicking.

9. The `Vision Egg source`_, visionegg-1.1.tar.gz file was downloaded and unpacked.

10. "python setup.py install" was executed from Terminal.app when in the "visionegg-1.1" directory

COMPLICATION. In my case, for some reason PIL was installed in step 4 with the wrong file permissions. This caused check-config.py to complain that it could not import Image. Once I changed all file permissions so all could read and execute ("chmod +rx") for all the PIL files and directories (at /Library/Frameworks/Python.framework/Versions/2.4/lib/python2.4/site-packages/), then everything worked. Hopefully this was caused by me switching to superuser at some point and forgetting to exit or something, let the mailing list or this wiki know if you run into this problem yourself.

`More details`_ about the new Universal Python2.4 packages used above.

See also `the Kubovy Lab setup page`_, who are no longer using Vision Egg per se but are using most of the same libraries.

Abbreviated Instructions for Tiger, Python 2.5
==============================================

Ensure the XCode development tools are installed. Download and install SDL, SDL_ttf, SDL_mixer, and SDL_image BINARIES from www.libsdl.org (drag them into /Library/Frameworks). Download and install all dependencies from SOURCE: PIL, Numeric (NOT numarray), pygame, PyOpenGL 3, pyobjc. Download Vision Egg source. Install the source

.. ############################################################################

.. _Alex Holcombe: http://www.psych.usyd.edu.au/staff/alexh/

.. _email: http://www.freelists.org/post/visionegg/Installing-VisionEgg-in-Snow-Leopard,2

.. _another email: http://www.freelists.org/post/visionegg/Installing-VisionEgg-in-Snow-Leopard,4

.. _python.org: http://python.org/ftp/python/2.5.4/python-2.5.4-macosx.dmg

.. _here: http://pythonmac.org/packages/py24-fat/

.. _Xcode 2.4: http://developer.apple.com/tools/download/

.. _Vision Egg source: http://sourceforge.net/project/showfiles.php?group_id=40846&package_id=32990&release_id=605248

.. _More details: http://bob.pythonmac.org/archives/2006/04/10/python-and-universal-binaries-on-mac-os-x/

.. _the Kubovy Lab setup page: http://kubovylab.psyc.virginia.edu/index.php/Installing_Perception_Toolkit_Dependencies

