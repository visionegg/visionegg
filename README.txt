Welcome to the Vision Egg!

INSTALLATION

To install from source, type this from a command line (as root, if
necessary) from the Vision Egg base directory:

python setup.py install

However, the above assumes all of the prerequisites are working.  For
blow-by-blow accounts of how I got the prerequisites for the Vision
Egg installed on all the supported platforms, check out the website at
http://www.visionegg.org/ 

RUN THE CONFIGURATION CHECK (BEFORE AND/OR AFTER INSTALLATION)

Check for pre-requisites on your system by running check-config.py.
This can be run before or after installation of the Vision Egg, and
also displays useful information about the Vision Egg, if already
installed.

DEMO SCRIPTS

For demos, see the 'demo' directory and the subdirectories therein.

The current reigning champion of all the demos is the combination of
the gratingTCP server with the gratingGUI controller in the demo/tcp
directory.

DOCUMENTATION

To get started, please look at the tutorials, demo programs, and the
Vision Egg Programmer's Manual.  If that fails, I highly recommend
looking at the source code, particularly the docstrings in the Core.py
module.

OUTPUT LOGGING

The output of the Vision Egg is logged.  The default log is a file
named "VisionEgg.log".  If unspecified, or if there are problems
opening the log file, the log will be printed to the system's standard
error console.  I recommend examining the log after running Vision Egg
scripts.

Exceptions occur when something goes wrong.  These exceptions are
normally logged to the same log file as the rest of the Vision Egg.
In some cases, however, the Vision Egg doesn't even load, and the
exception is printed to the console.  In this case, you will have to
look at the console.  On Windows, the console is normally open during
the execution of a python program, but disappers once python
terminates.  If you run from the command line, however, the console
window is not closed, and you can scroll back.

On Mac OS X, the console is visible when running the "Console"
application in "Applications/Utilities".

On other flavors of Unix, you probably know and love the console!

LICENSE

The Vision Egg is copyright (c) Andrew D. Straw, 2001-2003.  It is
distributed under the terms of the GNU LGPL (Lesser General Public
License.) See LICENSE.txt for more information.  This software is
provided "as is" without any warranty of any kind, either expressed or
implied.

MAILING LIST

Sign up for the mailing list at
http://www.visionegg.org/mailinglist.html