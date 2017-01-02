#!/bin/bash
GCCVERSION=`gcc -dumpversion`
LIBDIR_MINGW64="/c/msys64/mingw64/x86_64-w64-mingw32/lib/"
SPECSDIR_MINGW64="/c/msys64/mingw64/lib/gcc/x86_64-w64-mingw32/${GCCVERSION}/"
cp mingw64/x86_64-w64-mingw32/lib/* ${LIBDIR_MINGW64}
cp specs90 specs100 ${SPECSDIR_MINGW64}