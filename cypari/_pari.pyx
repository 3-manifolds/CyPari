cython: c_api_binop_methods=False

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
#       Copyright (C) 2016-2017 Marc Culler and Nathan Dunfield
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************
import sys, types
if sys.version_info.major > 2:
    iterable_types = (list, tuple, types.GeneratorType)
else:
    iterable_types = (list, tuple, types.XRangeType, types.GeneratorType)

cimport cython

from cpython.long cimport PyLong_Check
from cpython.bytes cimport PyBytes_Check
from cpython.unicode cimport PyUnicode_Check
from cpython.float cimport PyFloat_AS_DOUBLE
from cpython.complex cimport PyComplex_RealAsDouble, PyComplex_ImagAsDouble
from cpython.object cimport Py_EQ, Py_NE, Py_LE, Py_GE, Py_LT, Py_GT

from .paridecl cimport *
from .paripriv cimport *

# cdef extern from *:
#     """
#     /* Undo the damage caused by PARI's ridiculous
#      * #define long long long
#      */
#     #if defined long
#     #undef long
#     #endif
#     """
#     pass

cimport libc.stdlib
from libc.stdio cimport *

cdef String(x):
    """
    Return a string from either a string or bytes object, using ascii.
    """
    if isinstance(x, str):
        return x
    elif isinstance(x, bytes):
        return x.decode('ascii')
    else:
        raise ValueError('Neither a str nor a bytes object.')

cpu_width = '64bit' if sys.maxsize > 2**32 else '32bit'
cdef extern from *:
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
include "signals.pyx"
init_cysignals()
include "stack.pyx"
include "pari_instance.pyx"
# Instantiate an instance of the Pari class
cdef Pari pari_instance = Pari()
# and make it accessible from python as `pari`.
pari = pari_instance
include "convert.pyx"
include "handle_error.pyx"
include "closure.pyx"
include "gen.pyx"
