from __future__ import print_function
import os, sys, doctest
import cypari
cypari.gen.pari.shut_up()
doctest.testmod(cypari.gen, optionflags=doctest.ELLIPSIS|doctest.IGNORE_EXCEPTION_DETAIL)
print('Expected failures are those with both 32-bit and 64-bit results.')
print('WARNING: exception details are being ignored.')
print('(Python 3 uses qualified exception names, but Python 2 does not.')
