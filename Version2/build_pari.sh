#! /bin/bash
#
# This builds a fat (i386/x86_64) PARI library for OS X > 10.5 or a 
# normal binary for Linux or Windows. 
#

set -e
if [ ! -d "build/pari_src" ] ; then
    echo "Untarring Pari..."
    if [ ! -d "build" ] ; then
	mkdir build ;
    fi
    cd build
    tar xzf ../pari-2.9.1.tar.gz
    mv pari-2.9.1 pari_src
    cd pari_src
else
    cd build/pari_src
fi

if [ "$#" -eq 1 ] ; then
    PREFIX=../$1
    LIBDIR=../$1/lib
else
    PREFIX=../pari
    LIBDIR=../pari/lib
fi

export DESTDIR=

echo "Building Pari libary..."
if [ $(uname) = "Darwin" ] ; then # build for both 32 and 64 bits
    export CFLAGS='-mmacosx-version-min=10.5 -arch i386'
    ./Configure --prefix=../pari32 --libdir=../pari32/lib --without-gmp
    cd Odarwin-i386
    make install-lib-sta
    make install-include
    cd ..
    cp src/language/anal.h ../pari32/include/pari
    export CFLAGS='-mmacosx-version-min=10.5 -arch x86_64'
    ./Configure --prefix=../pari64 --libdir=../pari64/lib --without-gmp --host=x86_64-darwin
    cd Odarwin-x86_64
    make install
    make install-lib-sta
    cd ..
    mkdir ../pari ../pari/lib
    lipo ../pari32/lib/libpari.a ../pari64/lib/libpari.a -create -output ../pari/lib/libpari.a
    echo current directory: `pwd`
    echo `ls -l ..` `ls -l ../pari64`
    cp -r ../pari64/include ../pari
    cp src/language/anal.h ../pari/include/pari
    cd ..
    echo Patching paricfg.h for dual architectures
    patch pari/include/pari/paricfg.h < ../macOS/mac_paricfg.patch
    cd pari_src
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
    cp src/language/anal.h $PREFIX/include/pari
fi
# Fix non-prototype function declarations
sed -i -e s/\(\)\;/\(void\)\;/ $PREFIX/include/pari/paripriv.h
