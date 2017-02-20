#! /bin/bash

# This builds a fat (i386/x86_64) PARI library for OS X > 10.5.
# On Windows it uses mingw32 or mingw64, depending on the
# MSys2 environment.
# On linux the default system gcc is used to build for the host
# architecture.

set -e

if [ "$#" -eq 2 ] ; then
    PARIPREFIX=../../libcache/$1
    LIBDIR=../../libcache/$1/lib
    GMPPREFIX=../../libcache/$2
else
    PARIPREFIX=../../libcache/pari
    LIBDIR=../../libcache/pari/lib
    GMPPREFIX=../../libcache/gmp
fi

if [ "$2" != "nogmp" ] ; then
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
	if [ "$2" = "gmp32u" ] ; then
	    export ABI=32
	    export CFLAGS='-DUNIVERSAL_CRT'
	fi
	if [ "$2" = "gmp64u" ] ; then
	    export ABI=64
	    export CFLAGS='-DUNIVERSAL_CRT'
	fi
	./configure --prefix=$(pwd)/${GMPPREFIX}
    else # linux
	if [ "$2" = "gmp32" ] ; then
            export ABI=32
	else
            export ABI=64
	fi
	export CFLAGS=-fPIC
	./configure --prefix=$(pwd)/${GMPPREFIX}
    fi
    make install
    make distclean
    cd ../..
fi

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
    echo current directory `pwd`
    echo running mkdir ${PARIPREFIX} ${PARIPREFIX}/lib
    mkdir ${PARIPREFIX} ${PARIPREFIX}/lib
    lipo ../pari32/lib/libpari.a ../pari64/lib/libpari.a -create -output ${PARIPREFIX}/lib/libpari.a
    cp -r ../pari64/include ${PARIPREFIX}
    cp -r ../pari64/bin ${PARIPREFIX}
    cp -r ../pari64/share ${PARIPREFIX}
    cp -r ../pari64/lib/pari ${PARIPREFIX}/lib
    cp src/language/anal.h ${PARIPREFIX}/include/pari
    # Patch paricfg.h for dual architectures
    cd ${PARIPREFIX}
    patch include/pari/paricfg.h < ../../macOS/mac_paricfg.patch
    # patch gphelp, because we relocate it.
    sed -i -e 's/build\/pari_src\/\.\.\/pari64/libcache\/pari/g' ${PARIPREFIX}/bin/gphelp
    cd ../../build/pari_src
    
elif [ $(uname | cut -b -5) = "MINGW" ] ; then
    # This allows using C99 format specifications in printf.
    if [ "$1" = "pari32u" ] || [ "$1" = "pari64u" ] ; then
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

# Fix bad paths
sed -i -e 's/\/build\/pari_src\/\.\.\/\.\.//g' $PARIPREFIX/bin/gphelp
sed -i -e 's/\/build\/pari_src\/\.\.\/\.\.//g' $PARIPREFIX/include/pari/paricfg.h
sed -i -e 's/\/build\/pari_src\/\.\.\/\.\.//g' $PARIPREFIX/lib/pari/pari.cfg
sed -i -e 's/\/build\/pari_src\/\.\.\/\.\.//g' $PARIPREFIX/share/pari/doc/paricfg.tex
