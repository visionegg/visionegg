Welcome to the Vision Egg!

RUN THE CONFIGURATION CHECK (BEFORE AND/OR AFTER INSTALLATION)

Check for pre-requisites on your system by running check-config.py.
This can be run before or after installation of the Vision Egg, and
also displays useful information about the Vision Egg, if already
installed.

DEMO SCRIPTS

For demos, see the 'demo' directory and the subdirectories therein.

The current reigning champion of all the demos is the combination of
the multi_stim demo.  This demonstrates a large fraction of what the
Vision Egg is capable of.  If will probably push your hardware, maybe
even breaking on older systems.

DOCUMENTATION

The Programmer's Manual and API Reference are available in
doc/index.html

To get started, please look at the tutorials (on the website), demo
programs (in the "demo" directory). The ultimate authority is the
source code.

OUTPUT LOGGING

The output of the Vision Egg is logged using the standard Python
logging package.  The default log is a file named "VisionEgg.log".  If
unspecified, or if there are problems opening the log file, the log
will be printed to the system's standard error console.  I recommend
examining the log after running Vision Egg scripts.

You can increase the verbosity of the output by doing something like
"VisionEgg.logger.setLevel( VisionEgg.logging.DEBUG )" in your script.

WHEN SOMETHING GOES WRONG

Exceptions are normally logged to the same log file as the rest of the
Vision Egg (see above).  However, in some cases (a SyntaxError, for
example), the Vision Egg cannot load, and the exception is only
printed to the console (terminal window).  In this case, you will have
to look at the console.  On Windows, the console is normally open
during the execution of a python program, but disappers once python
terminates.  If you run the script from the command line, however, the
console window is not closed, and you can scroll back.

On Mac OS X, a Terminal window displays this information (when the
script ends in .py, but not .pyw).

On other flavors of Unix, you probably know (and may even love) the
console!

LICENSE

The Vision Egg is copyright (c) Andrew D. Straw, 2001-2003.  It is
distributed under the terms of the GNU LGPL (Lesser General Public
License.) See LICENSE.txt for more information.  This software is
provided "as is" without any warranty of any kind, either expressed or
implied.

MAILING LIST

Sign up for the mailing list at
http://www.visionegg.org/mailinglist.html