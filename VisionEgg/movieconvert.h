#include "Python.h"

#if defined(__APPLE__)
#  include <QuickTime/Movies.h>
#else
#  include <Movies.h>
#endif

void MovieObj_Convert(PyObject* MovieObj, Movie* outMovie);
