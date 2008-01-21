#emacs, this is -*-Python-*- mode
import numpy

ctypedef int GLenum
ctypedef int GLint
ctypedef int GLsizei

cdef extern from "vegl.h":
    void glGetTexImage( int, int, int, int, void* )
    void glTexSubImage1D( GLenum, GLint, GLint, GLsizei, GLenum, GLenum, void* )

cdef extern from "Python.h":
    ctypedef int Py_intptr_t
    void* PyCObject_AsVoidPtr(object)

# numpy's __array_struct__ interface:
ctypedef struct PyArrayInterface:
    int two                       # contains the integer 2 as a sanity check
    int nd                        # number of dimensions
    char typekind                 # kind in array --- character code of typestr
    int itemsize                  # size of each element
    int flags                     # flags indicating how the data should be interpreted
    Py_intptr_t *shape            # A length-nd array of shape information
    Py_intptr_t *strides          # A length-nd array of stride information
    void *data                    # A pointer to the first element of the array

def veglGetTexImage(target, level, format, type, buf):
    cdef PyArrayInterface* inter

    hold_onto_until_done_with_array = buf.__array_struct__
    inter = <PyArrayInterface*>PyCObject_AsVoidPtr( hold_onto_until_done_with_array )
    assert inter.two == 2

    glGetTexImage(target, level, format, type, inter.data )

def veglTexSubImage1D( target, level, xoffset, width, format, type, data ):
    # PyOpenGL 2.0.1.09 has a bug, so use our own wrapper
    cdef PyArrayInterface* inter

    hold_onto_until_done_with_array = data.__array_struct__
    inter = <PyArrayInterface*>PyCObject_AsVoidPtr( hold_onto_until_done_with_array )
    assert inter.two == 2

    glTexSubImage1D( target, level, xoffset, width, format, type, inter.data)
