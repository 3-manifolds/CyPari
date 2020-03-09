"""
Tests specific to Python 3:

    >>> old_prec = pari.set_real_precision(63)
    >>> int(pari('2^63-1'))
    9223372036854775807
    >>> int(pari('2^63+2'))
    9223372036854775810
    >>> pari.set_real_precision(old_prec)
    63
    >>> print(hex(pari(0)))
    0x0
    >>> print(hex(pari(15)))
    0xf
    >>> print(hex(pari(16)))
    0x10
    >>> print(hex(pari(16938402384092843092843098243)))
    0x36bb1e3929d1a8fe2802f083
    >>> print(hex(pari(-16938402384092843092843098243)))
    -0x36bb1e3929d1a8fe2802f083
"""
