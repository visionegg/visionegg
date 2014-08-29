#format rst

`[[Navigation(siblings)]]`_

Instructions for Vision Egg 1.2.1
=================================

If in doubt about how to install from a .egg file, use the corresponding .exe file instead.

with Python 2.5
---------------

First, download and install these dependencies:

* `python-2.5.4.msi`_

* `PIL-1.1.6.win32-py2.5.exe`_

* `PyOpenGL-2.0.2.01.py2.5-numpy24.exe`_ (VE 1.2 has issues with PyOpenGL 3.0 on Windows. See `SF#2817196`_)

* `pygame-1.8.0.win32-py2.5.msi`_

* `numpy-1.3.0-win32-superpack-python2.5.exe`_

* `setuptools-0.6c8.win32-py2.5.exe`_

Next, download and install a Vision Egg binary compiled for Python 2.5:

* `visionegg-1.2.1.win32-py2.5.exe`_, or `visionegg-1.2.1-py2.5-win32.egg`_

Optional:

* QuickTime_

with Python 2.6
---------------

**PyOpenGL 3.0 (the only PyOpenGL available for Python 2.6) has a bug that prevents the VE from working properly on Windows. Use PyOpenGL 2 and Python 2.5 until it's fixed.** `The bug report (SF#2817196)`_

First, download and install these dependencies:

* `python-2.6.6.msi`_

* `PIL-1.1.6.win32-py2.6.exe`_

* `PyOpenGL-3.0.1.win32.exe`_

* `pygame-1.8.1release.win32-py2.6.msi`_

* `numpy-1.3.0-win32-superpack-python2.6.exe`_

* `ssetuptools-0.6c9.win32.exe`_

Next, download and install the Vision Egg binary compiled for Python 2.6. I will upload them to PyPI once the PyOpenGL bug is fixed:

* `attachment:visionegg-1.2.1.win32-py2.6.exe`_visionegg-1.2.1.win32-py2.6.exe`attachment:None`_, or `attachment:visionegg-1.2.1-py2.6-win32.egg`_visionegg-1.2.1-py2.6-win32.egg`attachment:None`_

Optional:

* QuickTime_

Alternate installers
====================

`Christoph Gohlke`_ offers `unofficial Windows binaries`_ for various Python packages, including 64-bit versions of the Vision Egg.

Old Instructions for Vision Egg 1.1
===================================

Download and install:

* `python-2.5.4.msi`_

* `PIL-1.1.6.win32-py2.5.exe`_

* `PyOpenGL-2.0.2.01.py2.5-numpy24.exe`_ (VE 1.1.x has issues with PyOpenGL 3.)

* `pygame-1.8.0.win32-py2.5.msi`_

* `numpy-1.3.0-win32-superpack-python2.5.exe <http://superb-west.dl.sourceforge.net/sourceforge/numpy/numpy-1.3.0-win32-superpack-python2.5.exe>`__

* `setuptools-0.6c8.win32-py2.5.exe`_

Optional:

* QuickTime_

.. ############################################################################

.. _python-2.5.4.msi: http://python.org/ftp/python/2.5.4/python-2.5.4.msi

.. _PIL-1.1.6.win32-py2.5.exe: http://effbot.org/downloads/PIL-1.1.6.win32-py2.5.exe

.. _PyOpenGL-2.0.2.01.py2.5-numpy24.exe: http://www.develer.com/~rasky/PyOpenGL-2.0.2.01.py2.5-numpy24.exe

.. _SF#2817196:
.. _The bug report (SF#2817196): https://sourceforge.net/tracker/?func=detail&atid=105988&aid=2817196&group_id=5988

.. _pygame-1.8.0.win32-py2.5.msi: http://www.pygame.org/ftp/pygame-1.8.0.win32-py2.5.msi

.. _numpy-1.3.0-win32-superpack-python2.5.exe: http://downloads.sourceforge.net/project/numpy/NumPy/1.3.0/numpy-1.3.0-win32-superpack-python2.5.exe

.. _setuptools-0.6c8.win32-py2.5.exe: http://pypi.python.org/packages/2.5/s/setuptools/setuptools-0.6c8.win32-py2.5.exe#md5=963088fdb1c7332b1cbd4885876e077a

.. _visionegg-1.2.1.win32-py2.5.exe: http://sourceforge.net/projects/visionegg/files/visionegg/1.2.1/visionegg-1.2.1.win32-py2.5.exe

.. _visionegg-1.2.1-py2.5-win32.egg: http://sourceforge.net/projects/visionegg/files/visionegg/1.2.1/visionegg-1.2.1-py2.5-win32.egg

.. _QuickTime: http://www.apple.com/quicktime/download/

.. _python-2.6.6.msi: http://python.org/ftp/python/2.6.6/python-2.6.6.msi

.. _PIL-1.1.6.win32-py2.6.exe: http://effbot.org/media/downloads/PIL-1.1.6.win32-py2.6.exe

.. _PyOpenGL-3.0.1.win32.exe: http://pypi.python.org/packages/any/P/PyOpenGL/PyOpenGL-3.0.1.win32.exe

.. _pygame-1.8.1release.win32-py2.6.msi: http://pygame.org/ftp/pygame-1.8.1release.win32-py2.6.msi

.. _numpy-1.3.0-win32-superpack-python2.6.exe: http://downloads.sourceforge.net/project/numpy/NumPy/1.3.0/numpy-1.3.0-win32-superpack-python2.6.exe

.. _ssetuptools-0.6c9.win32.exe: http://astraw.com/setuptools/setuptools-0.6c9.win32.exe

.. _Christoph Gohlke: http://www.lfd.uci.edu/~gohlke/

.. _unofficial Windows binaries: http://www.lfd.uci.edu/~gohlke/pythonlibs/#visionegg

