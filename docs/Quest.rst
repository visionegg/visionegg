Quest
#####

.. contents::

Overview
========

The `Quest algorithm`_ has been ported directly from the MATLAB
sources available with the PsychToolbox_. The MATLAB source code was
written by Denis Pelli. Thanks to Denis for allowing it to be released
under the BSD license to the (Python) world.

This Python version **does not depend on the Vision Egg**, and may be
useful in other contexts.

Download
========

Download the source directly from the Quest package at the
`SourceForge download page`_.

Example
=======

::

   The intensity scale is abstract, but usually we think of it as representing log contrast.
   Specify true threshold of simulated observer: 0.5
   Estimate threshold: 0.4
   Trial   1 at  0.7 is right
   Trial   2 at  0.4 is right
   Trial   3 at -0.2 is wrong
   Trial   4 at  0.7 is right
   Trial   5 at  0.4 is right
   Trial   6 at  0.4 is wrong
   Trial   7 at  1.1 is right
   Trial   8 at  0.9 is right
   Trial   9 at  0.7 is right
   Trial  10 at  0.7 is right
   36 ms/trial
   Mean threshold estimate is 0.60 +/- 0.38

   Quest beta analysis. Beta controls the steepness of the Weibull function.

   Now re-analyzing with beta as a free parameter. . . .
   logC     sd      beta    sd      gamma
    0.62    0.39    3.7     4.5     0.500
   Actual parameters of simulated observer:
   logC    beta    gamma
    0.50    3.5     0.50

The example above is taken directly from the demo() function of
Quest.py and is a direct translation of the demo included in the
original MATLAB source:

::

       print 'The intensity scale is abstract, but usually we think of it as representing log contrast.'
       tActual = None
       while tActual is None:
           sys.stdout.write('Specify true threshold of simulated observer: ')
           input = raw_input()
           try:
               tActual = float(input)
           except:
               pass

       tGuess = None
       while tGuess is None:
           sys.stdout.write('Estimate threshold: ')
           input = raw_input()
           try:
               tGuess = float(input)
           except:
               pass

       tGuessSd = 2.0 # sd of Gaussian before clipping to specified range
       pThreshold = 0.82
       beta = 3.5
       delta = 0.01
       gamma = 0.5
       q=QuestObject(tGuess,tGuessSd,pThreshold,beta,delta,gamma)

       # Simulate a series of trials.
       trialsDesired=100
       wrongRight = 'wrong', 'right'
       timeZero=time.time()
       for k in range(trialsDesired):
           # Get recommended level.  Choose your favorite algorithm.
           tTest=q.quantile()
           #tTest=q.mean()
           #tTest=q.mode()
           tTest=tTest+random.choice([-0.1,0,0.1])
           # Simulate a trial
           timeSplit=time.time(); # omit simulation and printing from reported time/trial.
           response=q.simulate(tTest,tActual)
           print 'Trial %3d at %4.1f is %s'%(k+1,tTest,wrongRight[response])
           timeZero=timeZero+time.time()-timeSplit;

           # Update the pdf
           q.update(tTest,response);
       # Print results of timing.
       print '%.0f ms/trial'%(1000*(time.time()-timeZero)/trialsDesired)
       # Get final estimate.
       t=q.mean()
       sd=q.sd()
       print 'Mean threshold estimate is %4.2f +/- %.2f'%(t,sd)
       #t=QuestMode(q);
       #print 'Mode threshold estimate is %4.2f'%t
       print '\nQuest beta analysis. Beta controls the steepness of the Weibull function.\n'
       q.beta_analysis()
       print 'Actual parameters of simulated observer:'
       print 'logC beta    gamma'
       print '%5.2f        %4.1f   %5.2f'%(tActual,q.beta,q.gamma)

References
==========

* Watson, A. B. and Pelli, D. G. (1983) QUEST: a Bayesian adaptive
  psychometric method. Percept Psychophys, 33 (2), 113-20.

* Pelli, D. G. (1987) The ideal psychometric procedure. Investigative
  Ophthalmology & Visual Science, 28 (Suppl), 366.

* King-Smith, P. E., Grigsby, S. S., Vingrys, A. J., Benes, S. C., and
  Supowit, A.  (1994) Efficient and unbiased modifications of the
  QUEST threshold method: theory, simulations, experimental evaluation
  and practical implementation.  Vision Res, 34 (7), 885-912.

License
=======

The Python Quest package is released under a BSD-style license.  (The
Vision Egg itself has a LGPL license.)

.. ############################################################################

.. _Quest algorithm: http://psych.nyu.edu/pelli/software.html

.. _PsychToolbox: http://psychtoolbox.org/

.. _SourceForge download page: http://sourceforge.net/project/showfiles.php?group_id=40846

