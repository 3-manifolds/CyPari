/*
Interrupt and signal handling for Cython.

This code distinguishes between two kinds of signals:

(1) interrupt-like signals: SIGINT, SIGALRM, SIGHUP.  The word
"interrupt" refers to any of these signals.  These need not be handled
immediately, we might handle them at a suitable later time, outside of
sig_block() and with the Python GIL acquired.  SIGINT raises a
KeyboardInterrupt (as usual in Python), SIGALRM raises AlarmInterrupt
(a custom exception inheriting from KeyboardInterrupt), while SIGHUP
raises SystemExit, causing Python to exit.  The latter signal also
redirects stdin from /dev/null, to cause interactive sessions to exit.

(2) critical signals: SIGQUIT, SIGILL, SIGABRT, SIGFPE, SIGBUS, SIGSEGV.
These are critical because they cannot be ignored.  If they happen
outside of sig_on(), we can only exit Python with the dreaded
"unhandled SIG..." message.  Inside of sig_on(), they can be handled
and raise various exceptions (see cysignals/signals.pyx).  SIGQUIT
will never be handled and always causes Python to exit.

*/

/*****************************************************************************
 *       Copyright (C) 2006 William Stein <wstein@gmail.com>
 *                     2006 Martin Albrecht <martinralbrecht+cysignals@gmail.com>
 *                     2010-2016 Jeroen Demeyer <jdemeyer@cage.ugent.be>
 *
 * cysignals is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * cysignals is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with cysignals.  If not, see <http://www.gnu.org/licenses/>.
 *
 ****************************************************************************/


#ifndef CYSIGNALS_MACROS_H
#define CYSIGNALS_MACROS_H

#include <setjmp.h>
#include <signal.h>
#include "struct_signals.h"

#ifdef __cplusplus
extern "C" {
#endif


/**********************************************************************
 * IMPLEMENTATION OF SIG_ON/SIG_OFF                                   *
 **********************************************************************/

/*
 * Implementation of sig_on().  Applications should not use this
 * directly, use sig_on() or sig_str() instead.
 *
 * _sig_on_(message) is a macro which pretends to be a function.
 * Since this is declared as "cdef except 0", Cython will know that an
 * exception occurred if the value of _sig_on_() is 0 (false).
 *
 * INPUT:
 *
 *  - message -- a string to be displayed as error message when the code
 *    between sig_on() and sig_off() fails and raises an exception.
 *
 * OUTPUT: zero if an exception occurred, non-zero otherwise.
 *
 * The function sigsetjmp() in the _sig_on_() macro can return:
 *  - zero: this happens in the actual sig_on() call. sigsetjmp() sets
 *    up the address for the signal handler to jump to.  The
 *    program continues normally.
 *  - a signal number (e.g. 2 for SIGINT), assumed to be strictly
 *    positive: the cysignals signal handler handled a signal.  Since
 *    _sig_on_() will return 0 in this case, the Exception (raised by
 *    cysigs_signal_handler) will be detected by Cython.
 *  - a negative number: this is assumed to come from sig_retry().  In
 *    this case, the program continues as if nothing happened between
 *    sig_on() and sig_retry().
 *
 * We cannot simply put sigsetjmp() in a function, because when that
 * function returns, we would lose the stack frame to siglongjmp() to.
 * That's why we need this hackish macro.  We use the fact that || is
 * a short-circuiting operator (the second argument is only evaluated
 * if the first returns 0).
 */
#if defined(__MINGW32__) || defined(_WIN32)
#define _sig_on_(message) ( unlikely(_sig_on_prejmp(message, __FILE__, __LINE__)) || _sig_on_postjmp(setjmp(cysigs.env)) )
  //#define _sig_on_(message) ( 1 )
#else
  #define _sig_on_(message) ( unlikely(_sig_on_prejmp(message, __FILE__, __LINE__)) || _sig_on_postjmp(sigsetjmp(cysigs.env,0)) )
#endif
  
/*
 * Set message, return 0 if we need to sigsetjmp(), return 1 otherwise.
 */
static inline int _sig_on_prejmp(const char* message, const char* file, int line)
{
    cysigs.s = message;
    DEBUG("sig_on: setting count to %i at %s:%i\n", cysigs.sig_on_count+1, file, line)
    if (cysigs.sig_on_count > 0)
    {
        cysigs.sig_on_count++;
        return 1;
    }

    /* At this point, cysigs.sig_on_count == 0 */
    return 0;
}


/*
 * Process the return value of sigsetjmp().
 * Return 0 if there was an exception, 1 otherwise.
 */
static inline int _sig_on_postjmp(int jmpret)
{
    if (unlikely(jmpret > 0))
    {
        /* An exception occurred */
        _sig_on_recover();
        return 0;
    }

    /* When we are here, it's either the original sig_on() call or we
     * got here after sig_retry(). */
    cysigs.sig_on_count = 1;

    /* Check whether we received an interrupt before this point.
     * cysigs.interrupt_received can only be set by the interrupt
     * handler if cysigs.sig_on_count is zero.  Because of that and
     * because cysigs.sig_on_count and cysigs.interrupt_received are
     * volatile, we can safely evaluate cysigs.interrupt_received here
     * without race conditions. */
    if (unlikely(cysigs.interrupt_received))
    {
        _sig_on_interrupt_received();
        return 0;
    }

    return 1;
}


/*
 * Implementation of sig_off().  Applications should not use this
 * directly, use sig_off() instead.
 */
static inline void _sig_off_(const char* file, int line)
{
  DEBUG("sig_off: setting count to %i at %s:%i\n", cysigs.sig_on_count-1, file, line)
  if (unlikely(cysigs.sig_on_count <= 0))
    {
      _sig_off_warning(file, line);
    }
  else
    {
      --cysigs.sig_on_count;
#if defined(__MINGW32__) || defined(_WIN32)
      /* If a pari_error was generated, mingw32ctrlc should be reset to 0. */
      if (win32ctrlc > 0)
	{
	win32ctrlc = 0;
	raise(SIGINT);
	}
#endif
    }
}


/**********************************************************************
 * USER MACROS/FUNCTIONS                                              *
 **********************************************************************/

/* The actual macros which should be used in a program. */
#define sig_on()           _sig_on_(NULL)
#define sig_str(message)   _sig_on_(message)
#define sig_off()          _sig_off_(__FILE__, __LINE__)

/* sig_check() should be functionally equivalent to sig_on(); sig_off();
 * but much faster.  Essentially, it checks whether we missed any
 * interrupts.
 *
 * OUTPUT: zero if an interrupt occurred, non-zero otherwise.
 */
static inline int sig_check(void)
{
    if (unlikely(cysigs.interrupt_received) && cysigs.sig_on_count == 0)
    {
        _sig_on_interrupt_received();
        return 0;
    }

    return 1;
}


/*
 * Temporarily block interrupts from happening inside sig_on().  This
 * is meant to wrap malloc() for example.  sig_unblock() checks whether
 * an interrupt happened in the mean time.  If yes, the interrupt is
 * re-raised.
 *
 * NOTES:
 * - This only works inside sig_on()/sig_off().  Outside of sig_on(),
 *   interrupts behave as usual.  This is because we can't propagate
 *   Python exceptions from low-level C code.
 * - Other signals still go through, because we can't really ignore
 *   SIGSEGV for example.
 * - For efficiency reasons, currently these may NOT be nested.
 *   Nesting could be implemented like src/headers/pariinl.h in PARI.
 */
static inline void sig_block(void)
{
#if ENABLE_DEBUG_CYSIGNALS
    if (cysigs.block_sigint != 0)
    {
      DEBUG("sig_block called with sig_on_count = %i, block_sigint = %i\n", cysigs.sig_on_count, cysigs.block_sigint);
        //print_backtrace();
    }
#endif
    cysigs.block_sigint = 1;
}

static inline void sig_unblock(void)
{
    cysigs.block_sigint = 0;

#if defined(__MINGW32__) || defined(_WIN32)
    if (unlikely(cysigs.interrupt_received) && cysigs.sig_on_count > 0)
      raise(cysigs.interrupt_received);  /* Re-raise the signal */
#else
    if (unlikely(cysigs.interrupt_received) && cysigs.sig_on_count > 0)
        kill(getpid(), cysigs.interrupt_received);  /* Re-raise the signal */
#endif
}


/*
 * Retry a failed computation starting from sig_on().  This is useful
 * for PARI: if PARI complains that it doesn't have enough memory, we
 * allocate a larger stack and retry the computation.
 */
static inline void sig_retry(void)
{
    /* If we're outside of sig_on(), we can't jump, so we can only bail
     * out */
    DEBUG("Call to sig_retry.\n")
    if (unlikely(cysigs.sig_on_count <= 0))
    {
      DEBUG( "sig_retry() without sig_on()\n")
#if defined(__MINGW32__) || defined(_WIN32)
	// FIX ME!!!!
	raise(SIGFPE);
#else
        abort();
#endif
    }
    siglongjmp(cysigs.env, -1);
}

/* This is called by Pari's cb_pari_err_recover callback.
 * In Posix this sends a SIGABRT.  In Windows this raises SIGFPE
 * with an out-of-range mapped signal.  The signal handler should
 * either do a longjmp back to the last sig_on, or schedule one for later.
 */
static inline void sig_error(void)
{
#if defined(__MINGW32__) || defined(_WIN32)
    void (*old_handler)(int);
#endif
    DEBUG( "sig_error called with count %d\n", cysigs.sig_on_count)
    if (unlikely(cysigs.sig_on_count <= 0))
    {
        fprintf(stderr, "sig_error() without sig_on()\n");
    }
#if defined(__MINGW32__) || defined(_WIN32)
    /* 
     * The Windows abort function will terminate the process no
     * matter what.  If a SIGABRT handler is set it will be called,
     * but that is only to allow cleanup before the process is terminated.
     * So we can't call abort if we are on Windows.
     */
    
    cysigs.sig_mapped_to_FPE = 128;

    /*
     * Make sure that we have the correct signal handler set before we
     * raise a SIGFPE.  If the handler has been intentionally reset we
     * will restore it after the mapped signal has been handled.
     */

    old_handler = signal(SIGFPE, cysigs_signal_handler);
    if (old_handler != NULL && old_handler != cysigs_signal_handler) {
      cysigs.FPE_handler = old_handler;
    } else {
      cysigs.FPE_handler = NULL;
    }
    DEBUG("sig_error raising SIGFPE\n")
    raise(SIGFPE);
#else
    abort();
#endif
}

#define test_sigsegv() {int *p = (void*)5; *p = 5;}
#if defined(__MINGW32__) || defined(_WIN32)
  #define send_signal(sig) raise(sig)
#else
  #define send_signal(sig) kill(getpid(), sig)
#endif
  
#ifdef __cplusplus
}  /* extern "C" */
#endif

#endif  /* ifndef CYSIGNALS_MACROS_H */
