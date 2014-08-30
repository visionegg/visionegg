Intro and Overview/Calibration
##############################

`[[Navigation(siblings)]]`_

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   Controlling the luminance of the display precisely is important for many experiments. The Vision Egg allows you to calibrate your display
   system and overcome the inherent non-linearity present in most displays.  The result is a system where color intensities are specified as floating point numbers from 0.0 to 1.0, producing linear display luminance. This is achieved by setting the gamma lookup tables present in the video card.

   Here is the result of some measurements I performed on my own display using a calibrated photometric luminance detector (OptiCal by CRS
   Ltd.) and **ephys_gui**, an application that comes with the Vision Egg.

   .. image:: luminance_calibration.png
      :width: 400
      :height: 300
      :alt: luminance calibration

   Notes
   -----

   This test does not test the calibration near low contrasts near the threshold for human vision.  Video cards with high precision (10 bits
   per color or more) gamma lookup tables are well suited for low contrast experiments.  Even better are video cards with high precision
   framebuffers, although OpenGL support for this is currently lacking in all consumer cards that I know about (ATI Radeon 9700 series and
   Matrox Parhelia).

   I do not have the capabilities to perform color calibration -- this test was performed by locking the red, green, and blue values to each other.

