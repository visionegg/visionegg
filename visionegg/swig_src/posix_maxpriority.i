%module posix_maxpriority
%{
#include <sys/mman.h>
#include <sched.h>
#include <errno.h>
%}

/* policies */
%constant int SCHED_RR    = SCHED_RR;
%constant int SCHED_FIFO  = SCHED_FIFO;

/* define errno handler */
%exception {
  errno = 0;
  $action
  if (errno) {
    PyErr_SetFromErrno(PyExc_OSError);
    goto fail; // this line supported on swig 1.3.17
  }
}

/* in posix_maxpriority.c */
extern int set_self_policy_priority( int policy, int priority );
extern int stop_memory_paging();

/* in system libraries */
extern int sched_get_priority_max( int policy );

%exception;
