Welcome to the Vision Egg!

INSTALLATION

This is a straight Python package. The normal Python distutils method
works well. To install from source do this (as root, if necessary)
from the Vision Egg base directory:

python setup.py install

However, the above assumes all of the prerequisites are working.  For
blow-by-blow accounts of how I got the prerequisites for the Vision
Egg installed on all the supported platforms, check out the website at
http://www.visionegg.org/ 

check-config.py

Check for pre-requisites on your system by running the check-config
script.  This can be run before or after installation of the Vision
Egg, and also displays useful information about the Vision Egg, if
installed.

RUN THE CONFIGURATION CHECK

Run check-config.py script to check your configuration.  Additionally,
there may be useful system-specific information about where errors are
being printed, even if installation has not proceeded.

DEMO SCRIPTS

For demos, see the 'demo' directory.

CURRENT STATUS

This is release 0.9.0. We're homing in on a 1.0 release, and at this
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

In the rush to get release 0.9.0 out the door, the beginnings of a
true manual are available in the 'doc' directory if the source code.
Because of the preliminary nature, this is left unbuilt, but is still
available to read.  Please recognize this is still a work in progress!

Also, I highly recommend the pydoc tool.  If you have Python
installed, you can probably run pydoc by typing ``pydoc -p 1234'',
which opens a pydoc web server on port 1234 of your computer.  Just
point your favorite brower to http://localhost:1234/, click on
``VisionEgg'' (in the site-packages directory), and read away.

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

A CALL FOR HELP

Read the to-do list above. Do you see anywhere you could help out?
Get in touch if there is! Of course, suggestions and comments are
welcome.

MAILING LIST

Sign up for the mailing list at
http://www.visionegg.org/mailinglist.html

This document was written by Andrew Straw, June 2002.