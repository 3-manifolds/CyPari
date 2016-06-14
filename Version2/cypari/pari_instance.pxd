from .types cimport *
cimport cython
from gen cimport gen
    
cpdef long prec_bits_to_words(unsigned long prec_in_bits)
cpdef long prec_words_to_bits(long prec_in_words)
cpdef long default_bitprec()

cdef class PariInstance_auto:
    pass

@cython.final
cdef class PariInstance(PariInstance_auto):
    cdef long _real_precision
    cdef readonly gen PARI_ZERO, PARI_ONE, PARI_TWO
    cpdef gen zero(self)
    cpdef gen one(self)
    cdef inline gen new_gen(self, GEN x)
    cdef inline gen new_gen_noclear(self, GEN x)
    cdef gen new_gen_from_int(self, int value)
    cdef gen new_t_POL_from_int_star(self, int *vals, int length, long varnum)
    cdef inline void clear_stack(self)
    cdef gen double_to_gen_c(self, double)
    cdef GEN double_to_GEN(self, double)
    cdef GEN deepcopy_to_python_heap(self, GEN x, pari_sp* address)
    cdef gen new_ref(self, GEN g, gen parent)
    cdef gen _empty_vector(self, long n)
    cdef long get_var(self, v)

cdef PariInstance pari_instance