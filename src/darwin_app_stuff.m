#include "Python.h"
#import <Cocoa/Cocoa.h>

void set_icon(char * filename) {
  NSImage *icon;
  const char *error;

  NS_DURING
      icon = [[NSImage alloc] initWithContentsOfFile: \
			      [NSString stringWithCString: filename]];
      [NSApp setApplicationIconImage:icon];
  NS_HANDLER
    error = PyMem_Malloc(255);
    snprintf(error,255,"Cocoa exception: %s: %s",
	     [[localException name] cString],
	     [[localException reason] cString]);
    PyErr_SetString(PyExc_RuntimeError, error);
    PyMem_Free(error);
  NS_ENDHANDLER
}
