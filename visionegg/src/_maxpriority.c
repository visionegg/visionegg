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
#include <pthread.h>
#include <sched.h>
#include <sys/errno.h>
#include <sys/resource.h>
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

#define PY_CHECK(X) if (!(X)) goto error

static char set_realtime__doc__[] = 
"Raise the Vision Egg to maximum priority.\n"
"\n"
"The following optional keyword arguments only have an effect\n"
"on the platform specified. If not specified, the value\n"
"is taken from VisionEgg.config, which by default is\n"
"the value in parentheses.\n"
"\n"
"  darwin_realtime_period_denom (120)\n"
"  darwin_realtime_computation_denom (2400)\n"
"  darwin_realtime_constraint_denom (1200)\n"
"  darwin_realtime_preemptible (0)\n"
"  darwin_maxpriority_conventional_not_realtime (0) (Disables above realtime arguments)\n"
"  darwin_conventional_priority (-20) (-20 is maximum priority)\n"
"  darwin_pthread_priority (\"max\")\n"
"  win32_process_priority_class (\"HIGH_PRIORITY_CLASS\")\n"
"  win32_thread_priority_level (\"THREAD_PRIORITY_TIME_CRITICAL\")\n"
"  posix_scheduling_policy (\"SCHED_FIFO\")\n"
"  posix_scheduling_priority_less_than_max (0)\n";

static PyObject *set_realtime(PyObject *self, PyObject *args, PyObject *kw)
{
  /* We will parse all the keywords on all platforms because they
     should be legal, but we just won't care what there values are
     when they are irrelevant. */

  static char *kwlist[] = {"darwin_realtime_period_denom",
			   "darwin_realtime_computation_denom",
			   "darwin_realtime_constraint_denom",
			   "darwin_realtime_preemptible",
			   "darwin_maxpriority_conventional_not_realtime",
			   "darwin_conventional_priority",
			   "darwin_pthread_priority",
			   NULL};

  PyObject * rootModule=NULL;
  PyObject * configInstance=NULL;

  PyObject * coreModule=NULL;
  PyObject * coreDict=NULL;

  PyObject * core_Message=NULL; // class
  PyObject * core_Message_INFO=NULL; // attribute

  PyObject * core_message=NULL; // instance
  PyObject * core_message_add=NULL; // method
  PyObject * temp_result=NULL;

  PyObject * darwin_realtime_period_denom_py=NULL;
  PyObject * darwin_realtime_computation_denom_py=NULL;
  PyObject * darwin_realtime_constraint_denom_py=NULL;
  PyObject * darwin_realtime_preemptible_py=NULL;
  PyObject * darwin_maxpriority_conventional_not_realtime_py=NULL;
  PyObject * darwin_conventional_priority_py=NULL;
  PyObject * darwin_pthread_priority_py=NULL;
  PyObject * info_string=NULL;

#if defined(__APPLE__)
  int darwin_realtime_period_denom;
  int darwin_realtime_computation_denom;
  int darwin_realtime_constraint_denom;
  int darwin_realtime_preemptible;
  int darwin_maxpriority_conventional_not_realtime;
  int _darwin_get_max_pthread_priority;
  int darwin_conventional_priority;
  int darwin_pthread_priority;

  // for realtime
  struct thread_time_constraint_policy ttcpolicy;
  int ret;
  int bus_speed, mib [2] = { CTL_HW, HW_BUS_FREQ };
  size_t len;

  // for conventional
  int current_priority;
  struct sched_param sp;

#elif defined(_WIN32)
#else
  struct sched_param params;
  int policy;
#endif

  /* Default values for keyword arguments */
  /* borrowed refs */
  darwin_realtime_period_denom_py = Py_None;
  darwin_realtime_computation_denom_py = Py_None;
  darwin_realtime_constraint_denom_py = Py_None;
  darwin_realtime_preemptible_py = Py_None;
  darwin_maxpriority_conventional_not_realtime_py = Py_None;
  darwin_conventional_priority_py = Py_None;
  darwin_pthread_priority_py = Py_None;

  /* Get keyword arguments */
  PY_CHECK(PyArg_ParseTupleAndKeywords(args,kw,"|O!O!O!O!O!O!O",kwlist,
				       &PyInt_Type,&darwin_realtime_period_denom_py,
				       &PyInt_Type,&darwin_realtime_computation_denom_py,
				       &PyInt_Type,&darwin_realtime_constraint_denom_py,
				       &PyInt_Type,&darwin_realtime_preemptible_py,
				       &PyInt_Type,&darwin_maxpriority_conventional_not_realtime_py,
				       &PyInt_Type,&darwin_conventional_priority_py,
				       &darwin_pthread_priority_py));


  /* Get VisionEgg.config */
  rootModule = PyImport_ImportModule("VisionEgg"); /* New reference */
  PY_CHECK(rootModule);

  configInstance = PyObject_GetAttrString(rootModule,"config"); /* New reference */
  PY_CHECK(configInstance);

  Py_DECREF(rootModule); // Don't need it any more

  /* Now set the C types based on the values. */

  /* darwin specific arguments */
#if defined(__APPLE__)
  /* darwin_realtime_period_denom */
  if (darwin_realtime_period_denom_py != Py_None) {
    /* User passed keyword argument */
    temp_result = darwin_realtime_period_denom_py;
    Py_INCREF(temp_result);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_PERIOD_DENOM"); /* New ref */
    PY_CHECK(temp_result);
  }
  darwin_realtime_period_denom = PyInt_AsLong(temp_result);
  Py_DECREF(temp_result); // don't need it
  if (PyErr_Occurred())
    goto error;

  /* darwin_realtime_computation_denom */
  if (darwin_realtime_computation_denom_py != Py_None) {
    /* User passed keyword argument */
    temp_result = darwin_realtime_computation_denom_py;
    Py_INCREF(temp_result);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_COMPUTATION_DENOM");
    PY_CHECK(temp_result);
  }
  darwin_realtime_computation_denom = PyInt_AsLong(temp_result);
  Py_DECREF(temp_result); // don't need it
  if (PyErr_Occurred())
    goto error;

  /* darwin_realtime_constraint_denom */
  if (darwin_realtime_constraint_denom_py != Py_None) {
    /* User passed keyword argument */
    temp_result = darwin_realtime_constraint_denom_py;
    Py_INCREF(temp_result);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_CONSTRAINT_DENOM");
    PY_CHECK(temp_result);
  }
  darwin_realtime_constraint_denom = PyInt_AsLong(temp_result);
  Py_DECREF(temp_result); // don't need it
  if (PyErr_Occurred())
    goto error;

  /* darwin_realtime_preemptible */
  if (darwin_realtime_preemptible_py != Py_None) {
    /* User passed keyword argument */
    temp_result = darwin_realtime_preemptible_py;
    Py_INCREF(temp_result);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_REALTIME_PREEMPTIBLE");
    PY_CHECK(temp_result);
  }
  darwin_realtime_preemptible = PyInt_AsLong(temp_result);
  Py_DECREF(temp_result); // don't need it
  if (PyErr_Occurred())
    goto error;

  /* darwin_maxpriority_conventional_not_realtime */
  if (darwin_maxpriority_conventional_not_realtime_py != Py_None) {
    /* User passed keyword argument */
    temp_result = darwin_maxpriority_conventional_not_realtime_py;
    Py_INCREF(temp_result);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_MAXPRIORITY_CONVENTIONAL_NOT_REALTIME");
    PY_CHECK(temp_result);
  }
  darwin_maxpriority_conventional_not_realtime = PyInt_AsLong(temp_result);
  Py_DECREF(temp_result); // don't need it
  if (PyErr_Occurred())
    goto error;

  /* darwin_conventional_priority */
  if (darwin_conventional_priority_py != Py_None) {
    /* User passed keyword argument */
    temp_result = darwin_conventional_priority_py;
    Py_INCREF(temp_result);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_CONVENTIONAL_PRIORITY");
    PY_CHECK(temp_result);
  }
  darwin_conventional_priority = PyInt_AsLong(temp_result);
  Py_DECREF(temp_result); // don't need it
  if (PyErr_Occurred())
    goto error;

  /* darwin_pthread_priority */
  if (darwin_pthread_priority_py != Py_None) {
    /* User passed keyword argument */
    temp_result = darwin_pthread_priority_py;
    Py_INCREF(temp_result);
  } else {
    /* Get value from VisionEgg.config */
    temp_result = PyObject_GetAttrString(configInstance,"VISIONEGG_DARWIN_PTHREAD_PRIORITY");
    PY_CHECK(temp_result);
  }
  _darwin_get_max_pthread_priority = 0; /* if temp_result == "max": _darwin_get_max_pthread_priority = 1; */ 
  darwin_pthread_priority = 0; // Dummy value so compiler doesn't complain
  if (PyString_Check(temp_result)) {
    if (!strcmp(PyString_AsString(temp_result),"max")) {
      _darwin_get_max_pthread_priority = 1;
    }
    else {
      PyErr_SetString(PyExc_ValueError,"If darwin_pthread_priority is a string, it can only be \"max\".");
    }
  } else {
    darwin_pthread_priority = PyInt_AsLong(temp_result);
  }
  Py_DECREF(temp_result); // don't need it
  if (PyErr_Occurred())
    goto error;
#endif // closes if defined(__APPLE__)

  // Now get VisionEgg.Core.message to pass message 
  coreModule = PyImport_ImportModule("VisionEgg.Core"); // New ref
  PY_CHECK(coreModule);

  coreDict = PyModule_GetDict(coreModule); // borrowed ref
  PY_CHECK(coreDict);

  // Get VisionEgg.Core.Message (the class)
  core_Message = PyDict_GetItemString(coreDict, "Message"); // borrowed ref
  PY_CHECK(core_Message);

  // Get VisionEgg.Core.message (the instance)
  core_message = PyDict_GetItemString(coreDict, "message"); // borrowed ref
  PY_CHECK(core_message);

  // Get VisionEgg.Core.Message.INFO
  core_Message_INFO = PyObject_GetAttrString(core_Message, "INFO" ); // new ref
  PY_CHECK(core_Message_INFO);

  // Get VisionEgg.Core.message.add
  core_message_add = PyObject_GetAttrString(core_message,"add"); // new ref
  PY_CHECK(core_message_add);

  if (!PyCallable_Check(core_message_add)) {
    PyErr_SetString(PyExc_SystemError,"VisionEgg.Core.message.add not callable.");
    goto error;
  }
  
#if defined(__APPLE__)
  /* The Apple Mac OS X specific version */

  if (!darwin_maxpriority_conventional_not_realtime) { // use realtime

    len = sizeof(bus_speed);
    sysctl( mib, 2, &bus_speed, &len, NULL, 0);

    ttcpolicy.period= bus_speed / darwin_realtime_period_denom;
    ttcpolicy.computation=bus_speed / darwin_realtime_computation_denom;
    ttcpolicy.constraint=bus_speed / darwin_realtime_constraint_denom;
    ttcpolicy.preemptible= darwin_realtime_preemptible ;

    info_string = PyString_FromFormat("Setting max priority mode for darwin platform using realtime threads. "
				      "( period = %d / %d, "
				      "computation = %d / %d, "
				      "constraint = %d / %d, "
				      "preemptible=%d )",
				      bus_speed, darwin_realtime_period_denom,
				      bus_speed, darwin_realtime_computation_denom,
				      bus_speed, darwin_realtime_constraint_denom,
				      darwin_realtime_preemptible); // new ref
    PY_CHECK(info_string);
  
    temp_result = PyObject_CallObject(core_message_add,Py_BuildValue("(O)",info_string)); // new ref
    PY_CHECK(temp_result); // make sure it worked

    // clean up Python variables
    Py_DECREF(temp_result); 
    Py_DECREF(info_string);

    // do it
    ret=thread_policy_set(mach_thread_self(),
			  THREAD_TIME_CONSTRAINT_POLICY,
			  (int *)&ttcpolicy,
			  THREAD_TIME_CONSTRAINT_POLICY_COUNT);

    if (ret != KERN_SUCCESS) {
      PyErr_SetString(PyExc_RuntimeError,"Failed trying to set realtime priority in Mac OS X.");
      goto error;
    }
  } else {// use conventional priority stuff
    
    errno = 0;
    current_priority = getpriority(PRIO_PROCESS,0);
    switch (errno) {
    case 0:
      break;
    case ESRCH:
      PyErr_SetString(PyExc_RuntimeError,"Failed to get current priority: ESRCH: No process was located.");
      goto error;
    case EINVAL:
      PyErr_SetString(PyExc_RuntimeError,"Failed to get current priority: EINVAL: Invalid value.");
      goto error;
    default:
      PyErr_SetString(PyExc_SystemError,"Failed to get current priority: Unknown error value.");
      goto error;
    }

    // set priority before doing pthread stuff -- they manipulate the current thread of the task
    if (!setpriority(PRIO_PROCESS,0,darwin_conventional_priority)) {
      switch (errno) {
      case EPERM:
	PyErr_SetString(PyExc_RuntimeError,"Failed to change priority: EPERM: User ID does not match user ID of process.");
	goto error;
      case EACCES:
	PyErr_SetString(PyExc_RuntimeError,"Failed to change priority: EACCES: A non super-user attempted to lower a process priority.");
	goto error;
      default:
	PyErr_SetString(PyExc_SystemError,"Failed to change priority: Unknown error value.");
	goto error;
      }
    }

    // find priority to use if necessary
    if (_darwin_get_max_pthread_priority) {
      darwin_pthread_priority = sched_get_priority_max(SCHED_RR);
    }
    
    info_string = PyString_FromFormat("Setting priority for darwin platform using conventional priority. "
				      "( Changing process priority from %d to %d. Setting pthread priority = %d, pthread policy = SCHED_RR )",
				      current_priority,
				      darwin_conventional_priority,
				      darwin_pthread_priority); // new ref
    PY_CHECK(info_string);
  
    temp_result = PyObject_CallObject(core_message_add,Py_BuildValue("(O)",info_string)); // new ref
    PY_CHECK(temp_result); // make sure it worked

    // clean up Python variables
    Py_DECREF(temp_result); 
    Py_DECREF(info_string);

    memset(&sp,0,sizeof(struct sched_param));
    sp.sched_priority=darwin_pthread_priority;
    if (pthread_setschedparam(pthread_self(), SCHED_RR, &sp) == -1) {
      PyErr_SetString(PyExc_RuntimeError,"Failed to change pthread priority.");
      goto error;
    }

  }

#elif defined(_WIN32)
  /* Add message saying what's about to happen. */
  info_string = PyString_FromFormat("Setting priority for win32 platform. "
				    "( Process priority class REALTIME_PRIORITY_CLASS, "
				    "thread priority THREAD_PRIORITY_HIGHEST)"); // new ref
  PY_CHECK(info_string);
  
  temp_result = PyObject_CallObject(core_message_add,Py_BuildValue("(O)",info_string)); // new ref
  PY_CHECK(temp_result); // make sure it worked

  // clean up Python variables
  Py_DECREF(temp_result); 
  Py_DECREF(info_string);

  SetPriorityClass(GetCurrentProcess(), REALTIME_PRIORITY_CLASS);
  SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_HIGHEST);
#else

  /* This should work on all POSIX non-Apple platforms. */

  /* First, tell get the maximum priority value for our scheduling policy. */
  //  policy = SCHED_RR;
  policy = SCHED_FIFO;
  params.sched_priority = sched_get_priority_max(policy);

  /* Add message saying what's about to happen. */
  info_string = PyString_FromFormat("Setting priority for POSIX platform. "
				    "( Policy SCHED_FIFO, priority %d, which is the maximum possible priority - 0 )",
				    params.sched_priority); // new ref
  PY_CHECK(info_string);
  
  temp_result = PyObject_CallObject(core_message_add,Py_BuildValue("(O)",info_string)); // new ref
  PY_CHECK(temp_result); // make sure it worked

  // clean up Python variables
  Py_DECREF(temp_result); 
  Py_DECREF(info_string);

  /* Do it now */
  if (sched_setscheduler(0,policy,&params) == -1) { // pid 0 means this process
    switch(errno) {
    case EPERM:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned EPERM (Permission error. Do you have permission; are you superuser?)");
      goto error;
    case ESRCH:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned ESRCH");
      goto error;
    case EINVAL:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned EINVAL");
      goto error;
    default:
      PyErr_SetString(PyExc_RuntimeError,"sched_setscheduler returned unknown error");
      goto error;
    }
  }
  
#ifdef MCL_CURRENT
#ifdef MCL_FUTURE
  /* Prevent the memory from paging. */
  if (mlockall(MCL_CURRENT|MCL_FUTURE) == -1) {
    switch(errno) {
    case EPERM:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned EPERM (Are you superuser?)");
      goto error;
    case ESRCH:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned ESRCH");
      goto error;
    case EINVAL:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned EINVAL");
      goto error;
    default:
      PyErr_SetString(PyExc_RuntimeError,"mlockall returned unknown error");
      goto error;
    }
  }
#endif /* closes ifdef MCL_FUTURE */
#endif /* closes ifdef MCL_CURRENT */
#endif /* closes all precompiler conditionals */

  /* Destroy Python variables we don't need */
  Py_DECREF(configInstance);
  Py_DECREF(coreModule);
  Py_DECREF(core_Message_INFO);
  Py_DECREF(core_message_add);

  Py_INCREF(Py_None);
  return Py_None;  /* It worked OK. */

 error:

  Py_XDECREF(rootModule);
  Py_XDECREF(configInstance);
  Py_XDECREF(temp_result);
  Py_XDECREF(coreModule);
  Py_XDECREF(core_Message_INFO);
  Py_XDECREF(info_string);
  
  if (!PyErr_Occurred()) {
    // Make sure an exception is raised if we exit this way.
    PyErr_SetString(PyExc_SystemError,"An internal error occurred in _maxpriority.c.");
  }

  return NULL; /* It failed. */
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
