CyPari
======

CyPari is a standalone version of Sage's pari module which is largely
consistent with the Sage cypari2 package that it inspired, but which
can be distributed in binary form as a pip wheel and also works on
Windows.  In particular, CyPari uses the automated build scripts
written by Jeroen DeMeyer for cypari2.  Currently it uses Pari 2.11,
which is several releases newer than the PARI used in the original
version of CyPari.  The fact that the build process continues to work
with each new release of PARI is a strong validation of Jeroen's
flexible build scheme.

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
single shared library for the extension module, due to the fact that
Windows does not allow functions in one shared library to access
global data in another shared library.

On linux or macOS the module should build and/or install with the
usual commands::

    python setup.py build
    python setup.py install

To run doctests use::

    python setup.py test

All tests should pass on all platforms.

To clean up the build area (but not remove PARI) use::

    python setup.py clean

Note that the ``future`` module is required for Python 2.
Install if necessary with::

    pip install future

For building on Windows we expect an msys64 system with the
toolchains::

    mingw-w64\i686-6.3.0-posix-dwarf-rt_v5-rev1 (for 32-bit builds)
    mingw-w64\x86_64-8.1.0-posix-seh-rt_v6-rev0 (for 64-bit builds)

These toolchains support Microsoft's Universal C Runtime, which means
that CyPari no longer requires installation of any special C runtime
dll files.  The build process uses the mingw toolchains to build libpari.a
but the Python extension is built with an appropriate version of
MSVC.

It is also possible to build the Windows Python extension entirely
with MinGW for Python versions less than 3.5.  To do this, run::

    setup.py build -cmingw32

Currently we support 32 and 64 bit Python 2.7, 3.6-3.10 on linux,
macOS and Windows.
