from .types cimport *
cimport cython

include "sage.pxi"

cdef class RingElement:
    pass

cdef class gen_auto(RingElement):
    cdef GEN g
    cdef pari_sp b
    cdef dict refers_to

IF SAGE == True:
    cdef class gen_base(gen_auto):
        cpdef int _cmp_(left, Element right) except -2
        cpdef _richcmp_(left, Element right, int op)
ELSE:
    cdef class gen_base(gen_auto):
        pass

@cython.final
cdef class gen(gen_base):
    pass

cpdef gen objtogen(s)
