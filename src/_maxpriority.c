#include "Python.h"

/*
 * This is the C source code for setting maximum priority by the Vision Egg
 * library.
 *
 * There is code for darwin (Mac OS X), win32, and linux/irix/posix.
 *
 * Copyright (c) 2001, 2002 Andrew Straw.  Distributed under the terms of
 * the GNU Lesser General Public License (LGPL).
 *
 * $Revision$
 * $Date$
 * Author = Andrew Straw <astraw@users.sourceforge.net>
 *
 */

#if defined(__APPLE__)
/* Everything to support realtime in Apple Mac OS X is based on the following two things:
   1) http://developer.apple.com/techpubs/macosx/Darwin/General/KernelProgramming/scheduler/Using_Mach__pplications.html
   2) The Mac OS X port of the Esound daemon.
*/
#include "darwin_pthread_modified.h" // Had problems with original...
#include <mach/mach.h>
#include <sys/sysctl.h>
#elif defined(_WIN32)
/* Windows */
#include <WINDOWS.H> // winbase.h is all we really want, but it doesn't include all the headers it needs
#include <WINBASE.H>
#else 
/* Normal UNIX stuff */
#include <sys/mman.h>
#include <sched.h>
#include <errno.h>
#endif 

#define TRY(E)     if(! (E)) return NULL

static char set_realtime__doc__[] = 
"Raise the Vision Egg to maximum priority.\n"
"\n"
"The following optional keyword arguments only have an effect\n"
"on the darwin (Mac OS X) platform:\n"
"\n"
"  darwin_period_denom = 120;\n"
"  darwin_computation_denom = 2400;\n"
"  darwin_constraint_denom = 1200;\n"
"  darwin_preemptible = 0;";

static PyObject *set_realtime(PyObject *self, PyObject *args, PyObject *kw)
{
  /* We will parse all the keywords on all platforms because they
     should be legal, but we just won't care what there values are
     when they are irrelevant. */

  static char *kwlist[] = {"darwin_period_denom",
			   "darwin_computation_denom",
			   "darwin_constraint_denom",
			   "darwin_preemptible",
			   NULL};

  PyObject * rootModule;
  PyObject * configInstance;

  PyObject * coreModule;
  PyObject * coreDict;

  PyObject * core_Message; // class
  PyObject * core_Message_INFO; // attribute

  PyObject * core_message; // instance
  PyObject * core_message_add; // method
  PyObject * temp_result;

  PyObject * darwin_period_denom_py;
  PyObject * darwin_computation_denom_py;
  PyObject * darwin_constraint_denom_py;
  PyObject * darwin_preemptible_py;

#if defined(__APPLE__)
  PyObject * info_string;

  int darwin_period_denom;
  int darwin_computation_denom;
  int darwin_constraint_denom;
  int darwin_preemptible;

  struct thread_time_constraint_policy ttcpolicy;
  int ret;
  int bus_speed, mib [2] = { CTL_HW, HW_BUS_FREQ };
  size_t len;
#elif defined(_WIN32)
#else
  struct sched_param params;
  int policy;
#endif

  /* Default values for keyword arguments */
  /* borrowed ref */
  darwin_period_denom_py = Py_None;
  darwin_computation_denom_py = Py_None;
  darwin_constraint_denom_py = Py_None;
  darwin_preemptible_py = Py_None;

  /* Get keyword arguments */
  TRY(PyArg_ParseTupleAndKeywords(args,kw,"|O!O!O!O!",kwlist,
				  &PyInt_Type,&darwin_period_denom_py,
				  &PyInt_Type,&darwin_computation_denom_py,
				  &PyInt_Type,&darwin_constraint_denom_py,
				  &PyInt_Type,&darwin_preemptible_py));

  /* Get VisionEgg.config */
  rootModule = PyImport_ImportModule("VisionEgg");
  if (rootModule == NULL) {
    return NULL;
  }
  configInstance = PyObject_GetAttrString(rootModule,"config");
  Py_DECREF(rootModule);
  if (configInstance == NULL) {
    return NULL;
  }

  /* Now set the C types based on the values. */
#if defined(__APPLE__)
  /* darwin specific arguments */

  /* darwin_period_denom */
  if (darwin_period_denom_py != Py_None) {
    darwin_period_denom = PyInt_AS_LONG(darwin_period_denom_py);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_PERIOD_DENOM");
    if (temp_result == NULL) {
      Py_DECREF(configInstance);
      return NULL;
    }
    darwin_period_denom = PyInt_AsLong(temp_result);
    Py_DECREF(temp_result);
    if (PyErr_Occurred()) {
      Py_DECREF(configInstance);
      return NULL;
    }      
  }
  /* darwin_computation_denom */
  if (darwin_computation_denom_py != Py_None) {
    darwin_computation_denom = PyInt_AS_LONG(darwin_computation_denom_py);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_COMPUTATION_DENOM");
    if (temp_result == NULL) {
      Py_DECREF(configInstance);
      return NULL;
    }
    darwin_computation_denom = PyInt_AsLong(temp_result);
    Py_DECREF(temp_result);
    if (PyErr_Occurred()) {
      Py_DECREF(configInstance);
      return NULL;
    }      
  }
  /* darwin_constraint_denom */
  if (darwin_constraint_denom_py != Py_None) {
    darwin_constraint_denom = PyInt_AS_LONG(darwin_constraint_denom_py);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_CONSTRAINT_DENOM");
    if (temp_result == NULL) {
      Py_DECREF(configInstance);
      return NULL;
    }
    darwin_constraint_denom = PyInt_AsLong(temp_result);
    Py_DECREF(temp_result);
    if (PyErr_Occurred()) {
      Py_DECREF(configInstance);
      return NULL;
    }      
  }
  /* darwin_preemptible */
  if (darwin_preemptible_py != Py_None) {
    darwin_preemptible = PyInt_AS_LONG(darwin_preemptible_py);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_PREEMPTIBLE");
    if (temp_result == NULL) {
      Py_DECREF(configInstance);
      return NULL;
    }
    darwin_preemptible = PyInt_AsLong(temp_result);
    Py_DECREF(temp_result);
    if (PyErr_Occurred()) {
      Py_DECREF(configInstance);
      return NULL;
    }      
  }
#endif /* closes if defined(__APPLE__) */

  /* Destroy Python variables we don't need */
  Py_DECREF(configInstance);  configInstance = NULL;

  /* Now get VisionEgg.Core.message to pass message */
  coreModule = PyImport_ImportModule("VisionEgg.Core");
  if (coreModule == NULL) {
    return NULL;
  }

  coreDict = PyModule_GetDict(coreModule);
  /* coreDict is a borrowed ref */
  if (coreDict == NULL) {
    Py_DECREF(coreModule);
    return NULL;
  }

  /* Get VisionEgg.Core.Message (the class) */
  core_Message = PyDict_GetItemString(coreDict, "Message");
  /* core_Message is a borrowed ref */
  if (core_Message == NULL) {
    Py_DECREF(coreModule);
    return NULL;
  }

  /* Get VisionEgg.Core.message (the instance) */
  core_message = PyDict_GetItemString(coreDict, "message");
  /* core_message is a borrowed ref */
  if (core_message == NULL) {
    Py_DECREF(coreModule);
    return NULL;
  }

  core_Message_INFO = PyObject_GetAttrString(core_Message, "INFO" );
  if (core_Message_INFO == NULL) {
    Py_DECREF(coreModule);
    return NULL;
  }

  core_message_add = PyObject_GetAttrString(core_message,"add");
  if (core_message_add == NULL) {
    Py_DECREF(core_Message_INFO);
    Py_DECREF(coreModule);
    return NULL;
  }

  if (!PyCallable_Check(core_message_add)) {
    PyErr_SetString(PyExc_SystemError,"VisionEgg.Core.message.add not callable.");
    Py_DECREF(core_message_add);
    Py_DECREF(core_Message_INFO);
    Py_DECREF(coreModule);
    return NULL;
  }
    
  
#if defined(__APPLE__)
  /* The Apple Mac OS X specific version */

  len = sizeof(bus_speed);
  sysctl( mib, 2, &bus_speed, &len, NULL, 0);

  ttcpolicy.period= bus_speed / darwin_period_denom;
  ttcpolicy.computation=bus_speed / darwin_computation_denom;
  ttcpolicy.constraint=bus_speed / darwin_constraint_denom;
  ttcpolicy.preemptible= darwin_preemptible ;

  info_string = PyString_FromFormat("Setting maximum priority for darwin platform.\n"
				    "( period_denom=%d,\n"
				    "computation_denom=%d,\n"
				    "constraint_denom=%d,\n"
				    "preemptible=%d )",
				    darwin_period_denom,
				    darwin_computation_denom,
				    darwin_constraint_denom,
				    darwin_preemptible);

  if (info_string == NULL) {
    Py_DECREF(core_Message_INFO);
    Py_DECREF(coreModule);
    return NULL;
  }
  
  temp_result = PyObject_CallObject(core_message_add,Py_BuildValue("(O)",info_string));

  //temp_result = PyObject_CallMethod(core_message, "add", "sO", "Setting maximum priority.", core_Message_INFO );
  if (temp_result == NULL) {
    Py_DECREF(core_Message_INFO);
    Py_DECREF(coreModule);
    return NULL;
  }
  Py_DECREF(temp_result);
  Py_XDECREF(temp_result);  // PyObject_CallMethod incremented refcount, but not sure if method decremented it, so using XDECREF
  Py_DECREF(info_string);

  ret=thread_policy_set(mach_thread_self(),
			THREAD_TIME_CONSTRAINT_POLICY,
			(int *)&ttcpolicy,
			THREAD_TIME_CONSTRAINT_POLICY_COUNT);

  if (ret != KERN_SUCCESS) {
    PyErr_SetString(PyExc_RuntimeError,"Failed trying to set realtime priority in Mac OS X.");
    return NULL;
  }

#elif defined(_WIN32)
  temp_result = PyObject_CallMethod(core_message, "add", "sO", "Setting maximum priority for win32 platform.", core_Message_INFO );
  if (temp_result == NULL) {
    Py_DECREF(core_Message_INFO);
    Py_DECREF(coreModule);
    return NULL;
  }
  Py_DECREF(temp_result);
  Py_XDECREF(temp_result);  // PyObject_CallMethod incremented refcount, but not sure if method decremented it, so using XDECREF

  SetPriorityClass(GetCurrentProcess(), REALTIME_PRIORITY_CLASS);
  SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_HIGHEST);
#else

  temp_result = PyObject_CallMethod(core_message, "add", "sO", "Setting maximum priority for POSIX platform.", core_Message_INFO );
  if (temp_result == NULL) {
    Py_DECREF(core_Message_INFO);
    Py_DECREF(coreModule);
    return NULL;
  }
  Py_DECREF(temp_result);
  Py_XDECREF(temp_result);  // PyObject_CallMethod incremented refcount, but not sure if method decremented it, so using XDECREF

  /* This should work on all POSIX non-Apple platforms. */

  /* First, tell the scheduler that we want maximum priority! */
  //  policy = SCHED_RR;
  policy = SCHED_FIFO;
  params.sched_priority = sched_get_priority_max(policy);

  if (sched_setscheduler(0,policy,&params) == -1) { // pid 0 means this process
    switch(errno) {
    case EPERM:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned EPERM (Are you superuser?)");
      return NULL;
      break;
    case ESRCH:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned ESRCH");
      return NULL;
      break;
    case EINVAL:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned EINVAL");
      return NULL;
      break;
    default:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned unknown error");
      return NULL;
      break;
    }
  }
  
#ifdef MCL_CURRENT
#ifdef MCL_FUTURE
  /* Second, prevent the memory from paging. */
  if (mlockall(MCL_CURRENT|MCL_FUTURE) == -1) {
    switch(errno) {
    case EPERM:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned EPERM (Are you superuser?)");
      return NULL;
      break;
    case ESRCH:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned ESRCH");
      return NULL;
      break;
    case EINVAL:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned EINVAL");
      return NULL;
      break;
    default:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned unknown error");
      return NULL;
      break;
    }
  }
#endif /* closes ifdef MCL_FUTURE */
#endif /* closes ifdef MCL_CURRENT */
#endif /* closes all precompiler conditionals */

  // Done with python variables
  Py_DECREF(core_Message_INFO);
  Py_DECREF(coreModule);
  Py_DECREF(core_message_add);

  Py_INCREF(Py_None);
  return Py_None;  /* It worked OK. */
}

static PyMethodDef
_maxpriority_methods[] = {
  { "set_realtime", (PyCFunction)set_realtime, METH_VARARGS | METH_KEYWORDS, set_realtime__doc__},
  { NULL, NULL, 0, NULL} /* sentinel */
};

DL_EXPORT(void)
init_maxpriority(void)
{
  Py_InitModule("_maxpriority", _maxpriority_methods);
  return;
}
