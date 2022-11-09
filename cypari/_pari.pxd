cimport cython
include "sage.pxi"

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

