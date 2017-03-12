from .types cimport *
cimport cython

include "sage.pxi"

cdef class RingElement:
    pass

cdef class Gen_auto(RingElement):
    cdef GEN g
    cdef pari_sp b
    cdef dict refers_to

IF SAGE:
    cdef class gen_base(Gen_auto):
        cpdef int _cmp_(left, Element right) except -2
        cpdef _richcmp_(left, Element right, int op)
ELSE:
    cdef class gen_base(Gen_auto):
        pass

@cython.final
cdef class Gen(gen_base):
    pass

cpdef Gen objtogen(s)


IF SAGE == False:
    cpdef long prec_bits_to_words(unsigned long prec_in_bits)
    cpdef long prec_words_to_bits(long prec_in_words)
    cpdef long default_bitprec(long bitprec=*)

    cdef class Pari_auto:
        pass
    cdef class Pari_base(Pari_auto):
        pass
    
    # pari_instance.pyx
    @cython.final
    cdef class Pari(Pari_base):
        cdef long _real_precision
        cdef readonly Gen PARI_ZERO, PARI_ONE, PARI_TWO
        cpdef Gen zero(self)
        cpdef Gen one(self)
        cdef Gen new_gen_from_int(self, int value)
        cdef Gen new_t_POL_from_int_star(self, int *vals, int length, long varnum)
        cdef Gen double_to_gen_c(self, double)
        cdef GEN double_to_GEN(self, double)
        cdef Gen _empty_vector(self, long n)
        cpdef _real_coerced_to_bits_prec(self, double x, long bits)
        cdef _UI_callback

    cdef long get_var(v) except -2
    cdef Pari pari_instance

    # stack.pyx
    cdef GEN deepcopy_to_python_heap(GEN x, pari_sp* address)
    cdef inline Gen new_gen(GEN x)
    cdef inline Gen new_gen_noclear(GEN x)
    cdef inline void clear_stack()

    cdef void _pari_init_error_handling()
    cdef int _pari_err_handle(GEN E) except 0
    cdef void _pari_err_recover(long errnum)

    cdef extern from *:
        int sig_on() nogil except 0
        int sig_str(char*) nogil except 0
        int sig_check() nogil except 0
        void sig_off() nogil
        void sig_retry() nogil  # Does not return
        void sig_error() nogil  # Does not return
        void sig_block() nogil
        void sig_unblock() nogil

        # for testing signal handling
        void send_signal(int sig) nogil
        void test_sigsegv() nogil

        # Macros behaving exactly like sig_on, sig_str and sig_check but
        # which are *not* declared "except 0".  This is useful if some
        # low-level Cython code wants to do its own exception handling.
        int sig_on_no_except "sig_on"() nogil
        int sig_str_no_except "sig_str"(char*) nogil
        int sig_check_no_except "sig_check"() nogil

        # Do we need to declare these?
        # void print_backtrace() nogil
        # void _sig_on_interrupt_received() nogil
        # void _sig_on_recover() nogil
        # void _sig_off_warning(const char*, int) nogil

    # This function does nothing, but it is declared cdef except *, so it
    # can be used to make Cython check whether there is a pending exception
    # (PyErr_Occurred() is non-NULL). To Cython, it will look like
    # cython_check_exception() actually raised the exception.
    cdef inline void cython_check_exception() nogil except *:
        pass


# Private stuff below, do not use directly
cdef extern from "struct_signals.h":
    ctypedef struct cysigs_t:
        int sig_on_count
        const char* s

cdef api:
     cysigs_t cysigs "cysigs"
#     void print_backtrace() nogil
#     void _sig_on_interrupt_received() nogil
#     void _sig_on_recover() nogil
#     void _sig_off_warning(const char*, int) nogil
