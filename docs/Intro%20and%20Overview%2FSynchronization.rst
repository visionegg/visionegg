#format rst
## page was renamed from IntroAndOverview/Synchronization

`[[Navigation(siblings)]]`_

A final timing consideration is synchronization with data acquisition or other hardware.  A common paradigm is to trigger data acquisition hardware from the Vision Egg. There are several ways to do this with the Vision Egg.

Perhaps the simplest is to control a digital output on the computer's parallel port so that this value goes from low to high when the first frame of a stimulus is drawn.  Support for this is provided for linux and win32.  Unfortunately, the parallel port is can only be updated when OpenGL is instructed to swap buffers, not when the monitor actually refreshes. If you need timing accuracy better than your inter-frame interval, the best solution is to *arm* the trigger of your data aquisition device (with the parallel port output or a network command) immediately before the stimulus begins and trigger with the vertical sync pulse from the VGA cable itself.

Alternatively, you could begin data acquisition less precisely, digitize the vertical sync pulse going to the monitor along with your usual data, and align the data after the experiment is complete.

**Important note:** As described_ by Sol Simpson of SR Research, swap_buffers() will return immediately if no buffer is already waiting to be swapped. If a buffer *is* waiting to be swapped, then swap_buffers() waits until *that* buffer is swapped. Thus, your drawing actually appears as an extra frame of later than the naive expectation in this case.

**Another similar note:** Some projectors also introduce an additional frame of latency.  

Another method, or a method to validate timing, is to use a photo detector on a patch of screen whose brightness might go from dark to light at the onset of the experiment.

Here is a figure taken from the technical specifications (Figure 5) of `Burr-Brown/Texas Instruments' OPT101 Monolithic Photodiode and Single-Supply Transimpedance Amplifier`_ that shows how this chip can be used in such a way.

`attachment:OPT101_circuit.png`_

.. ############################################################################

.. _described: http://www.freelists.org/archives/visionegg/01-2007/msg00025.html

.. _Burr-Brown/Texas Instruments' OPT101 Monolithic Photodiode and Single-Supply Transimpedance Amplifier: http://focus.ti.com/docs/prod/folders/print/opt101.html

