#include <pthread.h>
#include <sched.h>
#include <sys/errno.h>
#include <sys/resource.h>
#include <mach/mach.h>
#include <sys/sysctl.h>

int get_bus_speed( void ) {

  int bus_speed, mib [2] = { CTL_HW, HW_BUS_FREQ };
  size_t len;

  len = sizeof(bus_speed);
  sysctl( mib, 2, &bus_speed, &len, NULL, 0);

  return bus_speed;
}

int set_self_thread_time_constraint_policy( unsigned int period, 
	                                           unsigned int computation,
						   unsigned int constraint,
						   unsigned int preemptible ) {

  struct thread_time_constraint_policy ttcpolicy;

  ttcpolicy.period = period;
  ttcpolicy.computation = computation;
  ttcpolicy.constraint = constraint;
  ttcpolicy.preemptible = preemptible;

  return thread_policy_set( mach_thread_self(),
			    THREAD_TIME_CONSTRAINT_POLICY,
			    (int *)&ttcpolicy,
			    THREAD_TIME_CONSTRAINT_POLICY_COUNT);
}

int set_self_pthread_priority( int policy, int priority ) {
  struct sched_param sp;

  memset(&sp,0,sizeof(struct sched_param));
  sp.sched_priority=priority;
  return pthread_setschedparam(pthread_self(), policy, &sp);
}
