#! /bin/bash
#
# This builds a fat (i386/x86_64) PARI library for OS X > 10.5 or a 
# normal binary for Linux or Windows. 
#

set -e
if [ ! -d "build" ] ; then
    mkdir build
fi
PREFIX=`pwd`/build/pari
echo "Untarring Pari..."
cd build
tar xzf ../pari-2.8.tgz
cd pari_src

echo "Building Pari libary..." 
if [ "$(uname)" = "Darwin" ] ; then  # OS X
    export CFLAGS='-arch x86_64'
    ./Configure --prefix=${PREFIX} --without-gmp --host=x86_64-darwin
    cd Odarwin-x86_64
    make install
    cd ../..
    cp pari_src/src/language/anal.h pari/include/pari
    cd ../cypari
    if [ ! -e "libpari-2.8.dylib" ] ; then
	ln -s ../build/pari/lib/libpari-2.8.dylib
    fi

elif [ "$(uname)" = *MINGW32* ] ; then # MinGW on Windows
    ./Configure --prefix=${PREFIX} --libdir=lib --without-gmp --host=i386-mingw
    cd Omingw-i386
    make install
    make install-lib-sta
else  # Linux
    ./Configure --prefix=${PREFIX} --without-gmp
    cd Olinux-*
    make install
    make install-lib-sta
    cd ../..
    cp pari_src/src/language/anal.h pari/include/pari
    cd ../cypari
    if [ ! -e "libpari-2.8.so.0" ] ; then
	ln -s ../build/pari/lib/libpari-2.8.so.0 .
    fi
fi
