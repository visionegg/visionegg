#include <sys/mman.h>
#include <sched.h>
#include <errno.h>

extern int set_self_policy_priority( int policy, int priority ) {
  struct sched_param params;

  params.sched_priority = priority;
  return sched_setscheduler(0,policy,&params);
}

int stop_memory_paging() {

#if defined(MCL_CURRENT) && defined(MCL_FUTURE)
  return mlockall( MCL_CURRENT | MCL_FUTURE );
#else
  return 0;
#endif

}
