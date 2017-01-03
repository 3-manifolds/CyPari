#!/bin/bash
GCCVERSION=`gcc -dumpversion`
LIBDIR_MINGW32="/c/msys64/mingw32/i686-w64-mingw32/lib/"
SPECSDIR_MINGW32="/c/msys64/mingw32/lib/gcc/i686-w64-mingw32/${GCCVERSION}/"
cp mingw32/i686-w64-mingw32/lib/* ${LIBDIR_MINGW32}
cp specs90_32 ${SPECSDIR_MINGW32}/specs90
#cp specs100 ${SPECSDIR_MINGW32}/specs100

