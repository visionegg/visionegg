Miscellaneous
#############

`[[Navigation(children)]]`_

.. contents::

Mailing List
============

For discussion of the Vision Egg, visit (and subscribe to) the mailing list at http://www.freelists.org/list/visionegg

Once you've subscribed, you can email the list by sending email to `visionegg@freelists.org`_.

Develop
=======

Getting the Vision Egg off the ground and maintaining it has been done by AndrewStraw_.  However, to really thrive, the Vision Egg needs you.  As an open-source project, you are free to modify the Vision Egg to suit your needs and extend it to do your experiments.  It would benefit the entire vision science community, however, if you incorporate your changes back into the distribution.

Please, if you experience a bug or a Vision Egg-related wish, send it to the mailing list.  Open source projects such as this one depend on the users to drive development, and reporting of bugs is the first place to start.  Furthermore, other users may benefit from your report, even if you've solved the bug for yourself.

To download the development tree, see the SourceRepository_ page.

Eye Tracking
============

**.. raw:: html
Rendering of reStructured text is not possible, please install Docutils.**



::

   `SR Research`_, the makers of eye tracking hardware and software, have
   released Pylink_.

   Pylink can be used with the Vision Egg!

   According to SR Research::

     Pylink allows for tracker control, real-time data access, and
     external synchronization with eye data via custom messaging.

     Many people find Python to be a simpler, yet still powerful,
     alternative to C.  Pylink can also be used in combination with the
     excellent third party open source Vision Egg software; providing a
     combined visual presentation and eye tracking scripting package.

   Distributed with Pylink is a modified Vision Egg demo using realtime
   tracker data to move a Gaussian-windowed grating in a gaze-contingent
   fashion. Following this example, it should be easy to create other
   VisionEgg/Pylink scripts for a variety of vision experiments involving
   eye tracking.

   .. _`SR Research`: http://www.eyelinkinfo.com
   .. _`Pylink`: http://www.eyelinkinfo.com/mount_software.php#Python


   Question: Is pylink open source?
   "The pylink module just wraps our C library for the EyeLink system, so
   although the pylink source itself is 'open', it is just a thin wrapper for a
   C API that is not open.
   Sol Simpson
   SR Research Ltd."

.. ############################################################################

.. _visionegg@freelists.org: mailto:visionegg@freelists.org

.. _AndrewStraw: ../AndrewStraw

.. _SourceRepository: ../SourceRepository

