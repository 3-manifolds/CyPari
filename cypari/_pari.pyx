# Use sys.getdefaultencoding() to convert Unicode strings to <char*>
#
# cython: c_string_encoding=default
"""
Sage class for PARI's GEN type

See the ``Pari`` class for documentation and examples.

AUTHORS:

- William Stein (2006-03-01): updated to work with PARI 2.2.12-beta

- William Stein (2006-03-06): added newtonpoly

- Justin Walker: contributed some of the function definitions

- Gonzalo Tornaria: improvements to conversions; much better error
  handling.

- Robert Bradshaw, Jeroen Demeyer, William Stein (2010-08-15):
  Upgrade to PARI 2.4.3 (:trac:`9343`)

- Jeroen Demeyer (2011-11-12): rewrite various conversion routines
  (:trac:`11611`, :trac:`11854`, :trac:`11952`)

- Peter Bruin (2013-11-17): move Pari to a separate file
  (:trac:`15185`)

- Jeroen Demeyer (2014-02-09): upgrade to PARI 2.7 (:trac:`15767`)

- Martin von Gagern (2014-12-17): Added some Galois functions (:trac:`17519`)

- Jeroen Demeyer (2015-01-12): upgrade to PARI 2.8 (:trac:`16997`)

- Jeroen Demeyer (2015-03-17): automatically generate methods from
  ``pari.desc`` (:trac:`17631` and :trac:`17860`)

- Kiran Kedlaya (2016-03-23): implement infinity type

- Luca De Feo (2016-09-06): Separate Sage-specific components from
  generic C-interface in ``Pari`` (:trac:`20241`)

- Marc Culler and Nathan Dunfield (2016): adaptation for the standalone
  CyPari module.

"""

#*****************************************************************************
#       Copyright (C) 2016-2022 Marc Culler and Nathan Dunfield
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# Define the conditional compilation variable SAGE
include "sage.pxi"

import sys, types
iterable_types = (list, tuple, types.GeneratorType)

cimport cython
from cpython.int cimport PyInt_Check
from cpython.long cimport PyLong_Check
from cpython.bytes cimport PyBytes_Check
from cpython.unicode cimport PyUnicode_Check
from cpython.float cimport PyFloat_AS_DOUBLE
from cpython.complex cimport PyComplex_RealAsDouble, PyComplex_ImagAsDouble
from cpython.object cimport PyTypeObject, PyObject_Call, Py_SIZE	  
from cpython.tuple cimport *
from cpython.int cimport PyInt_AS_LONG, PyInt_FromLong
from cpython.longintrepr cimport _PyLong_New, digit, py_long
from cpython.ref cimport PyObject, Py_XINCREF, Py_XDECREF, Py_INCREF, Py_DECREF
from cpython.exc cimport PyErr_SetString
from cpython cimport PyErr_Occurred

cimport libc.stdlib
from libc.stdio cimport *
from libc.limits cimport LONG_MIN, LONG_MAX
from libc.math cimport INFINITY
from libc.stdlib cimport malloc, calloc, realloc, free

ctypedef unsigned long ulong 'pari_ulong'
ctypedef long* GEN
ctypedef char* byteptr
ctypedef unsigned long pari_sp
include 'pari_long.pxi'
cdef extern const char* closure_func_err()
from .types cimport *
from .paridecl cimport *
from .auto_paridecl cimport *

from warnings import *
try:
    from inspect import getfullargspec as getargspec
except ImportError:
    from inspect import getargspec

cpu_width = '64bit' if sys.maxsize > 2**32 else '32bit'

cdef extern from *:
    """
    /* C code which Cython inserts verbatim into _pari.c.  This provides
     * access to literals which are defined in header files.
     */
    static size_t pari_BITS_IN_LONG = BITS_IN_LONG;
    static int pari_DEFAULTPREC = DEFAULTPREC;
    static int pari_INIT_DFTm = INIT_DFTm;
    static int pari_d_SILENT = d_SILENT;
    static int pari_d_RETURN = d_RETURN;
    static int pari_EQ = Py_EQ;
    static int pari_GE = Py_GE;
    static int pari_LE = Py_LE;
    static int pari_LT = Py_LT;
    static int pari_NE = Py_NE;
    static size_t pari_PyLong_SHIFT = PyLong_SHIFT;
    static int pari_PyLong_MASK = PyLong_MASK;
    static char *pari_PARIVERSION = PARIVERSION;
    """
    size_t pari_BITS_IN_LONG
    int pari_DEFAULTPREC
    int pari_INIT_DFTm
    int pari_d_SILENT
    int pari_d_RETURN
    int pari_EQ
    int pari_GE
    int pari_LE
    int pari_LT
    int pari_NE
    size_t pari_PyLong_SHIFT
    int pari_PyLong_MASK
    char *pari_PARIVERSION

include "memory.pxi"
include "handle_error.pyx"
include "pari_instance.pyx"
include "auto_gen.pxi"
include "gen.pyx"
include "signals.pyx"
init_cysignals()
include "stack.pyx"
include "string_utils.pyx"
include "convert.pyx"
include "closure.pyx"
# Instantiate an instance of the Pari class
cdef Pari pari_instance = Pari()
# and make it accessible from python as `pari`.
pari = pari_instance


