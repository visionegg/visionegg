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
#define     PRIO_PROCESS    0

/* From /usr/include/pthread_impl.h */
#define SCHED_OTHER                1
#define SCHED_RR                   2
#define SCHED_FIFO                 4

/* in darwin_maxpriority.c */
extern int get_bus_speed( void );
extern int set_self_thread_time_constraint_policy( unsigned int period, 
	                                           unsigned int computation,
						   unsigned int constraint,
						   unsigned int preemptible );
extern int set_self_pthread_priority( int policy, int priority );

/* in system libraries */
extern int errno;
extern int getpriority( int, int );
extern int setpriority( int, int, int );
extern int sched_get_priority_max( int );