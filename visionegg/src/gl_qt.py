# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.
import _gl_qt
def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


initialize_quicktime = _gl_qt.initialize_quicktime

gl_qt_renderer_create = _gl_qt.gl_qt_renderer_create

gl_qt_renderer_delete = _gl_qt.gl_qt_renderer_delete

gl_qt_renderer_update = _gl_qt.gl_qt_renderer_update

load_movie = _gl_qt.load_movie

LoadMovieIntoRam = _gl_qt.LoadMovieIntoRam

PrerollMovie = _gl_qt.PrerollMovie

GetMovieDuration = _gl_qt.GetMovieDuration

GetMovieTimeScale = _gl_qt.GetMovieTimeScale

GetMovieTimeBase = _gl_qt.GetMovieTimeBase

GetMovieRate = _gl_qt.GetMovieRate

IsMovieDone = _gl_qt.IsMovieDone

MoviesTask = _gl_qt.MoviesTask

StartMovie = _gl_qt.StartMovie

StopMovie = _gl_qt.StopMovie

GetMovieActiveSegment = _gl_qt.GetMovieActiveSegment

GoToBeginningOfMovie = _gl_qt.GoToBeginningOfMovie

GoToEndOfMovie = _gl_qt.GoToEndOfMovie

GetMovieBox = _gl_qt.GetMovieBox


