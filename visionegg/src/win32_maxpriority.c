#include <WINDOWS.H> // winbase.h is all we really want, but it doesn't include all the headers it needs
#include <WINBASE.H>

void set_self_process_priority_class( int priority_class ) {
  return SetPriorityClass( GetCurrentProcess(), priority_class );
}

void set_self_thread_priority( int priority ) {
  return SetThreadPriority( GetCurrentThread(), priority );
}
