"""
Interrupt and signal handling

See ``tests.pyx`` for extensive tests.
"""

#*****************************************************************************
#       Copyright (C) 2011-2016 Jeroen Demeyer <jdemeyer@cage.ugent.be>
#                     2016 Marc Culler and Nathan Dunfield
#
#  cysignals is free software: you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  cysignals is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with cysignals.  If not, see <http://www.gnu.org/licenses/>.
#
#*****************************************************************************

from libc.signal cimport *
from libc.stdio cimport freopen, stdin
from cpython.exc cimport PyErr_Occurred

cdef extern from "implementation.c":
    void setup_cysignals_handlers() nogil
    void print_backtrace() nogil
    void _sig_on_interrupt_received() nogil
    void _sig_on_recover() nogil
    void _sig_off_warning(const char*, int) nogil


class AlarmInterrupt(KeyboardInterrupt):
    """
    Exception class for :func:`alarm` timeouts.

    EXAMPLES::

        XXX from cysignals import AlarmInterrupt
        XXX from signal import alarm
        XXX try:
        ...     _ = alarm(1)
        ...     while True:
        ...         pass
        ... except AlarmInterrupt:
        ...     print("alarm!")
        alarm!
        XXX from cysignals.signals import sig_print_exception
        XXX import signal
        XXX sig_print_exception(signal.SIGALRM)
        AlarmInterrupt

    """
    pass

class SignalError(BaseException):
    """
    Exception class for critical signals such as ``SIGSEGV``. Inherits
    from ``BaseException`` because these normally should not be handled.

    EXAMPLES::

        >>> import signal
        >>> sig_print_exception(signal.SIGSEGV)
        SignalError: Segmentation fault

    """
    pass


cdef public int sig_raise_exception "sig_raise_exception"(int sig, const char* msg) except 0 with gil:
    """
    Raise an exception for signal number ``sig`` with message ``msg``
    (or a default message if ``msg`` is ``NULL``).
    """
    # Do not raise an exception if an exception is already pending
    if PyErr_Occurred():
        return 0

    # Convert msg to Python string, assuming UTF-8 encoding
    s = msg.decode("utf-8") if msg is not NULL else None

    if sig == SIGTERM:
        # Redirect stdin from /dev/null to close interactive sessions
        _ = freopen("/dev/null", "r", stdin)
        # This causes Python to exit
        raise SystemExit
    if sig == SIGINT:
        raise KeyboardInterrupt
    if sig == SIGILL:
        raise SignalError(s or "Illegal instruction")
    if sig == SIGABRT:
        raise RuntimeError(s or "Aborted")
    if sig == SIGFPE:
        raise FloatingPointError(s or "Floating point exception")
    if sig == SIGSEGV:
        raise SignalError(s or "Segmentation fault")
    IF UNAME_SYSNAME != 'Windows':
        if sig == SIGHUP:
            _ = freopen("/dev/null", "r", stdin)
            raise SystemExit
        if sig == SIGALRM:
            raise AlarmInterrupt
        if sig == SIGBUS:
            raise SignalError(s or "Bus error")
    ELSE:
        if sig == 128:  # Used for signals that map to FPE
            raise RuntimeError(s or "Pari Error")
    raise SystemError("unknown signal number %s"%sig)


def sig_print_exception(sig, msg=None):
    """
    Python version of :func:`sig_raise_exception` which prints the
    exception instead of raising it. This is just for doctesting.

    EXAMPLES::

        XXX from cysignals.signals import sig_print_exception
        >>> import signal
        >>> sig_print_exception(signal.SIGFPE)
        FloatingPointError: Floating point exception

        XXX sig_print_exception(signal.SIGBUS, "CUSTOM MESSAGE")
        SignalError: CUSTOM MESSAGE
        >>> sig_print_exception(0)
        SystemError: unknown signal number 0

    For interrupts, the message is ignored::

        >>> sig_print_exception(signal.SIGINT, "ignored")
        KeyboardInterrupt

        XXX sig_print_exception(signal.SIGALRM, "ignored")
        AlarmInterrupt

    """
    cdef const char* m
    if msg is None:
        m = NULL
    else:
        m = msg = msg.encode("utf-8")

    try:
        sig_raise_exception(sig, m)
    except BaseException as e:
        # Print exception to stdout without traceback
        import sys, traceback
        typ, val, tb = sys.exc_info()
        try:
            # For doctests, we want exceptions to look the same,
            # regardless of the Python version. Python 3 will put the
            # module name in the traceback, which we avoid by faking
            # the module to be __main__.
            typ.__module__ = "__main__"
        except TypeError:
            pass
        try:
            # Python 3
            traceback.print_exception(typ, val, None, file=sys.stdout, chain=False)
        except TypeError:
            # Python 2
            traceback.print_exception(typ, val, None, file=sys.stdout)

cdef cysigs_t cysigs

def init_cysignals():
    """
    Initialize ``cysignals``.

    This is normally done exactly once, namely when importing
    ``cysignals``. However, it is legal to call this multiple times,
    for example when switching between the ``cysignals`` interrupt
    handler and a different interrupt handler.

    OUTPUT: the old Python-level interrupt handler

    EXAMPLES::

        XXX from cysignals.signals import init_cysignals
        >>> init_cysignals()
        <built-in function python_check_interrupt>

    """
    # Set the Python-level interrupt handler. When a SIGINT occurs,
    # this will not be called directly. Instead, a SIGINT is caught by
    # our interrupt handler, set up in implementation.c. If it happens
    # during pure Python code (not within sig_on()/sig_off()), the
    # handler will set Python's interrupt flag. Python regularly checks
    # this and will call its interrupt handler (which is the one we set
    # now). This handler issues a sig_check() which finally raises the
    # KeyboardInterrupt exception.
    import signal
    old = signal.signal(signal.SIGINT, python_check_interrupt)

    setup_cysignals_handlers()
    return old

def sig_on_reset():
    """
    Return the current value of ``cysigs.sig_on_count`` and set its
    value to zero. This is used by the SageMath doctesting framework.

    EXAMPLES::

        XXX from cysignals.signals import sig_on_reset
        XXX from cysignals.tests import _sig_on
        XXX _sig_on(); sig_on_reset()
        1
        XXX sig_on_reset()
        0

    """
    cdef int s = cysigs.sig_on_count
    cysigs.sig_on_count = 0
    return s


def python_check_interrupt(sig, frame):
    """
    Python-level interrupt handler for interrupts raised in Python
    code. This simply delegates to the interrupt handling code in
    ``implementation.c``.
    """
    sig_check()

def test_signal(int sig):
    """
    Test whether critical signals can be handled within a sig_on-sig_off
    block.

    >>> from signal import *
    >>> from cypari._pari import test_signal
    >>> test_signal(SIGFPE)
    Traceback (most recent call last):
        ...
    FloatingPointError: Floating point exception
    >>> test_signal(SIGSEGV)
    Traceback (most recent call last):
        ...
    SignalError: Segmentation fault
    """
    import signal
    if sig == signal.SIGSEGV:
        sig_on()
        test_sigsegv()
        sig_off()
    else:
        sig_on()
        send_signal(sig)
        sig_off()
