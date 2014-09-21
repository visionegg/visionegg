Miscellaneous/LabView
#####################

`[[Navigation(siblings)]]`_

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   Thanks to Jamie Theobald (Graduate Program in Neurobiology and
   Behavior, Zoology Department, University of Washington) for
   contributing Labview 6 code to control gratings made with the Vision
   Egg.  He writes::

     As of yesterday, my own Labview program - written for the Innisfree
     Picasso - is completely functional with the Vision Egg.  It took
     some messing around, but I can now do experiments as well or better
     than before.

     I intend to phase out my Labview programs over time - in favor of
     Python - but in the meantime it is quickest to interface with what I
     already have.  And it's created a set of tools in Labview that
     control the Vision Egg gratings.  It can't take advantage of
     everything that the Vision Egg can do, but I don't think you can do
     that without knowing Python.  And it's not a bad start, either.  It
     does everything I've ever needed with gratings (the contrast ramps
     are really nice).  It uses go loops with daq triggering for
     synchronizing.

   The Labview code is in the ''visionegg-contrib'' package at the
   `Vision Egg SourceForge files page`_.  Control Grating.vi is the main
   program file in that package.

   To the best of my knowledge, this is the setup that he uses:

   .. image:: labview_schematic.gif
      :width: 434
      :height: 194
      :alt: Computer setup overview

   Here are some screenshots he sent from Labview running on Mac OS 9.

   .. image:: grating_control.gif
      :width: 455
      :height: 426
      :alt: Grating Control Labview panel

   .. image:: waveforms.gif
      :width: 815
      :height: 538
      :alt: Edit Grating panel

   .. image:: innards.gif
      :width: 996
      :height: 654
      :alt: VI diagram

   .. _`Vision Egg SourceForge files page`: http://sourceforge.net/project/showfiles.php?group_id=40846

