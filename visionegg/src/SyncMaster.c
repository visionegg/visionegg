#include "Python.h"

#if defined(__APPLE__)
#  include <SyncMaster/syncmaster.h> // Get header from framework
#else
#  include "syncmaster.h"
#endif

#include <stdlib.h>

#define PY_CHECK(X) if (!(X)) { goto error; }
#define SYNCMASTER(X) if (X) { PyErr_SetString(PyExc_SyncMasterError,sm_get_error()); goto error; }

static PyObject *PyExc_SyncMasterError=NULL;

static char init__doc__[] = 
"init\n";

static PyObject *init(PyObject *self, PyObject *args)
{
  SYNCMASTER(sm_init());
  Py_INCREF(Py_None);
  return Py_None;
 error:
  return NULL;
}

//////////////////////////////////////////////

static char py_sm_close__doc__[] = 
"\n";

static PyObject *py_sm_close(PyObject *self, PyObject *args)
{
  return NULL;
}

//////////////////////////////////////////////

static char clear_vsync_count__doc__[] = 
"\n";

static PyObject *clear_vsync_count(PyObject *self, PyObject *args)
{
  SYNCMASTER(sm_clear_vsync_count());
  Py_INCREF(Py_None);
  return Py_None;
 error:
  return NULL;
}

//////////////////////////////////////////////

static char notify_device__doc__[] = 
"\n";

static PyObject *notify_device(PyObject *self, PyObject *args)
{
  int flags=0;

  PY_CHECK(PyArg_ParseTuple(args,"|i",&flags));

  if ((flags > 255) || (flags < 0)) {
    PyErr_SetString(PyExc_OverflowError,"Argument must be in range [0,255].");
    goto error;
  }

  SYNCMASTER(sm_notify_device((UInt8)flags));
  Py_INCREF(Py_None);
  return Py_None;
 error:
  return NULL;
}

//////////////////////////////////////////////

static char get_vsync_count__doc__[] = 
"\n";

static PyObject *get_vsync_count(PyObject *self, PyObject *args)
{
  UInt32 vsyncs;

  SYNCMASTER(sm_get_vsync_count(&vsyncs));

  return PyInt_FromLong(vsyncs);
 error:
  return NULL;
}

//////////////////////////////////////////////

static PyMethodDef
SyncMaster_methods[] = {
  { "init", (PyCFunction)init, METH_VARARGS, init__doc__},  
  { "close", (PyCFunction)py_sm_close, METH_VARARGS, py_sm_close__doc__},  
  { "clear_vsync_count", (PyCFunction)clear_vsync_count, METH_VARARGS, clear_vsync_count__doc__},  
  { "notify_device", (PyCFunction)notify_device, METH_VARARGS, notify_device__doc__},  
  { "get_vsync_count", (PyCFunction)get_vsync_count, METH_VARARGS, get_vsync_count__doc__},  
  { NULL, NULL, 0, NULL} /* sentinel */
};

DL_EXPORT(void)
initSyncMaster(void)
{
  PyObject *module;
  PyObject *module_dict;
  PyObject *class_dict;
  PyObject *class_name;
  PyObject *bases;

  module = Py_InitModule("SyncMaster", SyncMaster_methods);
  module_dict = PyModule_GetDict(module);
  class_dict = PyDict_New();
  class_name = PyString_FromString("SyncMasterError");
  bases = Py_BuildValue("(O)",PyExc_Exception);
  PyExc_SyncMasterError = PyClass_New(bases,class_dict,class_name);
  PyDict_SetItemString(module_dict, "SyncMasterError", PyExc_SyncMasterError);
  PyDict_SetItemString(module_dict, "SWAPPED_BUFFERS", PyInt_FromLong(SM_SWAPPED_BUFFERS));
  PyDict_SetItemString(module_dict, "IN_GO_LOOP", PyInt_FromLong(SM_IN_GO_LOOP));
  Py_DECREF(class_dict);
  Py_DECREF(class_name);
  Py_DECREF(bases);
  Py_DECREF(PyExc_SyncMasterError);

  return;
}
