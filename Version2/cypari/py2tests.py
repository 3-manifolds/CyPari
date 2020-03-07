"""
Tests specific to Python 2:

    >>> old_prec = pari.set_real_precision(63)
    >>> int(pari('2^63-1'))
    9223372036854775807L  # 32-bit
    9223372036854775807   # 64-bit
    >>> int(pari('2^63+2')))
    9223372036854775810L
    >>> pari.set_real_precision(old_prec)
    >>> print(hex(pari(0)))
    0
    >>> print(hex(pari(15)))
    f
    >>> print(hex(pari(16)))
    10
    >>> print(hex(pari(16938402384092843092843098243)))
    36bb1e3929d1a8fe2802f083
    >>> print(hex(pari(-16938402384092843092843098243)))
    -36bb1e3929d1a8fe2802f083
"""
