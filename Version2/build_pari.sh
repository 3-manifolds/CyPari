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
    export CFLAGS='-arch i386 -mmacosx-version-min=10.4 '
    ./Configure --prefix=${PREFIX} --without-gmp --host=i386-darwin
    cd Odarwin-i386
    make install-lib-sta
    make install-include
    cd ..
    mv lib/libpari.a lib/i386-libpari.a
    mv include include32
#
    export CFLAGS='-arch x86_64'
    ./Configure --prefix=`pwd` --without-gmp --host=x86_64-darwin
    cd Odarwin-x86_64
    make install-lib-sta
    make install-include
    cd ..
    mv lib/libpari.a lib/x86_64-libpari.a
    mv include include64
#
    lipo lib/i386-libpari.a lib/x86_64-libpari.a -create -output lib/libpari.a
    ranlib lib/*.a
    ln -s include32 include

elif [ "$(uname)" = *MINGW32* ] ; then # MinGW on Windows
    ./Configure --prefix=${PREFIX} --libdir=lib --without-gmp --host=i386-mingw
    cd Omingw-i386
    make install-lib-sta
    make install-include
else  # Linux
    ./Configure --prefix=${PREFIX} --without-gmp
    cd Olinux-*
    make install
    make install-lib-sta
    cd ../..
    cp pari_src/src/language/anal.h pari/include/pari
    cd pari
#    ln -s lib/libpari.a libpari.a
fi
