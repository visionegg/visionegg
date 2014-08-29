#format rst

`[[Navigation(siblings)]]`_

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   Here is a description of technology at the core of the Vision Egg.
   The computer language used is Python, and graphics are drawn using the
   OpenGL standard. Ample documentation for these technologies is
   available, both online and in print.  This document covers why the
   choice was made to rely on these technologies, and why you can trust
   them with your experiments.  It also provides some insight into how
   the Vision Egg works and the philosophy of its construction.

   Python - http://www.python.org
   ------------------------------

   * What is Python?

   The Python computer programming language is free, easy to learn, easy
   to use, powerful, and flexible.  Python supports modern programming
   techniques such as object oriented programming, threading, and
   high-level data types.  There are countless modules for virtually any
   programming task.  Therefore, Python is well suited for complex
   programming tasks. There is much Python advocacy on the internet, but
   let me just say that Python was chosen for the Vision Egg because
   creating something like this project would be a much larger burden
   without such a fantastic language.

   * Why an interpreted language for real-time stimulus control?

   A program written in an interpreted language will run more slowly than
   a well-written C program. But there are two reasons why Python works
   well for this job.  The first reason is that data array manipulation
   is performed with high-performance, compiled C code via the Numeric
   module of Python. In other words, high-level Python code is only used
   to direct computationally intensive tasks.

   The second reason why Python works for this task is that computer
   monitors can only be refreshed at their maximum vertical frequency,
   which typically ranges up to 200 Hz.  At 200 Hz, your program and the
   graphics card have about 5 milliseconds to prepare the next
   frame. Modern computers can perform enormous numbers of calculations
   in that time, especially if the hardware is specialized for the task,
   such as graphics processing on a graphics card. In other words, it's
   fast enough.  This is evidenced by the fact that running under Windows
   2000, on an Athlon 1800+ system with an nVidia geForce 2 Pro card, no
   frames are skipped while updating the monitor at 200 Hz.  Although I
   do not know of any exhaustive testing, **the Vision Egg runs for
   hours at a time without skipping a single frame on standard,
   consumer-level hardware.**

   The biggest timing-related concern is unrelated to choice of
   programming language.  A multitasking operating system might take
   control of the CPU from the stimulus generating program for an
   unacceptably long period.  This is the biggest potential cause of
   frame-skipping latencies.

   * Comparison of Python with other languages

   Matlab is frequently used by vision scientists because it is well
   suited for data analysis and numerical modeling.  However, it would be
   difficult to reproduce the functionality of the Vision Egg directly in
   Matlab because of the lack of many language features such as (useful)
   object oriented programming, an OpenGL interface, and easy access to
   routines written in C.

   The C language is used for various bits of the Vision Egg, but it
   would be a very difficult tool with which to write an application of
   the scale of the Vision Egg.  With todays fast computers, execution
   speed is at less of a premium than a scientist or programmer's
   time. The main role of C within the Vision Egg is as interface code
   that allows Python programs to call platform-specific functions.
   Performance critical routines could be written in C, but these
   optimizations have not been needed in general.  It does remain an
   option to re-code the drawing performed by a particular stimulus class
   or even the entire main loop in C.

   If you prefer another language, you are welcome to use the ideas found
   within the Vision Egg because it is open-source.  Also, it would be
   possible to embed Python and the Vision Egg within a C program.

   OpenGL - http://www.opengl.org
   -------------------------------

   * What is OpenGL?

   OpenGL is the ubiquitous cross platform way to access hardware
   accelerated graphics processing in today's video cards.  It is an open
   standard 2D and 3D graphics programming interface that recent video
   cards support.  While OpenGL is defined in C, the PyOpenGL_ project
   makes the OpenGL interface available in Python.

   OpenGL offers features not available on traditional 2D graphics cards.
   Recent graphics cards are capable of realtime image scaling, sub-pixel
   image re-sampling and movement, perspective projections and other
   image warping, true color support for framebuffers and DACs greater
   than 8 bits (no more color lookup tables!).  These are just a few of
   the features that OpenGL offers and that the Vision Egg uses.

   The Vision Egg comes with many standard stimuli, such as sinusoidal
   gratings, moving rectangles, random dots, images, and
   checkerboards. Therefore, you may not need to learn OpenGL to take
   advantage of it.  But if you do learn OpenGL, you can extend the
   Vision Egg to do anything your graphics card is capable of.  OpenGL is
   complex and is therefore challenging to learn, but it is a standard,
   so there is an incredible wealth of information on it.

   Other bits used by the Vision Egg
   -----------------------------------------------------

   There are a several pieces of code that extend Python in various ways
   required by the Vision Egg.  Thanks to the developers of these great
   packages! PyOpenGL_ brings OpenGL to Python, pygame_ and SDL_ create
   OpenGL windows in a cross-platform way and get keyboard and mouse
   input (among many other features that the Vision Egg does not use),
   `Numeric Python (Numpy)`_ handles vectors and matrices of numeric
   data, the `Python Imaging Library (PIL)`_ handles images, and
   (optionally) Pyro_ allows communication between Python programs
   running on the same network.

   .. _PyOpenGL: http://pyopengl.sourceforge.net
   .. _pygame: http://www.pygame.org
   .. _SDL: http://www.libsdl.org
   .. _`Numeric Python (Numpy)`: http://www.pfdubois.com/numpy
   .. _`Python Imaging Library (PIL)`: http://www.pythonware.com/products/pil/index.htm
   .. _Pyro: http://pyro.sourceforge.net

