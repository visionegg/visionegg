#include <stdlib.h>
#import <Cocoa/Cocoa.h>

int darwin_getrefresh_error = 0;
const char * darwin_getrefresh_error_str= NULL;

int darwin_getrefresh_err_occurred( void ) {
  return darwin_getrefresh_error;
}
const char * darwin_getrefresh_err_message( void ) {
  return darwin_getrefresh_error_str;
}
void darwin_getrefresh_set_error(const char * errmsg) {
  darwin_getrefresh_error = 1;
  darwin_getrefresh_error_str = errmsg;
}

double getrefresh( void ) {            
  // This is based on SDL12 http://www.libsdl.org/ 

  CFDictionaryRef mode = NULL;
  CFNumberRef refreshRateCFNumber = NULL;
  double refreshRate;
            
  mode = CGDisplayCurrentMode(kCGDirectMainDisplay);
  if ( NULL == mode ) {
    darwin_getrefresh_set_error("Cannot get display mode");
    goto ERROR;
  }
  refreshRateCFNumber = CFDictionaryGetValue (mode, kCGDisplayRefreshRate);
  if ( NULL == refreshRateCFNumber ) {
    darwin_getrefresh_set_error("Mode has no refresh rate");
    goto ERROR;
  }
  if ( 0 == CFNumberGetValue (refreshRateCFNumber, kCFNumberDoubleType, &refreshRate) ) {
    // From CGDirectDisplay.h: (Mac OS X 10.2.6, Dec 2002 Developer Tools:
    //
    // Some display systems may not conventional video vertical and
    // horizontal sweep in painting.  These displays report a
    // kCGDisplayRefreshRate of 0 in the CFDictionaryRef returned by
    // CGDisplayCurrentMode().  On such displays, this function
    // returns at once.
    darwin_getrefresh_set_error("Error getting refresh rate - no conventional video sweep?");
    goto ERROR;
  }
  if ( 0 == refreshRate ) {
    // 
    darwin_getrefresh_set_error("Error getting refresh rate - no conventional video sweep?");
    goto ERROR;
  }
  return refreshRate;
 ERROR:
  return 0;
}
