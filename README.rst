CyPari
======

CyPari is a standalone version of Sage's pari module which is largely
consistent with the Sage cypari2 package that it inspired, but which
can be distributed in binary form as a pip wheel and also works on
Windows.  In particular, CyPari uses the automated build scripts
written by Jeroen DeMeyer for cypari2.  Currently it uses Pari 2.15.
The fact that the build process continues to work with each new
release of PARI is a strong validation of Jeroen's flexible build
scheme.

CyPari handles critical signals such as SIGSEGV when sent from within
a sig_on - sig_off block. Long computations in sig_on - sig_off blocks
are interruptable with a SIGINT. This feature work on Windows as
well as linux and macOS.

Because CyPari is intended to be distributed in binary form as a pip
wheel some changes are needed in the overall design compared to that
used in Sage.  First it embeds the relevant parts of the cysignals
module, since cysignals is not distributable as a wheel.  Second, it
is statically linked with the pari library so that it does not depend
on or interfere with the user's PARI installation. Finally, it uses a
single shared library for the extension module.  This avoids sharing
global variables across DLLs and avoids creating modules which are not
useful by themselves.

The module ia built and installed by the following commands::

    python3 setup.py build
    python3 -m pip install .

To run doctests use::

    python setup.py test

All tests should pass on all platforms.

To clean up the build area (but not remove PARI) use::

    python setup.py clean

For building on Windows we expect an msys64 system with the
UCRT64 environment installed.  For building the extension module
we expect Microsoft Visual Studio 2022 with the 10.0.22000.0
SDK installed, as well as the Universal CRT SDK. The build
process uses the mingw UCRT64 toolchain to build libpari.a and
libgmp.a but the Python extension is built with MSVC.

Currently we support 64 bit Python 3.6 - 3.12 on linux, macOS and Windows.
