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
tar xzf ../pari-2.9.1.tar.gz
mv pari-2.9.1 pari_src
cd pari_src
PREFIX=../pari
LIBDIR=../pari/lib

export DESTDIR=

echo "Building Pari libary..."
if [ $(uname) = "Darwin" ] ; then # build for both 32 and 64 bits
    export CFLAGS='-mmacosx-version-min=10.5 -arch i386'
    ./Configure --prefix=${PREFIX} --libdir=${LIBDIR} --without-gmp
    cd Odarwin-i386
    make install-lib-sta
    make install-include
    cd ..
    cp src/language/anal.h ../pari/include/pari
    mv ../pari ../pari-i386
    export CFLAGS='-mmacosx-version-min=10.5 -arch x86_64'
    ./Configure --prefix=${PREFIX} --libdir=${LIBDIR} --without-gmp --host=x86_64-darwin
    cd Odarwin-x86_64
    make install
    make install-lib-sta
    cd ..
    lipo ../pari-i386/lib/libpari.a ../pari/lib/libpari.a -create -output ../pari/lib/libpari.a
    cp src/language/anal.h ../pari/include/pari
    cd ..
    echo Patching paricfg.h for dual architectures
    patch pari/include/pari/paricfg.h < ../macOS/mac_paricfg.patch
else
    if [ $(uname | cut -b -5) = "MINGW" ] ; then
	export CFLAGS='-D__USE_MINGW_ANSI_STDIO -Dprintf=__MINGW_PRINTF_FORMAT'
    fi
    
    ./Configure --prefix=${PREFIX} --libdir=${LIBDIR} --without-gmp

    if [ $(uname | cut -b -5) = "MINGW" ] ; then
	# remove the funky RUNPTH which confuses gcc and is irrelevant anyway
	echo Patching the MinGW Makefile ...
	sed -i -e s/^RUNPTH/\#RUNPTH/ Omingw-*/Makefile
    fi
    
    make install
    make install-lib-sta
    cp src/language/anal.h ../pari/include/pari
fi
# Fix non-prototype function declarations
sed -i -e s/\(\)\;/\(void\)\;/ ../pari/include/pari/paripriv.h
