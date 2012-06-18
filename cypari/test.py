import os, sys, doctest
import cypari
cypari.gen.pari.shut_up()
doctest.testmod(cypari.gen, optionflags=doctest.ELLIPSIS)
