Welcome to the Vision Egg!

INSTALLATION

This is just a straight Python package. On some platforms, additional
functionality is available with via C extensions. The normal Python
distutils method works well. To install from source do this (as root,
if necessary) from the Vision Egg base directory:

python setup.py install

However, the above assumes all of the prerequisites are working.  For
blow-by-blow accounts of how I got the prerequisites for the Vision
Egg installed on all the supported platforms, check out the website at
http://www.visionegg.org/

DEMO SCRIPTS

For demos, see the 'demo' directory.

CURRENT STATUS

This is release 0.9.0. We're homing in on a 1.0 release, and at this
time, I am quite happy that all of the core functionality I had
planned for the Vision Egg is now working. Also, the existing
interface has stabilized, with a vast majority of changes being
bugfixes and additions of new code. For these reasons, I declare this
release unofficially "1.0 beta0". What does this mean to you?

Use the Vision Egg! I've been using the Vision Egg for psychophysics
experiments for some months, and with the triggering functions
working, we're getting it integrated into our electrophysiology
experiments as well. All of the code in the distribution is working
for me.  If it doesn't work for you, it's a bug.  Report it.  Or fix
it yourself and send me the patch! :)

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

MAILING LIST

Sign up for the mailing list at
http://www.visionegg.org/mailinglist.html
