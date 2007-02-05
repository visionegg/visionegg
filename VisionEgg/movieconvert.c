#include "Python.h"

#if defined(__APPLE__)
#  include <QuickTime/Movies.h>
#else
#  include <Movies.h>
#endif

void MovieObj_Convert(PyObject* MovieObj, Movie* outMovie) {
  PyObject* MovieObj_theMovie;
  PyObject* MovieObj_theMovie_value;
  Py_intptr_t ptr_as_int;

  MovieObj_theMovie = PyObject_GetAttrString(MovieObj,"theMovie");
  if (!MovieObj_theMovie) return;

  MovieObj_theMovie_value = PyObject_GetAttrString(MovieObj_theMovie,"value");
  if (!MovieObj_theMovie_value) return;
  
  // convert python int -> Movie*
  ptr_as_int = PyLong_AsLong(MovieObj_theMovie_value);
  (*outMovie) = (Movie)ptr_as_int;
}
