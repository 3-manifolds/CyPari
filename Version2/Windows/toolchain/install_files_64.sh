#!/bin/bash
GCCVERSION="6.3.0"
TOOLCHAIN="/c/mingw-w64/x86_64-6.3.0-posix-dwarf-rt_v5-rev2/mingw64"
LIBDIR_MINGW64="${TOOLCHAIN}/lib/"
SPECSDIR_MINGW64="${TOOLCHAIN}/lib/gcc/x86_64-w64-mingw64/${GCCVERSION}/"
cp mingw64/x86_64-w64-mingw32/lib/* ${LIBDIR_MINGW64}
cp specs90_64 ${SPECSDIR_MINGW64}/specs90
cp specs100_64 ${SPECSDIR_MINGW64}/specs100
