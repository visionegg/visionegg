%module darwin_maxpriority
%{
#include <pthread.h>
#include <sched.h>
#include <sys/errno.h>
#include <sys/resource.h>
#include <mach/mach.h>
#include <sys/sysctl.h>
%}

/* From /usr/include/sys/resource.h */
%constant int PRIO_PROCESS = PRIO_PROCESS;

/* From /usr/include/pthread_impl.h */
%constant int SCHED_OTHER = SCHED_OTHER;
%constant int SCHED_RR    = SCHED_RR;
%constant int SCHED_FIFO  = SCHED_FIFO;

/* in darwin_maxpriority.c */
extern int get_bus_speed( void );
extern int set_self_thread_time_constraint_policy( unsigned int period, 
	                                           unsigned int computation,
						   unsigned int constraint,
						   unsigned int preemptible );
extern int set_self_pthread_priority( int policy, int priority );

/* system libraries functions */

/* define exception handler to deal with errno */
%exception {
  errno = 0;
  $action
  if (errno) {
    PyErr_SetFromErrno(PyExc_OSError);
    goto fail; // this line supported on swig 1.3.17
  }
}

extern int getpriority( int, int );
extern int sched_get_priority_max( int );
extern int setpriority( int, int, int );

%exception;   /* Deletes previously defined handler */
