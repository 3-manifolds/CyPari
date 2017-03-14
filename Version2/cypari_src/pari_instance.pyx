"""
PARI C-library interface

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

- Peter Bruin (2013-11-17): split off this file from gen.pyx
  (:trac:`15185`)

- Jeroen Demeyer (2014-02-09): upgrade to PARI 2.7 (:trac:`15767`)

- Jeroen Demeyer (2014-09-19): upgrade to PARI 2.8 (:trac:`16997`)

- Jeroen Demeyer (2015-03-17): automatically generate methods from
  ``pari.desc`` (:trac:`17631` and :trac:`17860`)

- Luca De Feo (2016-09-06): Separate Sage-specific components from
  generic C-interface in ``Pari`` (:trac:`20241`)

- Marc Culler and Nathan Dunfield (2016-2017): adaptation for the standalone
  CyPari module.

EXAMPLES::

    sage: pari('5! + 10/x')
    (120*x + 10)/x
    sage: pari('intnum(x=0,13,sin(x)+sin(x^2) + x)')
    85.6215190762676
    sage: f = pari('x^3-1')
    sage: v = f.factor(); v
    [x - 1, 1; x^2 + x + 1, 1]
    sage: v[0]   # indexing is 0-based unlike in GP.
    [x - 1, x^2 + x + 1]~
    sage: v[1]
    [1, 1]~

Arithmetic operations cause all arguments to be converted to PARI::

    sage: type(pari(1) + 1)
    <type 'cypari._pari.Gen'>
    sage: type(1 + pari(1))
    <type 'cypari._pari.Gen'>

Guide to real precision in the PARI interface
=============================================

In the PARI interface, "real precision" refers to the precision of real
numbers, so it is the floating-point precision. This is a non-trivial
issue, since there are various interfaces for different things.

Internal representation of floating-point numbers in PARI
---------------------------------------------------------

Real numbers in PARI have a precision associated to them, which is
always a multiple of the CPU wordsize. So, it is a multiple of 32
of 64 bits. When converting a ``float`` from Python to PARI, the
``float`` has 53 bits of precision which is rounded up to 64 bits
in PARI::

    sage: x = 1.0
    sage: pari(x)
    1.00000000000000
    sage: pari(x).bitprecision()
    64

It is possible to change the precision of a PARI object with the
:meth:`Gen.bitprecision` method::

    sage: p = pari(1.0)
    sage: p.bitprecision()
    64
    sage: p = p.bitprecision(100)
    sage: p.bitprecision()   # Rounded up to a multiple of the wordsize
    128

Beware that these extra bits are just bogus. For example, this will not
give a more precision approximation of ``math.pi``:

    sage: p = pari(math.pi)
    sage: pari("Pi") - p
    1.225148... E-16
    sage: p = p.bitprecision(1000)
    sage: pari("Pi") - p
    1.225148... E-16

Another way to create numbers with many bits is to use a string with
many digits::

    sage: p = pari("3.1415926535897932384626433832795028842")
    sage: p.bitprecision()
    128

.. _pari_output_precision:

Output precision for printing
-----------------------------

Even though PARI reals have a precision, not all significant bits are
printed by default. The maximum number of digits when printing a PARI
real can be set using the methods
:meth:`Pari.set_real_precision_bits` or
:meth:`Pari.set_real_precision`.
Note that this will also change the input precision for strings,
see :ref:`pari_input_precision`.

We create a very precise approximation of pi and see how it is printed
in PARI::

    sage: pi = pari.pi(precision=1024)

The default precision is 15 digits::

    sage: pi
    3.14159265358979

With a different precision, we see more digits. Note that this does not
affect the object ``pi`` at all, it only affects how it is printed::

    sage: _ = pari.set_real_precision(50)
    sage: pi
    3.1415926535897932384626433832795028841971693993751

Back to the default::

    sage: _ = pari.set_real_precision(15)
    sage: pi
    3.14159265358979

Note, however, that setting the real precision to 15 digits only
provides 50 bits of precision, rather than the default bit precision
of 53, which is chosen to match the precision of a standard 64 bit
floating point number.

sage: pari.set_real_precision(15)
15
sage: pari.get_real_precision_bits()
50
sage: pari.set_real_precision_bits(53)

.. _pari_input_precision:

Input precision for function calls
----------------------------------

When we talk about precision for PARI functions, we need to distinguish
three kinds of calls:

1. Using the string interface, for example ``pari("sin(1)")``.

2. Using the library interface with exact inputs, for example
   ``pari(1).sin()``.

3. Using the library interface with inexact inputs, for example
   ``pari(1.0).sin()``.

In the first case, the relevant precision is the one set by the methods
:meth:`Pari.set_real_precision_bits` or
:meth:`Pari.set_real_precision`::

    sage: pari.set_real_precision_bits(150)
    sage: pari("sin(1)")
    0.841470984807896506652502321630298999622563061
    sage: pari.set_real_precision_bits(53)
    sage: pari("sin(1)")
    0.841470984807897

In the second case, the precision can be given as the argument
``precision`` in the function call, with a default of 53 bits.
The real precision set by
:meth:`Pari.set_real_precision_bits` or
:meth:`Pari.set_real_precision` does not affect the call
(but it still affects printing).

As explained before, the precision increases to a multiple of the
wordsize. ::

    sage: a = pari(1).sin(precision=180); a
    0.841470984807897
    sage: a.bitprecision()
    192
    sage: b = pari(1).sin(precision=40); b
    0.841470984807897
    sage: b.bitprecision()
    64
    sage: c = pari(1).sin(); c
    0.841470984807897
    sage: c.bitprecision()
    64
    sage: pari.set_real_precision_bits(90)
    sage: print(a); print(b); print(c)
    0.841470984807896506652502322
    0.8414709848078965067
    0.8414709848078965067

In the third case, the precision is determined only by the inexact
inputs and the ``precision`` argument is ignored::

    sage: pari(1.0).sin(precision=180).bitprecision()
    64
    sage: pari(1.0).sin(precision=40).bitprecision()
    64
    sage: pari("1.0000000000000000000000000000000000000").sin().bitprecision()
    128

Elliptic curve functions
------------------------

An elliptic curve given with exact `a`-invariants is considered an
exact object. Therefore, you should set the precision for each method
call individually::

    sage: e = pari([0,0,0,-82,0]).ellinit()
    sage: eta1 = e.elleta(precision=100)[0]
    sage: eta1.sage()
    3.6054636014326520859158205642077267748
    sage: eta1 = e.elleta(precision=180)[0]
    sage: eta1.sage()
    3.60546360143265208591582056420772677481026899659802474544

TESTS:

Check that output from PARI's print command is actually seen by
Sage (:trac:`9636`)::

    sage: pari('print("test")')
    test

Check that ``default()`` works properly::

    sage: pari.default("debug")
    0
    sage: pari.default("debug", 3)
    sage: pari(2**67+1).factor()
    IFAC: cracking composite
            49191317529892137643
    IFAC: factor 6713103182899
            is prime
    IFAC: factor 7327657
            is prime
    IFAC: prime 7327657
            appears with exponent = 1
    IFAC: prime 6713103182899
            appears with exponent = 1
    IFAC: found 2 large prime (power) factors.
    [3, 1; 7327657, 1; 6713103182899, 1]
    sage: pari.default("debug", 0)
    sage: pari(2**67+1).factor()
    [3, 1; 7327657, 1; 6713103182899, 1]
"""

#*****************************************************************************
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

# Define the conditional compilation variable SAGE
include "sage.pxi"

""" Sage header -- not used by the standalone CyPari
from __future__ import absolute_import, division

include "cysignals/signals.pxi"

import sys
from libc.stdio cimport *
cimport cython

from .paridecl cimport *
from .paripriv cimport *
from .gen cimport Gen, objtogen
from .stack cimport new_gen, new_gen_noclear, clear_stack
from .convert cimport new_gen_from_double
from .handle_error cimport _pari_init_error_handling
from .closure cimport _pari_init_closure
"""

# Default precision (in PARI words) for the PARI library interface,
# when no explicit precision is given and the inputs are exact.
cdef long prec = prec_bits_to_words(53)


IF not SAGE:
    cdef deprecation(int id, char* message):
        # Decide how to handle this in CyPari
        pass
    cdef deprecated_function_alias(id, alias):
        return alias

cdef extern from *:
    int sig_on_count "cysigs.sig_on_count"

#################################################################
# conversions between various real precision models
#################################################################

def prec_bits_to_dec(long prec_in_bits):
    r"""
    Convert from precision expressed in bits to precision expressed in
    decimal.

    EXAMPLES::

        sage: from cypari._pari import prec_bits_to_dec
        sage: prec_bits_to_dec(53)
        15
        sage: [prec_bits_to_dec(32*n) for n in range(1, 9)]
        [9, 19, 28, 38, 48, 57, 67, 77]
    """
    return nbits2ndec(prec_in_bits)

def prec_dec_to_bits(long prec_in_dec):
    r"""
    Convert from precision expressed in decimal to precision expressed
    in bits.

    EXAMPLES::

        sage: from cypari._pari import prec_dec_to_bits
        sage: prec_dec_to_bits(15)
        50
        sage: [prec_dec_to_bits(n) for n in range(10, 100, 10)]
        [34, 67, 100, 133, 167, 200, 233, 266, 299]
    """
    cdef double log_10 = 3.32192809488736
    return int(prec_in_dec*log_10 + 1.0)  # Add one to round up

cpdef long prec_bits_to_words(unsigned long prec_in_bits):
    r"""
    Convert from precision expressed in bits to pari real precision
    expressed in words. Note: this rounds up to the nearest word,
    adjusts for the two codewords of a pari real, and is
    architecture-dependent.

    EXAMPLES::

        sage: from cypari._pari import prec_bits_to_words
        sage: prec_bits_to_words(70)
        5   # 32-bit
        4   # 64-bit

    ::

        sage: [(32*n, prec_bits_to_words(32*n)) for n in range(1, 9)]
        [(32, 3), (64, 4), (96, 5), (128, 6), (160, 7), (192, 8), (224, 9), (256, 10)] # 32-bit
        [(32, 3), (64, 3), (96, 4), (128, 4), (160, 5), (192, 5), (224, 6), (256, 6)] # 64-bit
    """
    if not prec_in_bits:
        return prec
    cdef unsigned long wordsize = BITS_IN_LONG

    # This equals ceil(prec_in_bits/wordsize) + 2
    return (prec_in_bits - 1)//wordsize + 3

cpdef long prec_words_to_bits(long prec_in_words):
    r"""
    Convert from pari real precision expressed in words to precision
    expressed in bits. Note: this adjusts for the two codewords of a
    pari real, and is architecture-dependent.

    EXAMPLES::

        sage: from cypari._pari import prec_words_to_bits
        sage: prec_words_to_bits(10)
        256   # 32-bit
        512   # 64-bit
        sage: [(n, prec_words_to_bits(n)) for n in range(3, 10)]
        [(3, 32), (4, 64), (5, 96), (6, 128), (7, 160), (8, 192), (9, 224)]  # 32-bit
        [(3, 64), (4, 128), (5, 192), (6, 256), (7, 320), (8, 384), (9, 448)] # 64-bit
    """
    # see user's guide to the pari library, page 10
    return (prec_in_words - 2) * BITS_IN_LONG

cpdef long default_bitprec():
    r"""
    Return the default precision in bits.

    EXAMPLES::

        sage: from cypari._pari import default_bitprec
        sage: default_bitprec()
        64
    """
    return (prec - 2) * BITS_IN_LONG

def prec_dec_to_words(long prec_in_dec):
    r"""
    Convert from precision expressed in decimal to precision expressed
    in words. Note: this rounds up to the nearest word, adjusts for the
    two codewords of a pari real, and is architecture-dependent.

    EXAMPLES::

        sage: from cypari._pari import prec_dec_to_words
        sage: prec_dec_to_words(38)
        6   # 32-bit
        4   # 64-bit
        sage: [(n, prec_dec_to_words(n)) for n in range(10, 90, 10)]
        [(10, 4), (20, 5), (30, 6), (40, 7), (50, 8), (60, 9), (70, 10), (80, 11)] # 32-bit
        [(10, 3), (20, 4), (30, 4), (40, 5), (50, 5), (60, 6), (70, 6), (80, 7)] # 64-bit
    """
    return prec_bits_to_words(prec_dec_to_bits(prec_in_dec))

def prec_words_to_dec(long prec_in_words):
    r"""
    Convert from precision expressed in words to precision expressed in
    decimal. Note: this adjusts for the two codewords of a pari real,
    and is architecture-dependent.

    EXAMPLES::

        sage: from cypari._pari import prec_words_to_dec
        sage: prec_words_to_dec(5)
        28   # 32-bit
        57   # 64-bit
        sage: [(n, prec_words_to_dec(n)) for n in range(3, 10)]
        [(3, 9), (4, 19), (5, 28), (6, 38), (7, 48), (8, 57), (9, 67)] # 32-bit
        [(3, 19), (4, 38), (5, 57), (6, 77), (7, 96), (8, 115), (9, 134)] # 64-bit
    """
    return prec_bits_to_dec(prec_words_to_bits(prec_in_words))


# Callbacks from PARI to print stuff using sys.stdout.write() instead
# of C library functions like puts().
cdef PariOUT sage_pariOut

cdef void sage_putchar(char c):
    cdef char s[2]
    s[0] = c
    s[1] = 0
    sys.stdout.write(String(s))
    # Let PARI think the last character was a newline,
    # so it doesn't print one when an error occurs.
    pari_set_last_newline(1)
    
cdef void sage_puts(const char* s):
    sys.stdout.write(String(s))
    pari_set_last_newline(1)

cdef void sage_flush():
    sys.stdout.flush()

cdef void swallow_ch(char ch):
    return

cdef void swallow_s(const char* s):
    return

include 'auto_instance.pxi'

@cython.final
cdef class Pari(Pari_auto):
    
    def __init__(self, long size=1000000, unsigned long maxprime=500000):
        """
        Initialize the PARI system.

        INPUT:


        -  ``size`` -- long, the number of bytes for the initial
           PARI stack (see note below)

        -  ``maxprime`` -- unsigned long, upper limit on a
           precomputed prime number table (default: 500000)


        .. note::

           In Sage, the PARI stack is different than in GP or the
           PARI C library. In Sage, instead of the PARI stack
           holding the results of all computations, it *only* holds
           the results of an individual computation. Each time a new
           Python/PARI object is computed, it is copied to its own
           space in the Python heap, and the memory it occupied on the
           PARI stack is freed. Thus it is not necessary to make the
           stack very large. Also, unlike in PARI, if the stack does
           overflow, in most cases the PARI stack is automatically
           increased and the relevant step of the computation rerun.

           This design obviously involves some performance penalties
           over the way PARI works, but it scales much better and is
           far more robust for large projects.

        .. note::

           If you do not want prime numbers, put ``maxprime=2``, but be
           careful because many PARI functions require this table. If
           you get the error message "not enough precomputed primes",
           increase this parameter.
        """
        if avma:
            return  # pari already initialized.

        # PARI has a "real" stack size (parisize) and a "virtual" stack
        # size (parisizemax). The idea is that the real stack will be
        # used if possible, but the stack might be increased up to
        # the complete virtual stack. Therefore, it is not a problem to
        # set the virtual stack size to a large value. There are two
        # constraints for the virtual stack size:
        # 1) on 32-bit systems, even virtual memory can be a scarce
        #    resource since it is limited by 4GB (of which the kernel
        #    needs a significant part)
        # 2) the system should actually be able to handle a stack size
        #    as large as the complete virtual stack.
        # As a simple heuristic, we set the virtual stack to 1/4 of the
        # virtual memory.

        pari_init_opts(size, maxprime, INIT_DFTm)
        IF SAGE:
            from sage.misc.memory_info import MemoryInfo
            mem = MemoryInfo()
            sizemax = mem.virtual_memory_limit() // 4
            
            if CYGWIN_VERSION and CYGWIN_VERSION < (2, 5, 2):
                # Cygwin's mmap is broken for large NORESERVE mmaps (>~ 4GB) See
                # http://trac.sagemath.org/ticket/20463 So we set the max stack
                # size to a little below 4GB (putting it right on the margin proves
                # too fragile)
                #
                # The underlying issue is fixed in Cygwin v2.5.2
                sizemax = min(sizemax, 0xf0000000)
 
            paristack_setsize(size, sizemax)
        ELSE:
            from memory import total_ram
            if cpu_width == '32bit':
                sizemax = min(total_ram() // 4, 2**30)
            else:
                sizemax = total_ram() // 4
            paristack_setsize(size, sizemax)
        
        # Disable PARI's stack overflow checking which is incompatible
        # with multi-threading.
        pari_stackcheck_init(NULL)

        _pari_init_error_handling()

        # pari_init_opts() overrides MPIR's memory allocation functions,
        # so we need to reset them.
        IF SAGE:
           init_memory_functions()

        # Set printing functions
        global pariOut, pariErr

        pariOut = &sage_pariOut
        pariOut.putch = sage_putchar
        pariOut.puts = sage_puts
        pariOut.flush = sage_flush

        # Use 15 decimal digits as default precision
        self.set_real_precision_bits(53)

        # Disable pretty-printing
        GP_DATA.fmt.prettyp = 0

        # This causes PARI/GP to use output independent of the terminal
        # (which is what we want for the PARI library interface).
        GP_DATA.flags = gpd_TEST

        # Ensure that Galois groups are represented in a sane way,
        # see the polgalois section of the PARI users manual.
        global new_galois_format
        new_galois_format = 1

        # By default, factor() should prove primality of returned
        # factors. This not only influences the factor() function, but
        # also many functions indirectly using factoring.
        global factor_proven
        factor_proven = 1

        # Initialize some constants
        sig_on()
        self.PARI_ZERO = new_gen_noclear(gen_0)
        self.PARI_ONE = new_gen_noclear(gen_1)
        self.PARI_TWO = new_gen_noclear(gen_2)
        sig_off()

    def shut_up(self):
        global pariErr
        pariErr.putch = swallow_ch
        pariErr.puts = swallow_s

    def speak_up(self):
        global pariErr
        pariErr.putch = sage_putchar
        pariErr.puts = sage_puts
        
    @property
    def UI_callback(self):
        return self._UI_callback
    @UI_callback.setter
    def UI_callback(self, callback):
        self._UI_callback = callback
    
    def debugstack(self):
        r"""
        Print the internal PARI variables ``top`` (top of stack), ``avma``
        (available memory address, think of this as the stack pointer),
        ``bot`` (bottom of stack).

        EXAMPLE::

            sage: pari.debugstack()  # random
            top =  0x60b2c60
            avma = 0x5875c38
            bot =  0x57295e0
            size = 1000000
        """
        # We deliberately use low-level functions to minimize the
        # chances that something goes wrong here (for example, if we
        # are out of memory).
        printf("top =  %p\navma = %p\nbot =  %p\nsize = %lu\n",
               <void *>pari_mainstack.top, <void *>avma, <void *>pari_mainstack.bot,
               <unsigned long>pari_mainstack.rsize)
        fflush(stdout)

    def __dealloc__(self):
        """
        Deallocation of the Pari instance.

        NOTE:

        Usually this deallocation happens only when Sage quits.
        We do not provide a direct test, since usually there
        is only one Pari instance, and when artificially creating
        another instance, C-data are shared.

        The fact that Sage does not crash when quitting is an
        indirect doctest. See the discussion at :trac:`13741`.

        """
        if avma:
            pari_close()

    def __repr__(self):
        return "Interface to the PARI C library"

    def __hash__(self):
        return 907629390   # hash('pari')

    def set_debug_level(self, level):
        """
        Set the debug PARI C library variable.
        """
        self.default('debug', int(level))

    def get_debug_level(self):
        """
        Set the debug PARI C library variable.
        """
        return int(self.default('debug'))

    def set_real_precision_bits(self, n):
        """
        Sets the PARI default real precision in bits.

        This is used both for creation of new objects from strings and
        for printing. It determines the number of digits in which real
        numbers numbers are printed. It also determines the precision
        of objects created by parsing strings (e.g. pari('1.2')), which
        is *not* the normal way of creating new pari objects in Sage.
        It has *no* effect on the precision of computations within the
        PARI library.

        .. seealso:: :meth:`set_real_precision` to set the
           precision in decimal digits.

        EXAMPLES::

            sage: pari.set_real_precision_bits(200)
            sage: pari('1.2')
            1.20000000000000000000000000000000000000000000000000000000000
            sage: pari.set_real_precision_bits(53)
        """
        cdef bytes strn = str(n).encode("ascii")
        sig_on()
        sd_realbitprecision(strn, d_SILENT)
        sig_off()

    def get_real_precision_bits(self):
        """
        Return the current PARI default real precision in bits.

        This is used both for creation of new objects from strings and
        for printing. It determines the number of digits in which real
        numbers numbers are printed. It also determines the precision
        of objects created by parsing strings (e.g. pari('1.2')), which
        is *not* the normal way of creating new pari objects in Sage.
        It has *no* effect on the precision of computations within the
        PARI library.

        .. seealso:: :meth:`get_real_precision` to get the
           precision in decimal digits.

        EXAMPLES::

            sage: pari.set_real_precision(15)
            15
            sage: pari.get_real_precision_bits()
            50
            sage: pari.set_real_precision_bits(53)
            sage: pari.get_real_precision_bits()
            53
        """
        cdef long r
        sig_on()
        r = itos(sd_realbitprecision(NULL, d_RETURN))
        sig_off()
        return r

    def set_real_precision(self, long n):
        """
        Sets the PARI default real precision in bits.

        This is used both for creation of new objects from strings and
        for printing. It determines the number of digits in which real
        numbers numbers are printed. It also determines the precision
        of objects created by parsing strings (e.g. pari('1.2')), which
        is *not* the normal way of creating new pari objects in Sage.
        It has *no* effect on the precision of computations within the
        PARI library.

        .. seealso:: :meth:`set_real_precision` to set the
           precision in decimal digits.

        EXAMPLES::

            sage: pari.set_real_precision_bits(200)
            sage: pari('1.2')
            1.20000000000000000000000000000000000000000000000000000000000
            sage: pari.set_real_precision_bits(53)
        """
        old = self.get_real_precision()
        self.set_real_precision_bits(prec_dec_to_bits(n))
        return old

    
    def get_real_precision(self):
        """
        Returns the current PARI default real precision.

        This is used both for creation of new objects from strings and for
        printing. It is the number of digits *IN DECIMAL* in which real
        numbers are printed. It also determines the precision of objects
        created by parsing strings (e.g. pari('1.2')), which is *not* the
        normal way of creating new pari objects in Sage. It has *no*
        effect on the precision of computations within the pari library.

        EXAMPLES::

            sage: pari.get_real_precision()
            15
         """
        cdef long r
        sig_on()
        r = itos(sd_realprecision(NULL, d_RETURN))
        sig_off()
        return r

    def set_series_precision(self, int n):
        global precdl
        precdl = n

    def get_series_precision(self):
        return <int>precdl

    # def get_default_bit_precision(self):
    #     return default_bitprec()
        
    # def set_default_bit_precision(self, int n):
    #     """
    #     Set the default bit precision for real and complex Gens.

    #     >>> pari.get_default_bit_precision()
    #     64
    #     >>> pari.pi()
    #     3.14159265358979
    #     >>> pari.pi().precision()
    #     3  # 64-bit
    #     4  # 32-bit
    #     >>> pari.set_default_bit_precision(212)
    #     64
    #     >>> pari.get_default_bit_precision()
    #     256 # 64-bit
    #     224 # 32-bit
    #     >>> pari.pi()
    #     3.14159265358979
    #     >>> pari.pi().precision()
    #     6  # 64-bit
    #     9  # 32-bit
    #     >>> old_real_precision = pari.set_real_precision(50)
    #     >>> pari.pi()
    #     3.1415926535897932384626433832795028841971693993751
    #     >>> pari.set_default_bit_precision(64)
    #     256 # 64-bit
    #     224 # 32-bit
    #     >>> pari.pi()
    #     3.141592653589793239
    #     >>> pari.set_real_precision(old_real_precision)
    #     50
    #     >>> pari.pi()
    #     3.14159265358979
    #     >>> pari.set_real_precision_bits(53)
    #     50
    #     """
    #     return default_bitprec(n)

    cdef Gen new_gen_from_int(self, int value):
        sig_on()
        return new_gen(stoi(value))

    def double_to_gen(self, x):
        cdef double dx
        dx = float(x)
        return self.double_to_gen_c(dx)

    cdef Gen double_to_gen_c(self, double x):
        """
        Create a new gen with the value of the double x, using Pari's
        dbltor.

        EXAMPLES::

            sage: pari.double_to_gen(1)
            1.00000000000000
            sage: pari.double_to_gen(1e30)
            1.00000000000000 E30
            sage: pari.double_to_gen(0)
            0.E-15
            sage: pari.double_to_gen(-sqrt(RDF(2)))
            -1.41421356237310

        >>> pari.double_to_gen(1)
        1.00000000000000
        >>> pari.double_to_gen(1e30)
        1.00000000000000 E30
        >>> pari.double_to_gen(0)
        0.E-15
        >>> pari.double_to_gen(-sqrt(RDF(2)))
        -1.41421356237310
        """
        # Pari has an odd concept where it attempts to track the accuracy
        # of floating-point 0; a floating-point zero might be 0.0e-20
        # (meaning roughly that it might represent any number in the
        # range -1e-20 <= x <= 1e20).

        # Pari's dbltor converts a floating-point 0 into the Pari real
        # 0.0e-307; Pari treats this as an extremely precise 0.  This
        # can cause problems; for instance, the Pari incgam() function can
        # be very slow if the first argument is very precise.

        # So we translate 0 into a floating-point 0 with 53 bits
        # of precision (that's the number of mantissa bits in an IEEE
        # double).

        sig_on()
        if x == 0:
            return new_gen(real_0_bit(-53))
        else:
            return new_gen(dbltor(x))

    cdef GEN double_to_GEN(self, double x):
        if x == 0:
            return real_0_bit(-53)
        else:
            return dbltor(x)

    cpdef _real_coerced_to_bits_prec(self, double x, long bits):
        r""" 
        Creates a PARI t_REAL with value given by the float x, coerced
        to at least the given precision.  The resulting gen object
        will have word length (not including codewords) which is large
        enough to provide the requested number of bits, but no larger.

        >>> from cypari._pari import prec_bits_to_words
        >>> old_precision = pari.set_real_precision(64)
        >>> x = pari._real_coerced_to_bits_prec(1.23456789012345678, 100)
        >>> x
        1.23456789012345669043213547411141917109
        >>> x.length() == prec_bits_to_words(100) - 2
        True
        >>> pari.set_real_precision(old_precision)
	64

        Here the pari Gen uses two 64 bit words to provide at least
        100 bits of precision.  This can be used, for example, to convert
        quad-double numbers to pari numbers.
        """
        cdef long words = prec_bits_to_words(bits)
        cdef GEN g
        sig_on()
        if x == 0:
            return new_gen(real_0_bit(-bits))
        else:
            g = dbltor(x)
            return new_gen(gtofp(g, words))

    def complex(self, re, im):
        """
        Create a new complex number, initialized from re and im.
        """
        cdef Gen t0 = self(re)
        cdef Gen t1 = self(im)
        sig_on()
        return new_gen(mkcomplex(t0.g, t1.g))

    def __call__(self, s):
        """
        Create the PARI object obtained by evaluating s using PARI.

        EXAMPLES::

            sage: pari(0)
            0
            sage: pari([2,3,5])
            [2, 3, 5]

        ::

            sage: a = pari(1); a, a.type()
            (1, 't_INT')
            sage: a = pari('1/2'); a, a.type()
            (1/2, 't_FRAC')

        See :func:`pari` for more examples.
        """
        return objtogen(s)

    cpdef Gen zero(self):
        """
        EXAMPLES::

            sage: pari.zero()
            0

        >>> pari.zero()
        0
        """
        return self.PARI_ZERO

    cpdef Gen one(self):
        """
        EXAMPLES::

            sage: pari.one()
            1
        """
        return self.PARI_ONE

    def new_with_bits_prec(self, s, long precision):
        r"""
        pari.new_with_bits_prec(self, s, precision) creates s as a PARI
        Gen with (at most) precision *bits* of precision.
        """
        cdef unsigned long old_prec
        old_prec = <unsigned long>GP_DATA.fmt.sigd
        precision = prec_bits_to_dec(precision)
        if not precision:
            precision = old_prec
        self.set_real_precision(precision)
        x = self(s)
        self.set_real_precision(old_prec)
        return x

    ############################################################
    # Initialization
    ############################################################

    def stacksize(self):
        r"""
        Return the current size of the PARI stack, which is `10^6`
        by default.  However, the stack size is automatically doubled
        when needed up to some maximum.

        .. SEEALSO::

            - :meth:`stacksizemax` to get the maximum stack size
            - :meth:`allocatemem` to change the current or maximum
              stack size

        EXAMPLES::

            sage: pari.stacksize() # random
            1000000
            sage: pari.allocatemem(2**18, silent=True)
            sage: pari.stacksize()
            262144
        """
        return pari_mainstack.size

    def stacksizemax(self):
        r"""
        Return the maximum size of the PARI stack, which is determined
        at startup in terms of available memory. Usually, the PARI
        stack size is (much) smaller than this maximum but the stack
        will be increased up to this maximum if needed.

        .. SEEALSO::

            - :meth:`stacksize` to get the current stack size
            - :meth:`allocatemem` to change the current or maximum
              stack size

        EXAMPLES::

            sage: pari.allocatemem(2**18, 2**26, silent=True)
            sage: pari.stacksizemax()
            67108864
        """
        return pari_mainstack.vsize

    def allocatemem(self, size_t s=0, size_t sizemax=0, *, silent=False):
        r"""
        Change the PARI stack space to the given size ``s`` (or double
        the current size if ``s`` is `0`) and change the maximum stack
        size to ``sizemax``.

        PARI tries to use only its current stack (the size which is set
        by ``s``), but it will increase its stack if needed up to the
        maximum size which is set by ``sizemax``.

        The PARI stack is never automatically shrunk.  You can use the
        command ``pari.allocatemem(10**6)`` to reset the size to `10^6`,
        which is the default size at startup.  Note that the results of
        computations using Sage's PARI interface are copied to the
        Python heap, so they take up no space in the PARI stack.
        The PARI stack is cleared after every computation.

        It does no real harm to set this to a small value as the PARI
        stack will be automatically doubled when we run out of memory.

        INPUT:

        - ``s`` - an integer (default: 0).  A non-zero argument is the
          size in bytes of the new PARI stack.  If `s` is zero, double
          the current stack size.

        - ``sizemax`` - an integer (default: 0).  A non-zero argument
          is the maximum size in bytes of the PARI stack.  If
          ``sizemax`` is 0, the maximum of the current maximum and
          ``s`` is taken.

        EXAMPLES::

            sage: pari.allocatemem(10**7)
            PARI stack size set to 10000000 bytes, maximum size set to ...
            sage: pari.allocatemem()  # Double the current size
            PARI stack size set to 20000000 bytes, maximum size set to ...
            sage: pari.stacksize()
            20000000
            sage: pari.allocatemem(10**6)
            PARI stack size set to 1000000 bytes, maximum size set to ...

        The following computation will automatically increase the PARI
        stack size::

            sage: a = pari('2^100000000')

        ``a`` is now a Python variable on the Python heap and does not
        take up any space on the PARI stack.  The PARI stack is still
        large because of the computation of ``a``::

            sage: pari.stacksize()  # random
            12500264

        Setting a small maximum size makes this fail::

            sage: pari.allocatemem(10**6, 2**22)
            PARI stack size set to 1000000 bytes, maximum size set to ...
            sage: a = pari('2^100000000')
            Traceback (most recent call last):
            ...
            PariError: _^s: the PARI stack overflows (current size: 1000000; maximum size: 4194304)
            You can use pari.allocatemem() to change the stack size and try again

        TESTS:

        Do the same without using the string interface and starting
        from a very small stack size::

            sage: pari.allocatemem(1, 2**26)
            PARI stack size set to 1024 bytes, maximum size set to ...
            sage: a = pari(2)**100000000
            sage: pari.stacksize()  # random
            12500024

        We do not allow ``sizemax`` less than ``s``::

            sage: pari.allocatemem(10**7, 10**6)
            Traceback (most recent call last):
            ...
            ValueError: the maximum size (10000000) should be at least the stack size (1000000)
        """
        if s == 0:
            s = pari_mainstack.size * 2
            if s < pari_mainstack.size:
                raise OverflowError("cannot double stack size")
        elif s < 1024:
            s = 1024  # arbitrary minimum size
        if sizemax == 0:
            # For the default sizemax, use the maximum of current
            # sizemax and the given size s.
            if pari_mainstack.vsize > s:
                sizemax = pari_mainstack.vsize
            else:
                sizemax = s
        elif sizemax < s:
            raise ValueError("the maximum size ({}) should be at least the stack size ({})".format(s, sizemax))
        sig_on()
        paristack_setsize(s, sizemax)
        sig_off()
        if not silent:
            print("PARI stack size set to {} bytes, maximum size set to {}".
                format(self.stacksize(), self.stacksizemax()))

    def pari_version(self):
        return str(PARIVERSION)

    def init_primes(self, unsigned long M):
        """
        Recompute the primes table including at least all primes up to M
        (but possibly more).

        EXAMPLES::

            sage: pari.init_primes(200000)

        We make sure that ticket :trac:`11741` has been fixed::

            sage: pari.init_primes(2**30)
            Traceback (most recent call last):
            ...
            ValueError: Cannot compute primes beyond 436273290
        """
        # Hardcoded bound in PARI sources
        if M > 436273290:
            raise ValueError("Cannot compute primes beyond 436273290")

        if M <= maxprime():
            return
        sig_on()
        initprimetable(M)
        sig_off()

    def primes(self, n=None, end=None):
        """
        Return a pari vector containing the first `n` primes, the primes
        in the interval `[n, end]`, or the primes up to `end`.

        INPUT:

        Either

        - ``n`` -- integer

        or

        - ``n`` -- list or tuple `[a, b]` defining an interval of primes

        or

        - ``n, end`` -- start and end point of an interval of primes

        or

        - ``end`` -- end point for the list of primes

        OUTPUT: a PARI list of prime numbers

        EXAMPLES::

            sage: pari.primes(3)
            [2, 3, 5]
            sage: pari.primes(10)
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            sage: pari.primes(20)
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]
            sage: len(pari.primes(1000))
            1000
            sage: pari.primes(11,29)
            [11, 13, 17, 19, 23, 29]
            sage: pari.primes((11,29))
            [11, 13, 17, 19, 23, 29]
            sage: pari.primes(end=29)
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            sage: pari.primes(10**30, 10**30 + 100)
            [1000000000000000000000000000057, 1000000000000000000000000000099]

        TESTS::

            sage: pari.primes(0)
            []
            sage: pari.primes(-1)
            []
            sage: pari.primes(end=1)
            []
            sage: pari.primes(end=-1)
            []
            sage: pari.primes(3,2)
            []
        """
        cdef Gen t0, t1
        if end is None:
            t0 = objtogen(n)
            sig_on()
            return new_gen(primes0(t0.g))
        elif n is None:
            t0 = self.PARI_TWO  # First prime
        else:
            t0 = objtogen(n)
        t1 = objtogen(end)
        sig_on()
        return new_gen(primes_interval(t0.g, t1.g))

    def primes_up_to_n(self, n):
        deprecation(20216, "pari.primes_up_to_n(n) is deprecated, use pari.primes(end=n) instead")
        return self.primes(end=n)

    prime_list = deprecated_function_alias(20216, primes)

    nth_prime = deprecated_function_alias(20216, Pari_auto.prime)

    euler = Pari_auto.Euler
    pi = Pari_auto.Pi

    def polchebyshev(self, long n, v=None):
        """
        Chebyshev polynomial of the first kind of degree `n`,
        in the variable `v`.

        EXAMPLES::

            sage: pari.polchebyshev(7)
            64*x^7 - 112*x^5 + 56*x^3 - 7*x
            sage: pari.polchebyshev(7, 'z')
            64*z^7 - 112*z^5 + 56*z^3 - 7*z
            sage: pari.polchebyshev(0)
            1

        >>> pari.polchebyshev(7)
        64*x^7 - 112*x^5 + 56*x^3 - 7*x
        >>> pari.polchebyshev(7, 'z')
        64*z^7 - 112*z^5 + 56*z^3 - 7*z
        >>> pari.polchebyshev(0)
        1
        """
        sig_on()
        return new_gen(polchebyshev1(n, get_var(v)))

    # Deprecated by upstream PARI: do not remove this deprecated alias
    # as long as it exists in PARI.
    poltchebi = deprecated_function_alias(18203, polchebyshev)

    def factorial(self, long n):
        """
        Return the factorial of the integer n as a PARI Gen.

        EXAMPLES::

            sage: pari.factorial(0)
            1
            sage: pari.factorial(1)
            1
            sage: pari.factorial(5)
            120
            sage: pari.factorial(25)
            15511210043330985984000000

        >>> pari.factorial(0)
        1
        >>> pari.factorial(1)
        1
        >>> pari.factorial(5)
        120
        >>> pari.factorial(25)
        15511210043330985984000000
        """
        sig_on()
        return new_gen(mpfact(n))

    def polsubcyclo(self, long n, long d, v=None):
        """
        polsubcyclo(n, d, v=x): return the pari list of polynomial(s)
        defining the sub-abelian extensions of degree `d` of the
        cyclotomic field `\QQ(\zeta_n)`, where `d`
        divides `\phi(n)`.

        EXAMPLES::

            sage: pari.polsubcyclo(8, 4)
            [x^4 + 1]
            sage: pari.polsubcyclo(8, 2, 'z')
            [z^2 + 2, z^2 - 2, z^2 + 1]
            sage: pari.polsubcyclo(8, 1)
            [x - 1]
            sage: pari.polsubcyclo(8, 3)
            []

        >>> pari.polsubcyclo(8, 4)
        [x^4 + 1]
        >>> pari.polsubcyclo(8, 2, 'z')
        [z^2 + 2, z^2 - 2, z^2 + 1]
        >>> pari.polsubcyclo(8, 1)
        [x - 1]
        >>> pari.polsubcyclo(8, 3)
        []
        """
        cdef Gen plist
        sig_on()
        plist = new_gen(polsubcyclo(n, d, get_var(v)))
        if typ(plist.g) != t_VEC:
            return self.vector(1, [plist])
        else:
            return plist

    polcyclo_eval = deprecated_function_alias(20217, Pari_auto.polcyclo)

    def setrand(self, seed):
        """
        Sets PARI's current random number seed.

        INPUT:

        - ``seed`` -- either a strictly positive integer or a GEN of
          type ``t_VECSMALL`` as output by ``getrand()``

        This should not be called directly; instead, use Sage's global
        random number seed handling in ``sage.misc.randstate``
        and call ``current_randstate().set_seed_pari()``.

        EXAMPLES::

            sage: pari.setrand(50)
            sage: a = pari.getrand()
            sage: pari.setrand(a)
            sage: a == pari.getrand()
            True

        TESTS:

        Check that invalid inputs are handled properly (:trac:`11825`)::

            sage: pari.setrand("foobar")
            Traceback (most recent call last):
            ...
            PariError: incorrect type in setrand (t_POL)
        """
        cdef Gen t0 = self(seed)
        sig_on()
        setrand(t0.g)
        sig_off()

    def vector(self, long n, entries=None):
        """
        vector(long n, entries=None): Create and return the length n PARI
        vector with given list of entries.

        EXAMPLES::

            sage: pari.vector(5, [1, 2, 5, 4, 3])
            [1, 2, 5, 4, 3]
            sage: pari.vector(2, ['x', 1])
            [x, 1]
            sage: pari.vector(2, ['x', 1, 5])
            Traceback (most recent call last):
            ...
            IndexError: length of entries (=3) must equal n (=2)
        """
        cdef Gen v = self._empty_vector(n)
        if entries is not None:
            if len(entries) != n:
                raise IndexError("length of entries (=%s) must equal n (=%s)"%\
                      (len(entries), n))
            for i, x in enumerate(entries):
                v[i] = x
        return v

    cdef Gen _empty_vector(self, long n):
        cdef Gen v
        sig_on()
        v = new_gen(zerovec(n))
        return v

    def matrix(self, long m, long n, entries=None):
        """
        matrix(long m, long n, entries=None): Create and return the m x n
        PARI matrix with given list of entries.
        """
        cdef long i, j, k
        cdef Gen A
        cdef Gen x

        sig_on()
        A = new_gen(zeromatcopy(m,n))
        if entries is not None:
            if len(entries) != m*n:
                raise IndexError("len of entries (=%s) must be %s*%s=%s"%(len(entries),m,n,m*n))
            k = 0
            A.refers_to = {}
            for i from 0 <= i < m:
                for j from 0 <= j < n:
                    x = self(entries[k])
                    A.refers_to[(i,j)] = x
                    (<GEN>(A.g)[j+1])[i+1] = <pari_longword>(x.g)
                    k = k + 1
        return A

    def genus2red(self, P, P0=None):
        """
        Let `P` be a polynomial with integer coefficients.
        Determines the reduction of the (proper, smooth) genus 2
        curve `C/\QQ`, defined by the hyperelliptic equation `y^2 = P`.
        The special syntax ``genus2red([P,Q])`` is also allowed, where
        the polynomials `P` and `Q` have integer coefficients, to
        represent the model `y^2 + Q(x)y = P(x)`.

        EXAMPLES::

            sage: x = pari('x')
            sage: pari.genus2red([-5*x**5, x**3 - 2*x**2 - 2*x + 1])
            [1416875, [2, -1; 5, 4; 2267, 1], x^6 - 240*x^4 - 2550*x^3 - 11400*x^2 - 24100*x - 19855, [[2, [2, [Mod(1, 2)]], []], [5, [1, []], ["[V] page 156", [3]]], [2267, [2, [Mod(432, 2267)]], ["[I{1-0-0}] page 170", []]]]]
        """
        cdef Gen t0 = objtogen(P)
        sig_on()
        return new_gen(genus2red(t0.g, NULL))

    def List(self, x=None):
        """
        Create an empty list or convert `x` to a list.

        EXAMPLES::

            sage: pari.List(range(5))
            List([0, 1, 2, 3, 4])
            sage: L = pari.List()
            sage: L
            List([])
            sage: L.listput(42, 1)
            42
            sage: L
            List([42])
            sage: L.listinsert(24, 1)
            24
            sage: L
            List([24, 42])
        """
        if x is None:
            sig_on()
            return new_gen(listcreate())
        cdef Gen t0 = objtogen(x)
        sig_on()
        return new_gen(gtolist(t0.g))

IF SAGE:
    cdef inline void INT_to_mpz(mpz_ptr value, GEN g):
        """
        Store a PARI ``t_INT`` as an ``mpz_t``.
        """
        if typ(g) != t_INT:
            pari_err(e_TYPE, <char*>"conversion to mpz", g)

        cdef long size = lgefint(g) - 2
        mpz_import(value, size, -1, sizeof(long), 0, 0, int_LSW(g))

        if signe(g) < 0:
            mpz_neg(value, value)

    cdef void INTFRAC_to_mpq(mpq_ptr value, GEN g):
        """
        Store a PARI ``t_INT`` or ``t_FRAC`` as an ``mpq_t``.
        """
        if typ(g) == t_FRAC:
            INT_to_mpz(mpq_numref(value), gel(g, 1))
            INT_to_mpz(mpq_denref(value), gel(g, 2))
        elif typ(g) == t_INT:
            INT_to_mpz(mpq_numref(value), g)
            mpz_set_ui(mpq_denref(value), 1)
        else:
            pari_err(e_TYPE, <char*>"conversion to mpq", g)

cdef long get_var(v) except -2:
    """
    Convert ``v`` into a PARI variable number.

    If ``v`` is a PARI object, return the variable number of
    ``variable(v)``. If ``v`` is ``None`` or ``-1``, return -1.
    Otherwise, treat ``v`` as a string and return the number of
    the variable named ``v``.

    OUTPUT: a PARI variable number (varn) or -1 if there is no
    variable number.

    .. WARNING::

        You can easily create variables with garbage names using
        this function. This can actually be used as a feature, if
        you want variable names which cannot be confused with
        ordinary user variables.

    EXAMPLES:

    We test this function using ``Pol()`` which calls this function::

        sage: pari("[1,0]").Pol()
        x
        sage: pari("[2,0]").Pol('x')
        2*x
        sage: pari("[Pi,0]").Pol('!@#$%^&')
        3.14159265358979*!@#$%^&

    We can use ``varhigher()`` and ``varlower()`` to create
    temporary variables without a name. The ``"xx"`` below is just a
    string to display the variable, it doesn't create a variable
    ``"xx"``::

        sage: xx = pari.varhigher("xx")
        sage: pari("[x,0]").Pol(xx)
        x*xx

    Indeed, this is not the same as::

        sage: pari("[x,0]").Pol("xx")
        Traceback (most recent call last):
        ...
        PariError: incorrect priority in gtopoly: variable x <= xx
    """
    if v is None:
        return -1
    cdef long varno
    if isinstance(v, Gen):
        sig_on()
        varno = <long>gvar((<Gen>v).g)
        sig_off()
        if varno < 0:
            return -1
        else:
            return varno
    if v == -1:
        return -1
    sig_on()
    varno = <long>fetch_user_var(v.encode('ascii'))
    sig_off()
    return varno
