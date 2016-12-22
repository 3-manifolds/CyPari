#! /bin/bash
#
# This builds a fat (i386/x86_64) PARI library for OS X > 10.5 or a 
# normal binary for Linux or Windows. 
#

set -e
if [ ! -d "build" ] ; then
    mkdir build ;
else
    rm -rf build/pari_src
fi
echo "Untarring Pari..."
cd build
tar xvzf ../pari-2.9.1.tar.gz
mv pari-2.9.1 pari_src
cd pari_src
PREFIX=../pari
LIBDIR=../pari/lib

export DESTDIR=

echo "Building Pari libary..."
./Configure --prefix=${PREFIX} --libdir=${LIBDIR} --without-gmp
if [ $(uname | cut -b -5) = "MINGW" ] ; then
    # remove the funky RUNPTH which confuses gcc and is irrelevant anyway
    echo Patching the MinGW Makefile ...
    sed -i -e s/^RUNPTH/\#RUNPTH/ Omingw-*/Makefile
fi
make install
make install-lib-sta
cp src/language/anal.h ../pari/include/pari

