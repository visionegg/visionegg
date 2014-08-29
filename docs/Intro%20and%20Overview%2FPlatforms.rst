#format rst
## page was renamed from IntroAndOverview/Platforms

`[[Navigation(siblings)]]`_

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   The Vision Egg is known to run on:

   * Windows (tested with '95, 2000 and XP)
   * linux (x86 needed for hardware accelerated OpenGL)
   * Mac OS X (tested with 10.2 and 10.3)
   * SGI IRIX
   * Probably just about anything else with OpenGL

   Performance of your video card and its interaction with your system is
   very significant when running the Vision Egg. All of those computer
   gamers' reviews are relevant!

   In my experience, under Windows 2000 I get no frame skipping at a 200
   Hz frame rate.

   Linux offers a low latency kernel and a scheduler with adjustable
   priority, but even so, the Vision Egg (under kernel 2.4.12 at least)
   occasionally skips the occasional frame. (Note: `since linux 2.5.4`_,
   the kernel has been pre-emptible, possibly eliminating frames skipped
   for non-Vision Egg reasons.  To the best of my knowledge, no one has
   tested this yet. Here is `more information on the 2.6 kernel`_.)

   On Mac OS X, switchResX_ may allow video modes other than Apple's
   defaults, making high framerates possible. Mac OS X also has a
   realtime scheduler, which can eliminate dropped frames.

   The greatest appeal of SGI IRIX is that more than 8 bits per color are
   possible in the framebuffer and in the DACs. The Vision Egg has been
   tested on an SGI Fuel workstation with a V10 graphics card, and is
   known to support these 10 bits per channel in the framebuffer and in
   the DACs. (Recent consumer video cards have 10 bit DACs. However, many
   of these cards have only an 8 bit framebuffer which then passes
   through a 10 bit gamma table. The Matrox Parhelia and ATI Radeon 9700
   have full 10 bit framebuffers, but this mode does not work with those
   vendors' current OpenGL drivers. Please let me know if you find
   otherwise.)

   **For these reasons, I recommend Windows 2000 as the premiere
   operating system on which to run the Vision Egg. A recent Athlon or
   Pentium 4 with a recent video card from nVidia or ATI is ample power
   to run the Vision Egg.**

   That being said, the thing to remember is that the Vision Egg is cross
   platform, so you will be poised to take advantage of any particular
   features of any platform. And with the wars raging between the makers
   of graphics cards, the situation can only get better!

   .. _`since linux 2.5.4`: http://www.linuxdevices.com/news/NS3989618385.html
   .. _`more information on the 2.6 kernel`: http://www.linuxdevices.com/articles/AT7751365763.html
   .. _switchResX: http://www.madrau.com/html/SRX/indexSRX.html

