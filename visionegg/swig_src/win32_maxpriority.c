#include <WINDOWS.H> // winbase.h is all we really want, but it doesn't include all the headers it needs
#include <WINBASE.H>

unsigned short set_self_process_priority_class( int priority_class ) {
  return (unsigned short)SetPriorityClass( GetCurrentProcess(), priority_class );
}

unsigned short set_self_thread_priority( int priority ) {
  return (unsigned short)SetThreadPriority( GetCurrentThread(), priority );
}
