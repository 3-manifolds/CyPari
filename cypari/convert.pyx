# cython: cdivision = True
"""
Convert PARI objects to/from Python/C native types
**************************************************

This modules contains the following conversion routines:

- integers, long integers <-> PARI integers
- list of integers -> PARI polynomials
- doubles -> PARI reals
- pairs of doubles -> PARI complex numbers

PARI integers are stored as an array of limbs of type ``pari_ulong``
(which are 32-bit or 64-bit integers). Depending on the kernel
(GMP or native), this array is stored little-endian or big-endian.
This is encapsulated in macros like ``int_W()``:
see section 4.5.1 of the
`PARI library manual <http://pari.math.u-bordeaux.fr/pub/pari/manuals/2.7.0/libpari.pdf>`_.

Python integers of type ``int`` are just C longs. Python integers of
type ``long`` are stored as a little-endian array of type ``digit``
with 15 or 30 bits used per digit. The internal format of a ``long`` is
not documented, but there is some information in
`longintrepr.h <https://github.com/python-git/python/blob/master/Include/longintrepr.h>`_.

Because of this difference in bit lengths, converting integers involves
some bit shuffling.
"""

#*****************************************************************************
#       Copyright (C) 2016 Jeroen Demeyer <jdemeyer@cage.ugent.be>
#       Copyright (C) 2016 Luca De Feo <luca.defeo@polytechnique.edu>
#       Copyright (C) 2016 Vincent Delecroix <vincent.delecroix@u-bordeaux.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

cdef extern from *:
    ctypedef struct PyLongObject:
        digit* ob_digit

cdef extern from "Py_SET_SIZE.h":
    void Py_SET_SIZE(py_long o, Py_ssize_t size)

########################################################################
# Conversion C -> PARI
########################################################################

cdef inline GEN double_to_REAL(double x):
    # PARI has an odd concept where it attempts to track the accuracy
    # of floating-point 0; a floating-point zero might be 0.0e-20
    # (meaning roughly that it might represent any number in the
    # range -1e-20 <= x <= 1e20).

    # PARI's dbltor converts a floating-point 0 into the PARI real
    # 0.0e-307; PARI treats this as an extremely precise 0.  This
    # can cause problems; for instance, the PARI incgam() function can
    # be very slow if the first argument is very precise.

    # So we translate 0 into a floating-point 0 with 53 bits
    # of precision (that's the number of mantissa bits in an IEEE
    # double).
    if x == 0:
        return real_0_bit(-53)
    else:
        return dbltor(x)

cdef inline GEN doubles_to_COMPLEX(double re, double im):
    cdef GEN g = cgetg(3, t_COMPLEX)
    if re == 0:
        set_gel(g, 1, gen_0)
    else:
        set_gel(g, 1, dbltor(re))
    if im == 0:
        set_gel(g, 2, gen_0)
    else:
        set_gel(g, 2, dbltor(im))
    return g

########################################################################
# Conversion Python -> PARI
########################################################################

cdef inline GEN PyInt_AS_GEN(x):
    return stoi(PyInt_AS_LONG(x))

cdef inline GEN PyFloat_AS_GEN(x):
    return double_to_REAL(PyFloat_AS_DOUBLE(x))

cdef inline GEN PyComplex_AS_GEN(x):
    return doubles_to_COMPLEX(
        PyComplex_RealAsDouble(x), PyComplex_ImagAsDouble(x))

########################################################################
# Conversion PARI -> Python
########################################################################

cpdef gen_to_python(Gen z):
    r"""
    Convert the PARI element ``z`` to a Python object.

    OUTPUT:

    - a Python integer for integers (type ``t_INT``)

    - a ``Fraction`` (``fractions`` module) for rationals (type ``t_FRAC``)

    - a ``float`` for real numbers (type ``t_REAL``)

    - a ``complex`` for complex numbers (type ``t_COMPLEX``)

    - a ``list`` for vectors (type ``t_VEC`` or ``t_COL``). The function
      ``gen_to_python`` is then recursively applied on the entries.

    - a ``list`` of Python integers for small vectors (type ``t_VECSMALL``)

    - a ``list`` of ``list``s for matrices (type ``t_MAT``). The function
      ``gen_to_python`` is then recursively applied on the entries.

    - the floating point ``inf`` or ``-inf`` for infinities (type ``t_INFINITY``)

    - a string for strings (type ``t_STR``)

    - other PARI types are not supported and the function will raise a
      ``NotImplementedError``

    Examples:

    >>> from cypari import pari
    >>> from cypari import gen_to_python

    Converting integers:

    >>> z = pari('42'); z
    42
    >>> a = gen_to_python(z); a
    42
    >>> type(a)
    <... 'int'>

    >>> gen_to_python(pari('3^50')) == 3**50
    True
    >>> type(gen_to_python(pari('3^50'))) == type(3**50)
    True

    Converting rational numbers:

    >>> z = pari('2/3'); z
    2/3
    >>> a = gen_to_python(z); a
    Fraction(2, 3)
    >>> type(a)
    <class 'fractions.Fraction'>

    Converting real numbers (and infinities):

    >>> z = pari('1.2'); z
    1.20000000000000
    >>> a = gen_to_python(z); a
    1.2
    >>> type(a)
    <... 'float'>

    >>> z = pari('oo'); z
    +oo
    >>> a = gen_to_python(z); a
    inf
    >>> type(a)
    <... 'float'>

    >>> z = pari('-oo'); z
    -oo
    >>> a = gen_to_python(z); a
    -inf
    >>> type(a)
    <... 'float'>

    Converting complex numbers:

    >>> z = pari('1 + I'); z
    1 + I
    >>> a = gen_to_python(z); a
    (1+1j)
    >>> type(a)
    <... 'complex'>

    >>> z = pari('2.1 + 3.03*I'); z
    2.10000000000000 + 3.03000000000000*I
    >>> a = gen_to_python(z); a
    (2.1+3.03j)

    Converting vectors:

    >>> z1 = pari('Vecsmall([1,2,3])'); z1
    Vecsmall([1, 2, 3])
    >>> z2 = pari('[1, 3.4, [-5, 2], oo]'); z2
    [1, 3.40000000000000, [-5, 2], +oo]
    >>> z3 = pari('[1, 5.2]~'); z3
    [1, 5.20000000000000]~
    >>> z1.type(), z2.type(), z3.type()
    ('t_VECSMALL', 't_VEC', 't_COL')

    >>> a1 = gen_to_python(z1); a1
    [1, 2, 3]
    >>> type(a1)
    <... 'list'>
    >>> [type(x) for x in a1]
    [<... 'int'>, <... 'int'>, <... 'int'>]

    >>> a2 = gen_to_python(z2); a2
    [1, 3.4, [-5, 2], inf]
    >>> type(a2)
    <... 'list'>
    >>> [type(x) for x in a2]
    [<... 'int'>, <... 'float'>, <... 'list'>, <... 'float'>]

    >>> a3 = gen_to_python(z3); a3
    [1, 5.2]
    >>> type(a3)
    <... 'list'>
    >>> [type(x) for x in a3]
    [<... 'int'>, <... 'float'>]

    Converting matrices:

    >>> z = pari('[1,2;3,4]')
    >>> gen_to_python(z)
    [[1, 2], [3, 4]]

    >>> z = pari('[[1, 3], [[2]]; 3, [4, [5, 6]]]')
    >>> gen_to_python(z)
    [[[1, 3], [[2]]], [3, [4, [5, 6]]]]

    Converting strings:

    >>> z = pari('"Hello"')
    >>> a = gen_to_python(z); a
    'Hello'
    >>> type(a)
    <... 'str'>

    Some currently unsupported types:

    >>> z = pari('x')
    >>> z.type()
    't_POL'
    >>> gen_to_python(z)
    Traceback (most recent call last):
    ...
    NotImplementedError: conversion not implemented for t_POL

    >>> z = pari('12 + O(2^13)')
    >>> z.type()
    't_PADIC'
    >>> gen_to_python(z)
    Traceback (most recent call last):
    ...
    NotImplementedError: conversion not implemented for t_PADIC
    """
    return PyObject_FromGEN(z.g)


cpdef gen_to_integer(Gen x):
    """
    Convert a PARI ``gen`` to a Python ``int`` or ``long``.

    INPUT:

    - ``x`` -- a PARI ``t_INT``, ``t_FRAC``, ``t_REAL``, a purely
      real ``t_COMPLEX``, a ``t_INTMOD`` or ``t_PADIC`` (which are
      lifted).

    Examples:

    >>> from cypari import gen_to_integer
    >>> from cypari import pari
    >>> a = gen_to_integer(pari("12345")); a; type(a)
    12345
    <... 'int'>
    >>> gen_to_integer(pari("10^30")) == 10**30
    True
    >>> gen_to_integer(pari("19/5"))
    3
    >>> gen_to_integer(pari("1 + 0.0*I"))
    1
    >>> gen_to_integer(pari("3/2 + 0.0*I"))
    1
    >>> gen_to_integer(pari("Mod(-1, 11)"))
    10
    >>> gen_to_integer(pari("5 + O(5^10)"))
    5
    >>> gen_to_integer(pari("Pol(42)"))
    42
    >>> gen_to_integer(pari("u"))
    Traceback (most recent call last):
    ...
    TypeError: unable to convert PARI object u of type t_POL to an integer
    >>> s = pari("x + O(x^2)")
    >>> s
    x + O(x^2)
    >>> gen_to_integer(s)
    Traceback (most recent call last):
    ...
    TypeError: unable to convert PARI object x + O(x^2) of type t_SER to an integer
    >>> gen_to_integer(pari("1 + I"))
    Traceback (most recent call last):
    ...
    TypeError: unable to convert PARI object 1 + I of type t_COMPLEX to an integer

    Tests:

    >>> gen_to_integer(pari("1.0 - 2^64")) == -18446744073709551615
    True
    >>> gen_to_integer(pari("1 - 2^64")) == -18446744073709551615
    True
    >>> pari.allocatemem(64000000, 64000000)
    PARI stack size set to ...
    >>> for i in range(10000):
    ...     x = 3**i
    ...     if int(pari(x)) != int(x) or int(pari(x)) != x:
    ...         print(x)

    Check some corner cases:

    >>> for s in [1, -1]:
    ...     for a in [1, 2**31, 2**32, 2**63, 2**64]:
    ...         for b in [-1, 0, 1]:
    ...             Nstr = str(s * (a + b))
    ...             N1 = gen_to_integer(pari(Nstr))  # Convert via PARI
    ...             N2 = int(Nstr)                   # Convert via Python
    ...             if N1 != N2:
    ...                 print(Nstr, N1, N2)
    ...             if type(N1) is not type(N2):
    ...                 print(N1, type(N1), N2, type(N2))
    """
    return PyInt_FromGEN(x.g)


cdef PyObject_FromGEN(GEN g):
    cdef long t = typ(g)
    cdef Py_ssize_t i, j
    cdef Py_ssize_t lr, lc

    if t == t_INT:
        return PyInt_FromGEN(g)
    elif t == t_FRAC:
        from fractions import Fraction
        num = PyInt_FromGEN(gel(g, 1))
        den = PyInt_FromGEN(gel(g, 2))
        return Fraction(num, den)
    elif t == t_REAL:
        return rtodbl(g)
    elif t == t_COMPLEX:
        re = PyObject_FromGEN(gel(g, 1))
        im = PyObject_FromGEN(gel(g, 2))
        return complex(re, im)
    elif t == t_VEC or t == t_COL:
        return [PyObject_FromGEN(gel(g, i)) for i in range(1, lg(g))]
    elif t == t_VECSMALL:
        return [g[i] for i in range(1, lg(g))]
    elif t == t_MAT:
        lc = lg(g)
        if lc <= 1:
            return [[]]
        lr = lg(gel(g,1))
        return [[PyObject_FromGEN(gcoeff(g, i, j)) for j in range(1, lc)] for i in range(1, lr)]
    elif t == t_INFINITY:
        if inf_get_sign(g) >= 0:
            return INFINITY
        else:
            return -INFINITY
    elif t == t_STR:
        return to_string(GSTR(g))
    else:
        tname = to_string(type_name(t))
        raise NotImplementedError(f"conversion not implemented for {tname}")


cdef PyInt_FromGEN(GEN g):
    # First convert the input to a t_INT
    try:
        g = gtoi(g)
    finally:
        # Reset avma now. This is OK as long as we are not calling further
        # PARI functions before this function returns.
        reset_avma()

    if not signe(g):
        return PyInt_FromLong(0)

    cdef ulong u
    res = PyLong_FromINT(g)
    return res


cdef GEN gtoi(GEN g0) except NULL:
    """
    Convert a PARI object to a PARI integer.

    This function is shallow and not stack-clean.
    """
    if typ(g0) == t_INT:
        return g0
    cdef GEN g
    try:
        sig_on()
        g = simplify_shallow(g0)
        if typ(g) == t_COMPLEX:
            if gequal0(gel(g,2)):
                g = gel(g,1)
        if typ(g) == t_INTMOD:
            g = gel(g,2)
        g = trunc_safe(g)
        if typ(g) != t_INT:
            sig_error()
        sig_off()
    except RuntimeError:
        s = to_string(stack_sprintf(
            "unable to convert PARI object %Ps of type %s to an integer",
            g0, type_name(typ(g0))))
        raise TypeError(s)
    return g


cdef PyLong_FromINT(GEN g):
    # Size of input in words, bits and Python digits. The size in
    # digits might be a small over-estimation, but that is not a
    # problem.
    cdef size_t sizewords = (lgefint(g) - 2)
    cdef size_t sizebits = sizewords * pari_BITS_IN_LONG
    cdef size_t sizedigits = (sizebits + pari_PyLong_SHIFT - 1) // pari_PyLong_SHIFT

    # Actual correct computed size
    cdef Py_ssize_t sizedigits_final = 0

    cdef py_long x = _PyLong_New(sizedigits)
    cdef digit* D = x.ob_digit

    cdef digit d
    cdef ulong w
    cdef size_t i, j, bit
    for i in range(sizedigits):
        # The least significant bit of digit number i of the output
        # integer is bit number "bit" of word "j".
        bit = i * pari_PyLong_SHIFT
        j = bit // pari_BITS_IN_LONG
        bit = bit % pari_BITS_IN_LONG

        w = int_W(g, j)[0]
        d = w >> bit

        # Do we need bits from the next word too?
        if pari_BITS_IN_LONG - bit < pari_PyLong_SHIFT and j+1 < sizewords:
            w = int_W(g, j+1)[0]
            d += w << (pari_BITS_IN_LONG - bit)

        d = d & pari_PyLong_MASK
        D[i] = d

        # Keep track of last non-zero digit
        if d:
            sizedigits_final = i+1

    # Set correct size
    if signe(g) > 0:
        Py_SET_SIZE(x, sizedigits_final)
    else:
        Py_SET_SIZE(x, -sizedigits_final)

    return x


########################################################################
# Conversion Python -> PARI
########################################################################

cdef GEN PyLong_AS_GEN(py_long x):
    cdef const digit* D = x.ob_digit

    # Size of the input
    cdef size_t sizedigits
    cdef long sgn
    if Py_SIZE(x) == 0:
        return gen_0
    elif Py_SIZE(x) > 0:
        sizedigits = Py_SIZE(x)
        sgn = evalsigne(1)
    else:
        sizedigits = -Py_SIZE(x)
        sgn = evalsigne(-1)

    # Size of the output, in bits and in words
    cdef size_t sizebits = sizedigits * pari_PyLong_SHIFT
    cdef size_t sizewords = (sizebits + pari_BITS_IN_LONG - 1) // pari_BITS_IN_LONG

    # Compute the most significant word of the output.
    # This is a special case because we need to be careful not to
    # overflow the ob_digit array. We also need to check for zero,
    # in which case we need to decrease sizewords.
    # See the loop below for an explanation of this code.
    cdef size_t bit = (sizewords - 1) * pari_BITS_IN_LONG
    cdef size_t dgt = bit // pari_PyLong_SHIFT
    bit = bit % pari_PyLong_SHIFT

    cdef ulong w = <ulong>(D[dgt]) >> bit
    if 1*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG and dgt+1 < sizedigits:
        w += <ulong>(D[dgt+1]) << (1*pari_PyLong_SHIFT - bit)
    if 2*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG and dgt+2 < sizedigits:
        w += <ulong>(D[dgt+2]) << (2*pari_PyLong_SHIFT - bit)
    if 3*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG and dgt+3 < sizedigits:
        w += <ulong>(D[dgt+3]) << (3*pari_PyLong_SHIFT - bit)
    if 4*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG and dgt+4 < sizedigits:
        w += <ulong>(D[dgt+4]) << (4*pari_PyLong_SHIFT - bit)
    if 5*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG and dgt+5 < sizedigits:
        w += <ulong>(D[dgt+5]) << (5*pari_PyLong_SHIFT - bit)

    # Effective size in words plus 2 special codewords
    cdef pariwords = sizewords+2 if w else sizewords+1
    cdef GEN g = cgeti(pariwords)
    g[1] = sgn + evallgefint(pariwords)

    if w:
        int_MSW(g)[0] = w

    # Fill all words
    cdef GEN ptr = int_LSW(g)
    cdef size_t i
    for i in range(sizewords - 1):
        # The least significant bit of word number i of the output
        # integer is bit number "bit" of Python digit "dgt".
        bit = i * pari_BITS_IN_LONG
        dgt = bit // pari_PyLong_SHIFT
        bit = bit % pari_PyLong_SHIFT

        # Now construct the output word from the Python digits: we need
        # to check that we shift less than the number of bits in the
        # type. 6 digits are enough assuming that PyLong_SHIFT >= 15 and
        # BITS_IN_LONG <= 76. A clever compiler should optimize away all
        # but one of the "if" statements below.
        w = <ulong>(D[dgt]) >> bit
        if 1*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG:
            w += <ulong>(D[dgt+1]) << (1*pari_PyLong_SHIFT - bit)
        if 2*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG:
            w += <ulong>(D[dgt+2]) << (2*pari_PyLong_SHIFT - bit)
        if 3*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG:
            w += <ulong>(D[dgt+3]) << (3*pari_PyLong_SHIFT - bit)
        if 4*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG:
            w += <ulong>(D[dgt+4]) << (4*pari_PyLong_SHIFT - bit)
        if 5*pari_PyLong_SHIFT - bit < pari_BITS_IN_LONG:
            w += <ulong>(D[dgt+5]) << (5*pari_PyLong_SHIFT - bit)

        ptr[0] = w
        ptr = int_nextW(ptr)

    return g


cdef GEN PyObject_AsGEN(x) except? NULL:
    """
    Convert basic Python types to a PARI GEN.
    """
    cdef GEN g = NULL
    if isinstance(x, unicode):
        x = to_bytes(x)
    if isinstance(x, bytes):
        sig_on()
        g = gp_read_str(<bytes>x)
        sig_off()
    elif isinstance(x, long):
        sig_on()
        g = PyLong_AS_GEN(x)
        sig_off()
    elif isinstance(x, int):
        sig_on()
        g = PyInt_AS_GEN(x)
        sig_off()
    elif isinstance(x, float):
        sig_on()
        g = PyFloat_AS_GEN(x)
        sig_off()
    elif isinstance(x, complex):
        sig_on()
        g = PyComplex_AS_GEN(x)
        sig_off()
    return g


####################################
# Deprecated functions
####################################

def integer_to_gen(x):
    """
    Convert a Python ``int`` or ``long`` to a PARI ``gen`` of type
    ``t_INT``.

    Examples:

    >>> from cypari import integer_to_gen
    >>> a = integer_to_gen(int(12345)); a; type(a)
    12345
    <... 'cypari._pari.Gen'>
    >>> integer_to_gen(float(12345))
    Traceback (most recent call last):
    ...
    TypeError: integer_to_gen() needs an int or long argument, not float
    >>> integer_to_gen(2**100)
    1267650600228229401496703205376

    Tests:

    >>> assert integer_to_gen(int(12345)) == 12345
    >>> pari.allocatemem(64000000, 64000000)
    PARI stack size set to...
    >>> for i in range(10000):
    ...     x = 3**i
    ...     if pari(int(x)) != pari(x) or pari(int(x)) != pari(x):
    ...         print(x)
    """
    if isinstance(x, long):
        sig_on()
        return new_gen(PyLong_AS_GEN(x))
    elif isinstance(x, int):
        sig_on()
        return new_gen(stoi(PyInt_AS_LONG(x)))
    else:
        raise TypeError("integer_to_gen() needs an int or long argument, not {}".format(type(x).__name__))
