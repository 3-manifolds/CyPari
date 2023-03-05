/*
Interrupt and signal handling for Cython
*/

/*****************************************************************************
 *       Copyright (C) 2006 William Stein <wstein@gmail.com>
 *                     2006-2016 Martin Albrecht <martinralbrecht+cysignals@gmail.com>
 *                     2010-2016 Jeroen Demeyer <jdemeyer@cage.ugent.be>
 *                     2016 Marc Culler and Nathan Dunfield
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
 * This version of cysignals includes both posix and Windows versions, and
 * is embedded in CyPari, rather than being a separate extension module.
 * Some features have been removed for this special use.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with cysignals.  If not, see <http://www.gnu.org/licenses/>.
 *
 ****************************************************************************/
#define ENABLE_DEBUG_CYSIGNALS 0
#if ENABLE_DEBUG_CYSIGNALS
#define DEBUG(...) fprintf(stderr, __VA_ARGS__); fflush(stderr);
#else
#define DEBUG(...)
#endif

/* Posix version */
#if !defined(__MINGW32__) && !defined(_WIN32)

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <execinfo.h>
#include <Python.h>
#include <pari/pari.h>
#include "struct_signals.h"

/* The cysigs object (there is a unique copy of this, shared by all
 * Cython modules using cysignals) */
static cysigs_t cysigs;

/* The default signal mask during normal operation,
 * initialized by setup_cysignals_handlers(). */
static sigset_t default_sigmask;

/* default_sigmask with SIGHUP, SIGINT, SIGALRM added. */
static sigset_t sigmask_with_sigint;


static void do_raise_exception(int sig);
static void sigdie(int sig, const char* s);
static void print_backtrace(void);

/* Handler for SIGHUP, SIGINT, SIGALRM
 *
 * Inside sig_on() (i.e. when cysigs.sig_on_count is positive), this
 * raises an exception and jumps back to sig_on().
 * Outside of sig_on(), we set Python's interrupt flag using
 * PyErr_SetInterrupt() */
static void cysigs_interrupt_handler(int sig)
{
    DEBUG("Call to cysigs_interrupt_handler with signal %d\n", sig)
    if (cysigs.sig_on_count > 0)
    {
      if (!cysigs.block_sigint && !PARI_SIGINT_block)
        {
            /* Raise an exception so Python can see it */
            do_raise_exception(sig);

            /* Jump back to sig_on() (the first one if there is a stack) */
            siglongjmp(cysigs.env, sig);
        }
    }
    else
    {
        /* Set the Python interrupt indicator, which will cause the
         * Python-level interrupt handler in cysignals/signals.pyx to
         * be called. */
        PyErr_SetInterrupt();
    }

    /* If we are here, we cannot handle the interrupt immediately, so
     * we store the signal number for later use.  But make sure we
     * don't overwrite a SIGHUP or SIGTERM which we already received. */
    if (cysigs.interrupt_received != SIGHUP && cysigs.interrupt_received != SIGTERM)
    {
        cysigs.interrupt_received = sig;
        PARI_SIGINT_pending = sig;
    }
}

/* Handler for SIGQUIT, SIGILL, SIGABRT, SIGFPE, SIGBUS, SIGSEGV
 *
 * Inside sig_on() (i.e. when cysigs.sig_on_count is positive), this
 * raises an exception and jumps back to sig_on().
 * Outside of sig_on(), we terminate Python. */
static void cysigs_signal_handler(int sig)
{
    sig_atomic_t inside = cysigs.inside_signal_handler;
    cysigs.inside_signal_handler = 1;
    DEBUG("Call to cysigs_interrupt_handler with signal %d, count=%d\n", sig,
	  cysigs.sig_on_count)

    if (inside == 0 && cysigs.sig_on_count > 0 && sig != SIGQUIT)
    {
        /* We are inside sig_on(), so we can handle the signal! */
        DEBUG("Inside sig_on-sig_off -- calling siglongjmp.\n")
        /* Raise an exception so Python can see it */
        do_raise_exception(sig);

        /* Jump back to sig_on() (the first one if there is a stack) */
        siglongjmp(cysigs.env, sig);
    }
    else
    {
        /* We are outside sig_on() and have no choice but to terminate Python */
        DEBUG("Outside sig-on-sig_off -- terminating Python.\n")

        /* Reset all signals to their default behaviour and unblock
         * them in case something goes wrong as of now. */
        signal(SIGHUP, SIG_DFL);
        signal(SIGINT, SIG_DFL);
        signal(SIGQUIT, SIG_DFL);
        signal(SIGILL, SIG_DFL);
        signal(SIGABRT, SIG_DFL);
        signal(SIGFPE, SIG_DFL);
        signal(SIGBUS, SIG_DFL);
        signal(SIGSEGV, SIG_DFL);
        signal(SIGALRM, SIG_DFL);
        signal(SIGTERM, SIG_DFL);
        sigprocmask(SIG_SETMASK, &default_sigmask, NULL);

        if (inside) sigdie(sig, "An error occurred during signal handling.");

        /* Quit Python with an appropriate message. */
        switch(sig)
        {
            case SIGQUIT:
                sigdie(sig, NULL);
                break;  /* This will not be reached */
            case SIGILL:
                sigdie(sig, "Unhandled SIGILL: An illegal instruction occurred.");
                break;  /* This will not be reached */
            case SIGABRT:
                sigdie(sig, "Unhandled SIGABRT: An abort() occurred.");
                break;  /* This will not be reached */
            case SIGFPE:
                sigdie(sig, "Unhandled SIGFPE: An unhandled floating point exception occurred.");
                break;  /* This will not be reached */
            case SIGBUS:
                sigdie(sig, "Unhandled SIGBUS: A bus error occurred.");
                break;  /* This will not be reached */
            case SIGSEGV:
                sigdie(sig, "Unhandled SIGSEGV: A segmentation fault occurred.");
                break;  /* This will not be reached */
        };
        sigdie(sig, "Unknown signal received.\n");
    }
}


extern int sig_raise_exception(int sig, const char* msg);

/* This calls sig_raise_exception() to actually raise the exception. */
static void do_raise_exception(int sig)
{
    /* Call Cython function to raise exception */
    sig_raise_exception(sig, cysigs.s);
}


/* This will be called during _sig_on_postjmp() when an interrupt was
 * received *before* the call to sig_on(). */
static void _sig_on_interrupt_received(void)
{
    DEBUG("Call to _sig_on_interrupt_received.\n")
    /* Momentarily block signals to avoid race conditions */
    sigset_t oldset;
    sigprocmask(SIG_BLOCK, &sigmask_with_sigint, &oldset);

    do_raise_exception(cysigs.interrupt_received);
    cysigs.sig_on_count = 0;
    cysigs.interrupt_received = 0;
    PARI_SIGINT_pending = 0;

    sigprocmask(SIG_SETMASK, &oldset, NULL);
}

/* Cleanup after siglongjmp() (reset signal mask to the default, set
 * sig_on_count to zero) */
static void _sig_on_recover(void)
{
    DEBUG("Call to _sig_on_recover.\n")
    cysigs.block_sigint = 0;
    PARI_SIGINT_block = 0;
    cysigs.sig_on_count = 0;
    cysigs.interrupt_received = 0;
    PARI_SIGINT_pending = 0;

    /* Reset signal mask */
    sigprocmask(SIG_SETMASK, &default_sigmask, NULL);
    cysigs.inside_signal_handler = 0;
}

/* Give a warning that sig_off() was called without sig_on() */
static void _sig_off_warning(const char* file, int line)
{
    char buf[320];
    snprintf(buf, sizeof(buf), "sig_off() without sig_on() at %s:%i", file, line);

    /* Raise a warning with the Python GIL acquired */
    PyGILState_STATE gilstate_save = PyGILState_Ensure();
    PyErr_WarnEx(PyExc_RuntimeWarning, buf, 2);
    PyGILState_Release(gilstate_save);

    print_backtrace();
}


static void setup_cysignals_handlers(void)
{
    DEBUG("Setting up signal handlers\n")
    /* Reset the cysigs structure */
    memset(&cysigs, 0, sizeof(cysigs));

    /* Save the default signal mask */
    sigprocmask(SIG_BLOCK, NULL, &default_sigmask);

    /* Save the signal mask with non-critical signals blocked */
    sigprocmask(SIG_BLOCK, NULL, &sigmask_with_sigint);
    sigaddset(&sigmask_with_sigint, SIGHUP);
    sigaddset(&sigmask_with_sigint, SIGINT);
    sigaddset(&sigmask_with_sigint, SIGALRM);

    /* Install signal handlers */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    /* Block non-critical signals during the signal handlers */
    sigemptyset(&sa.sa_mask);
    sigaddset(&sa.sa_mask, SIGHUP);
    sigaddset(&sa.sa_mask, SIGINT);
    sigaddset(&sa.sa_mask, SIGALRM);

    sa.sa_handler = cysigs_interrupt_handler;
    if (sigaction(SIGHUP, &sa, NULL)) {perror("sigaction"); exit(1);}
    if (sigaction(SIGINT, &sa, NULL)) {perror("sigaction"); exit(1);}
    if (sigaction(SIGALRM, &sa, NULL)) {perror("sigaction"); exit(1);}
    sa.sa_handler = cysigs_signal_handler;
    /* Allow signals during signal handling, we have code to deal with
     * this case. */
    sa.sa_flags |= SA_NODEFER;
    if (sigaction(SIGQUIT, &sa, NULL)) {perror("sigaction"); exit(1);}
    if (sigaction(SIGILL, &sa, NULL)) {perror("sigaction"); exit(1);}
    if (sigaction(SIGABRT, &sa, NULL)) {perror("sigaction"); exit(1);}
    if (sigaction(SIGFPE, &sa, NULL)) {perror("sigaction"); exit(1);}
    if (sigaction(SIGBUS, &sa, NULL)) {perror("sigaction"); exit(1);}
    if (sigaction(SIGSEGV, &sa, NULL)) {perror("sigaction"); exit(1);}
}


static void print_sep(void)
{
    fprintf(stderr,
        "------------------------------------------------------------------------\n");
    fflush(stderr);
}

/* Print a backtrace if supported by libc */
static void print_backtrace()
{
    void* backtracebuffer[1024];
    fflush(stderr);
    int btsize = backtrace(backtracebuffer, 1024);
    backtrace_symbols_fd(backtracebuffer, btsize, 2);
    print_sep();
}

/* Print a message s and kill ourselves with signal sig */
static void sigdie(int sig, const char* s)
{
    print_sep();
    print_backtrace();

    if (s) {
        fprintf(stderr,
            "%s\n"
            "This probably occurred because a *compiled* module has a bug\n"
            "in it and is not properly wrapped with sig_on(), sig_off().\n"
            "Python will now terminate.\n", s);
        print_sep();
    }

    /* Suicide with signal ``sig`` */
    kill(getpid(), sig);

    /* We should be dead! */
    exit(128 + sig);
}


/* Finally include the macros and inline functions for use in
 * signals.pyx. These require some of the above functions, therefore
 * this include must come at the end of this file. */
#include "macros.h"

#else /* Windows version */

#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <sys/types.h>
#include <Python.h>
#include <stdlib.h>
#include <pari/pari.h>
#include "struct_signals.h"
#include <windows.h>
#include <float.h>

#ifndef __MINGW32__
#  define inline __inline
#endif
/* The cysigs object (there is a unique copy of this, shared by all
 * Cython modules using cysignals) */
static cysigs_t cysigs;

static void do_raise_exception(int sig);
static void sigdie(int sig, const char* s);
static void print_backtrace(void);
static void setup_cysignals_handlers(void);
static void cysigs_interrupt_handler(int sig);
static void cysigs_signal_handler(int sig);

/* Do whatever is needed to reset the CPU to a sane state after
 * handling a signals.  In particular on x86 CPUs, we need to clear
 * the FPU (this is needed after MMX instructions have been used or
 * if an interrupt occurs during an FPU computation).
 * Linux and OS X 10.6 do this as part of their signals implementation,
 * but Solaris doesn't.  Since this code is called only when handling a
 * signal (which should be very rare), it's better to play safe and
 * always execute this instead of special-casing based on the operating
 * system.
 * See http://trac.sagemath.org/sage_trac/ticket/12873
 */
static inline void reset_CPU(void)
{
    _fpreset();
}

/* Handler for SIGINT, SIGALRM
 *
 * On Windows, the way we handle an interrupt immediately is by
 * mapping it to SIGFPE.  Specifically, we save the signal number in
 * cysigs.sig_mapped_to_FPE and raise SIGFPE.  The handler for SIGFPE
 * will then call longjmp.  The reason that it is done this way is
 * that for most signals in Windows the handler is run in a separate
 * thread, with its own stack.  This makes it impossible to call
 * longjmp from a signal handler.  However, longjmp within a signal
 * handler is supported for exactly one signal, namely SIGFPE.
 */
static void cysigs_interrupt_handler(int sig)
{
  DEBUG( "call to cysigs_interrupt_handler with signal %d\n", sig )
  /* Since we are using signal, we must reset the handler. */
  if (signal(sig, cysigs_interrupt_handler) == SIG_ERR)
    {
      perror("signal");
      exit(1);
    }
  if (cysigs.sig_on_count > 0)
    {
      DEBUG( "Inside a sig_on, sig_off block -\n" )
	if (!cysigs.block_sigint && !PARI_SIGINT_block)
        {
	  cysigs.sig_mapped_to_FPE = sig;
	  win32ctrlc += 1;
	  DEBUG( "Incremented win32ctrlc to %d\n", win32ctrlc )
	  return;
        }
    }
  else
    {
      /* Set the Python interrupt indicator, which will cause the
       * Python-level interrupt handler in cysignals/signals.pyx to
       * be called. */
      DEBUG( "Outside a sig_on, sig_off block -Raising Python exception.\n" )
      PyErr_SetInterrupt();
    }
  /* If we are here, we could not handle the interrupt immediately, so
   * we store the signal number for later use.  But make sure we
   * don't overwrite a SIGTERM which we already received. */
  if (cysigs.interrupt_received != SIGTERM)
    {
        cysigs.interrupt_received = sig;
        PARI_SIGINT_pending = sig;
    }
  DEBUG( "Handler returning.\n" )
}

/* Handler for SIGQUIT, SIGILL, SIGABRT, SIGFPE, SIGBUS, SIGSEGV
 *
 * Inside sig_on() (i.e. when cysigs.sig_on_count is positive), this
 * raises an exception and jumps back to sig_on().
 * Outside of sig_on(), we terminate Python.
 *
 */

static void cysigs_signal_handler(int sig)
{
  DEBUG( "call to cysigs_signal_handler for %d with sig_count %d.\n",
	  sig, cysigs.sig_on_count )
  /*
   * Since we are using ANSI signals, we must reset the handler.
   */
  if (signal(sig, cysigs_signal_handler) == SIG_ERR)
    {
      perror("signal");
      exit(1);
    }
  if (cysigs.sig_on_count > 0)
    {
      DEBUG( "Inside sig_on - sig_off block\n" )
      /*
       * We are inside sig_on(), so we can handle the signal!
       *
       * Any signal which needs to be handled immediately, is
       * mapped to FPE by setting sig_mapped_to_FPE and raising
       * SIGFPE.  SIGFPE is the only signal which supports calling
       * longjmp within the handler.
       */
      if (sig == SIGFPE){
	if (cysigs.sig_mapped_to_FPE)
	  {
	    DEBUG( "Mapped from %d\n", cysigs.sig_mapped_to_FPE )
	      int mapped_sig = cysigs.sig_mapped_to_FPE;
	    cysigs.sig_mapped_to_FPE = 0;
	    do_raise_exception(mapped_sig);
	    if (cysigs.FPE_handler != NULL) {
	      signal(SIGFPE, cysigs.FPE_handler);
	    }
	    reset_CPU();
	    DEBUG( "Calling longjmp\n" )
	      longjmp(cysigs.env, mapped_sig);
	  }
	else /* This really is a floating point exception */
	  {
	    reset_CPU();
	    do_raise_exception(SIGFPE);
	    longjmp(cysigs.env, SIGFPE);
	  }
      }
      else
      {
	/* We are not handling SIGFPE, so we Can't longjmp here.  If
	 * the signal is SIGINT then pari will call pari_error later.
	 * Otherwise we need to deal with it somehow.
	*/
	DEBUG( "inside sig_on/sig_off\n" )
	cysigs.sig_mapped_to_FPE = sig;
	if (sig != SIGINT) {
          DEBUG( "raising SIGFPE\n" )
	  raise(SIGFPE);
	}
      }
    }
  else
    {
      /* We are outside sig_on() and have no choice but to terminate Python */
      DEBUG( "outside sig_on/sig_off: killing Python.\n" )
      /* Reset all signals to their default behaviour and unblock
       * them in case something goes wrong.
       */
      signal(SIGINT, SIG_DFL);
      signal(SIGILL, SIG_DFL);
      signal(SIGABRT, SIG_DFL);
      signal(SIGFPE, SIG_DFL);
      signal(SIGSEGV, SIG_DFL);
      signal(SIGTERM, SIG_DFL);

      /* Quit Python with an appropriate message. */
      switch(sig)
        {
	case SIGILL:
	  sigdie(sig, "Unhandled SIGILL: An illegal instruction occurred.");
	  break;  /* This will not be reached */
	case SIGABRT:
	  sigdie(sig, "Unhandled SIGABRT: An abort() occurred.");
	  break;  /* This will not be reached */
	case SIGFPE:
	  sigdie(sig, "Unhandled SIGFPE: An unhandled floating point exception occurred.");
	  break;  /* This will not be reached */
	case SIGSEGV:
	  sigdie(sig, "Unhandled SIGSEGV: A segmentation fault occurred.");
	  break;  /* This will not be reached */
        };
      sigdie(sig, "Unknown signal received.\n");
    }
}

__PYX_EXTERN_C DL_EXPORT(int) sig_raise_exception(int, char const *);
//extern int sig_raise_exception(int sig, const char* msg);

/* This calls sig_raise_exception() to actually raise the exception. */
static void do_raise_exception(int sig)
{
    /* Call Cython function to raise exception */
    sig_raise_exception(sig, cysigs.s);
}


/* This will be called during _sig_on_postjmp() when an interrupt was
 * received *before* the call to sig_on(). */
static void _sig_on_interrupt_received(void)
{
    DEBUG("Call to _sig_on_interrupt_received.\n")
    do_raise_exception(cysigs.interrupt_received);
    cysigs.sig_on_count = 0;
    cysigs.interrupt_received = 0;
    PARI_SIGINT_pending = 0;
}

/* Cleanup after siglongjmp() (set sig_on_count to zero) */
static void _sig_on_recover(void)
{
    DEBUG("Call to _sig_on_recover.\n")
    cysigs.block_sigint = 0;
    PARI_SIGINT_block = 0;
    cysigs.sig_on_count = 0;
    cysigs.interrupt_received = 0;
    PARI_SIGINT_pending = 0;
    win32ctrlc = 0;
}

/* Give a warning that sig_off() was called without sig_on() */
static void _sig_off_warning(const char* file, int line)
{
    char buf[320];
    PyGILState_STATE gilstate_save;
    snprintf(buf, sizeof(buf), "sig_off() without sig_on() at %s:%i", file, line);

    /* Raise a warning with the Python GIL acquired */
    gilstate_save = PyGILState_Ensure();
    PyErr_WarnEx(PyExc_RuntimeWarning, buf, 2);
    PyGILState_Release(gilstate_save);

    print_backtrace();
}

LONG WINAPI
SIGSEGV_generator(struct _EXCEPTION_POINTERS *ExceptionInfo)
{
  if (ExceptionInfo->ExceptionRecord->ExceptionCode ==
      EXCEPTION_ACCESS_VIOLATION) {
    raise(SIGSEGV);
    return EXCEPTION_CONTINUE_EXECUTION;
  } else{
    return EXCEPTION_CONTINUE_SEARCH;
  }
}

static void setup_cysignals_handlers(void)
{
  static PVOID exc_handler = NULL;
  /* Reset the cysigs structure */
  DEBUG("Installing signal handlers.\n")
  memset(&cysigs, 0, sizeof(cysigs));
  if (signal(SIGINT, &cysigs_interrupt_handler) == SIG_ERR ||
      signal(SIGFPE, cysigs_signal_handler) == SIG_ERR     ||
      signal(SIGILL, cysigs_signal_handler) == SIG_ERR     ||
      signal(SIGABRT, cysigs_signal_handler) == SIG_ERR    ||
      signal(SIGSEGV, cysigs_signal_handler) == SIG_ERR    )
    {
      perror("signal");
      exit(1);
    }
   exc_handler = AddVectoredExceptionHandler(1, SIGSEGV_generator);
}

static void print_sep(void)
{
    fprintf(stderr,
        "------------------------------------------------------------------------\n");
    fflush(stderr);
}

static void print_backtrace(void)
{
}

/* Print a message s and kill ourselves with signal sig */
static void sigdie(int sig, const char* s)
{
    print_sep();

    if (s) {
        fprintf(stderr,
            "%s\nsig_on count = %d\n"	
            "This probably occurred because a *compiled* module has a bug\n"
            "in it and is not properly wrapped with sig_on(), sig_off().\n"
	    "Python will now terminate.\n", s, cysigs.sig_on_count);
        print_sep();
    }

    /* Suicide with signal ``sig`` */
    raise(sig);
    /* We should be dead! */
    exit(128 + sig);
}

/* Finally include the macros and inline functions for use in
 * signals.pyx. These require some of the above functions, therefore
 * this include must come at the end of this file. */
#include "macros.h"

#endif
