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
tar xvzf ../pari-2.9.1.tar.gz
mv pari-2.9.1 pari_src
cd pari_src

echo "Building Pari libary..."
# Pari has become smarter about figuring out the platform.  But we may
# still need to deal with fat binaries for macOS.  So leaving this here.
# if [ "$(uname)" = "Darwin" ] ; then  # OS X
#     export CFLAGS='-arch x86_64'
#     ./Configure --prefix=${PREFIX} --without-gmp --host=x86_64-darwin
#     cd Odarwin-x86_64
#     make install
#     make install-lib-sta
#     cd ../..
#     cp pari_src/src/language/anal.h pari/include/pari
#else
./Configure --prefix=${PREFIX} --without-gmp
make install
make install-lib-sta
cd ../..
cp pari_src/src/language/anal.h pari/include/pari
#fi
