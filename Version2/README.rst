CyPari version 2.0

This directory contains a new version of CyPari based on current (7.4
as of January 2017) Sage sources.  In particular, it uses the
automated build scripts written by Jeroen DeMeyer.  It uses Pari 2.9.1,
which is newer than that used in Sage 7.4.  The fact that the build
process worked perfectly with a newer, changed, Pari is a strong
validation of Jeroen's flexible build scheme.

This version of CyPari handles critical signals such as SIGSEGV
when sent from within a sig_on - sig_off block and long computations
in sig_on - sig_off blocks are interruptable with a SIGINT. These
features work on Windows as well as linux and macOS.

CyPari is intended to be easily distributable as a binary, so it
needed to be possible to build a pip wheel for it.  This forced some
changes to the overall design.  First it was necessary to embed the
relevant parts of the cysignals module, since cysignals is not
distributable as a wheel.  Second, we needed to statically link with
the pari library so that we don't depend on or interfere with the
user's Pari installation.  The second requirement made it desirable to
generate a single shared library for the extension module, partly
because Windows does not allow functions in one shared library to
access global data in another shared library.

On linux or macOS the module should build and/or install with the
usual commands:
    python setup.py build
    python setup.py install

To run doctests use:
    python setup.py test
All tests should pass on all platforms.

To clean up the build area (but not remove Pari) use:
    python setup.py clean

Note that the future module is required for Python 2.  (Install with
pip install future).  Also, it is necessary to build for Python 2
before building for Python3.  This is because the scripts in autogen
are not (yet) compatible with Python 3.  Building with Python 2 will
install auto_gen.pxi and auto_instance.pxi which can then be used
to build for Python 3.

For building on Windows we expect you to have a working msys2 system
with a mingw32 toolchain that has been modified as described in the
file Windows/README.Windows.

Currently we support 32 and 64 bit Python 2.7 on linux, macOS and
Windows.  On linux and macOS we support 32 and 64 bit Python 3.5 or
3.6.  On Windows we support 64 bit Python 3.4, due to limitations of
mingw.
