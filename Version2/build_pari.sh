#! /bin/bash

# This builds a fat (i386/x86_64) PARI library for OS X > 10.5.
# On Windows it uses mingw32 or mingw64, depending on the
# MSys2 environment.
# On linux the default system gcc is used to build for the host
# architecture.

set -e

if [ "$#" -eq 2 ] ; then
    PARIPREFIX=../$1
    LIBDIR=../$1/lib
    GMPPREFIX=../$2
else
    PARIPREFIX=../pari
    LIBDIR=../pari/lib
    GMPPREFIX=../gmp
fi

if [ ! -d "build/gmp_src" ] ; then
    echo "Untarring gmp ..."
    if [ ! -d "build" ] ; then
	mkdir build ;
    fi
    cd build
    tar xzf ../gmp-6.1.2.tar.gz
    mv gmp-6.1.2 gmp_src
    cd gmp_src
else
    cd build/gmp_src
fi
if [ $(uname) = "Darwin" ] ; then
    export CFLAGS='-fPIC -mmacosx-version-min=10.5 -arch i386 -arch x86_64'
    ./configure --disable-assembly --prefix=$(pwd)/${GMPPREFIX}
elif [ $(uname | cut -b -5) = "MINGW" ] ; then
    echo MinGW
    ./configure --prefix=$(pwd)/${GMPPREFIX}
else    
    export CFLAGS=-fPIC
    ./configure --prefix=$(pwd)/${GMPPREFIX}
fi

make install
cd ../..

if [ ! -d "build/pari_src" ] ; then
    echo "Untarring Pari..."
    if [ ! -d "build" ] ; then
	mkdir build ;
    fi
    cd build
    tar xzf ../pari-2.9.1.tar.gz
    mv pari-2.9.1 pari_src
    cd pari_src
    # neuter win32_set_pdf_viewer so it won't break linking with MSVC.
    patch -p0 < ../../Windows/mingw_c.patch
else
    cd build/pari_src
fi

export DESTDIR=

echo "Building Pari libary..."

if [ $(uname) = "Darwin" ] ; then # build for both 32 and 64 bits
    export CFLAGS='-mmacosx-version-min=10.5 -arch i386'
    ./Configure --prefix=../pari32 --libdir=../pari32/lib --with-gmp=${GMPPREFIX}
    cd Odarwin-i386
    make install-lib-sta
    make install-include
    cd ..
    cp src/language/anal.h ../pari32/include/pari
    export CFLAGS='-mmacosx-version-min=10.5 -arch x86_64'
    ./Configure --prefix=../pari64 --libdir=../pari64/lib --with-gmp=${GMPPREFIX} --host=x86_64-darwin
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
    
elif [ $(uname | cut -b -5) = "MINGW" ] ; then
    # This allows using C99 format specifications in printf.
    if [[ "$1" = *"u" ]] ; then
	export CFLAGS='-D__USE_MINGW_ANSI_STDIO -Dprintf=__MINGW_PRINTF_FORMAT -DUNIVERSAL_CRT'
    else
	export CFLAGS='-D__USE_MINGW_ANSI_STDIO -Dprintf=__MINGW_PRINTF_FORMAT'
    fi
    ./Configure --prefix=${PARIPREFIX} --libdir=${LIBDIR} --with-gmp

    make install-lib-sta RUNPTH=
    
    # We cannot build the dll for Pythons > 3.4, because mingw can't
    # handle the Universal CRT.  So we also cannot build gp.
    cd Omingw-*
    make install-include
    make install-cfg
    make install-doc
    cd ..
    # Remove the .o files, since Pari always builds in the same directory 
    make clean
    
else # linux, presumably
    ./Configure --prefix=${PARIPREFIX} --libdir=${LIBDIR} --with-gmp=${GMPPREFIX}
    make install
    make install-lib-sta
fi

cp src/language/anal.h $PARIPREFIX/include/pari

# Fix non-prototype function declarations
sed -i -e s/\(\)\;/\(void\)\;/ $PARIPREFIX/include/pari/paripriv.h
