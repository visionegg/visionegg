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

For demos, see the 'demo' directory.

CURRENT STATUS

This is release 0.9.1. We're homing in on a 1.0 release, and at this
time, I am quite happy that all of the core functionality planned for
the Vision Egg is now working. Also, the existing interface has
stabilized, with a vast majority of changes being bugfixes and
additions of new code. For these reasons, I declare this release
unofficially "1.0 beta0". What does this mean to you?

Use the Vision Egg! I've been using the Vision Egg for psychophysics
experiments for some months, and with the triggering functions
working, we're getting it integrated into our electrophysiology
experiments as well. All of the code in the distribution is working
for me.  If it doesn't work for you, it's a bug.  Report it.  Or fix
it yourself and send me the patch! :)

DOCUMENTATION

I highly recommend the pydoc tool.  If you have Python installed, you
can probably run pydoc by typing ``pydoc -p 1234'', which opens a
pydoc web server on port 1234 of your computer.  Just point your
favorite brower to http://localhost:1234/, click on ``VisionEgg'' (in
the site-packages directory), and read away.

Because of the rush to this release out the door, a true manual is not
yet included.  In the CVS repository (see our SourceForge project
webpage for access details), the beginnings of a true manual are
available in the 'doc' directory.  Because of its preliminary nature,
it is left unbuilt (not compiled to HTML or other pretty format), but
is still available to read.

WRITING YOUR OWN APPLICATION

Because the documentation and demos are limited at this point, here is
a very brief sketch of how to use the Vision Egg in an experimental
situation.  The best bet is to run the Vision Egg in fullscreen mode
and exercise control from a remote computer over TCP.  If you plan on
using Python as your means of control from the second computer, look
at the demo/Pyro directory.  If you want to exercise control from
something like LabVIEW, MATLAB, or anything else that can be made to
do TCP, check out the demo/tcp directory.  You probably want to run
the Vision Egg in "run forever" mode, entering a "go" loop for a
particular experimental run.  For the best example of this, check out
the demo/calibrate directory.

TODO

There are lots of things that will be improved or created for the 1.0
release: better documentation, a better website, more demos,
executable demo downloads that don't require Python installation, and
LabView and Matlab scripts to control the Vision Egg. (See
demos/tcp/gratingTCP.py for the Python/Vision Egg side of a LabView or
Matlab controlled stimulus generator.) Now that the interface has been
settling down and the core feature set is implemented, it's time to
get onto this user-oriented side of things.  Help with any of the
above would be great -- even writing up little tutorials that detail
how you've done something.

OUTPUT LOGGING

The output of the Vision Egg is logged.  The default log is a file
named "VisionEgg.log".  If unspecified, or if there are problems
opening the log file, the log will be printed to the system's standard
error console.  I recommend examining the log after running Vision Egg
scripts.  Most of the demos do not open GUI windows, and so any normal
ouput they produce is sent to the log.

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

The Vision Egg is copyright (c) Andrew D. Straw, 2001-2002.  It is
distributed under the terms of the GNU LGPL (Lesser General Public
License.) See LICENSE.txt for more information.  This software is
provided "as is" without any arranty of any kind, either expressed or
implied.

MAILING LIST

Sign up for the mailing list at
http://www.visionegg.org/mailinglist.html

This document was written by Andrew Straw, June 2002.