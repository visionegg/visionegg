%module darwin_getrefresh
%{
PyObject *PyErr_DarwinGetRefreshError;
%}

%init %{
  /* New exception */
  PyErr_DarwinGetRefreshError = PyErr_NewException( "VisionEgg.DarwinGetRefreshError", NULL, NULL ); // New reference
  Py_INCREF(PyErr_DarwinGetRefreshError);
%}

%exception {
  $action
  if (darwin_getrefresh_err_occurred()) {
    PyErr_SetString(PyErr_DarwinGetRefreshError, (const char *)darwin_getrefresh_err_message());
    return NULL;
  }
}

double getrefresh( void );
