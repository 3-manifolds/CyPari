#!/bin/bash
GCCVERSION="6.3.0"
TOOLCHAIN="/c/mingw-w64/i686-6.3.0-posix-dwarf-rt_v5-rev2/mingw32"
LIBDIR_MINGW32="${TOOLCHAIN}/lib/"
SPECSDIR_MINGW32="${TOOLCHAIN}/lib/gcc/i686-w64-mingw32/${GCCVERSION}/"
cp mingw32/i686-w64-mingw32/lib/* ${LIBDIR_MINGW32}
cp specs90_32 ${SPECSDIR_MINGW32}/specs90
cp specs100_32 ${SPECSDIR_MINGW32}/specs100

