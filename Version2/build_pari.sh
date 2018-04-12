#! /bin/bash

# On macOS this builds a fat (i386/x86_64) PARI library for OS X > 10.5.
# On Windows it uses mingw32 or mingw64, depending on the MSys2 environment.
# On linux the default system gcc is used to build for the host architecture.

set -e

PARIURL=https://pari.math.u-bordeaux.fr/pub/pari/unix/
PARIVERSION=pari-2.9.3
GMPURL=https://ftp.gnu.org/gnu/gmp/
GMPVERSION=gmp-6.1.2

if [[ $(pwd) =~ " " ]]; then
    echo "Fatal Error: Sorry, the path:"
    echo "             $(pwd)"
    echo "             has a space in it, preventing GMP from building"
    echo "             because of a limitation of libtool."
    exit 1
fi

if [ "$#" -eq 2 ] ; then
    PARIPREFIX=$(pwd)/libcache/$1
    PARILIBDIR=$(pwd)/libcache/$1/lib
    GMPPREFIX=$(pwd)/libcache/$2
else
    PARIPREFIX=$(pwd)/libcache/pari
    PARILIBDIR=$(pwd)/libcache/pari/lib
    GMPPREFIX=$(pwd)/libcache/gmp
fi

echo Building gmp ...

if [ "$2" != "nogmp" ] ; then
    if [ ! -e ${GMPVERSION}.tar.bz2 ] ; then
        echo "Downloading GMP source archive ..." ;
	if [ $(uname) = "Darwin" ] ; then
            curl -O ${GMPURL}${GMPVERSION}.tar.bz2 ;
	else
            wget ${GMPURL}${GMPVERSION}.tar.bz2 ;
	fi
    fi
    if [ ! -d "build/gmp_src" ] ; then
	echo "Extracting gmp source code ..."
	if [ ! -d "build" ] ; then
	    mkdir build ;
	fi
	cd build
	tar xjf ../${GMPVERSION}.tar.bz2
	mv ${GMPVERSION} gmp_src
	cd gmp_src
    else
	cd build/gmp_src
    fi
    if [ $(uname) = "Darwin" ] ; then
    #macOS -- build separately for 32 and 64 bits then use lipo
	export CFLAGS='-mmacosx-version-min=10.5 -arch i386'
	export ABI=32
	./configure --with-pic --build=i686-none-darwin --prefix=${GMPPREFIX}32
	make install
	make distclean
	export CFLAGS='-mmacosx-version-min=10.5 -arch x86_64'
	export ABI=64
	./configure --with-pic --build=x86_64-none-darwin --prefix=${GMPPREFIX}64
	make install
        make distclean
	if [ ! -d "${GMPPREFIX}/lib" ] ; then
	    mkdir -p ${GMPPREFIX}/lib
	fi
	lipo ${GMPPREFIX}32/lib/libgmp.a ${GMPPREFIX}64/lib/libgmp.a -create -output ${GMPPREFIX}/lib/libgmp.a
	cd ../..
    else
	if [ $(uname | cut -b -5) = "MINGW" ] ; then
	# Windows -- with no CFLAGS the ABI is not needed
	    if [ "$2" = "gmp32u" ] || [ "$2" = "gmp64u" ] ; then
		export CFLAGS='-DUNIVERSAL_CRT'
	    fi
	    if [ "$2" = "gmp32" ] || [ "$2" = "gmp32u" ] ; then
		export ABI=32
		BUILD=i686-w32-mingw32
	    else
		export ABI=64
		BUILD=x86_64-w64-mingw32
	    fi
	else
	# linux
	    if [ "$2" = "gmp32" ] ; then
		export ABI=32
		BUILD=i686-none-none
	    else
		export ABI=64
		BUILD=x86_64-none-none
	    fi
	fi
	echo ./configure --build=${BUILD} --prefix=${GMPPREFIX} --with-pic
	./configure --build=${BUILD} --prefix=${GMPPREFIX} --with-pic
	make install
	make distclean
	cd ../..
    fi
fi

echo Building Pari ...
    
if [ ! -d "build/pari_src" ] ; then
    if [ ! -e ${PARIVERSION}.tar.gz ] ; then
        echo "Downloading Pari source archive ..." ;
	if [ $(uname) = "Darwin" ] ; then
            curl -O ${PARIURL}${PARIVERSION}.tar.gz ;
	else
            wget ${PARIURL}${PARIVERSION}.tar.gz ;
	fi
    fi
    echo "Extracting Pari source code ..."
    if [ ! -d "build" ] ; then
	mkdir build ;
    fi
    cd build
    tar xzf ../${PARIVERSION}.tar.gz
    mv ${PARIVERSION} pari_src
    cd pari_src
else
    cd build/pari_src
fi

export DESTDIR=
if [ $(uname) = "Darwin" ] ; then
#macOS -- build separately for 32 and 64 bits then use lipo
    export CFLAGS='-mmacosx-version-min=10.5 -arch i386'
    ./Configure --prefix=../pari32 --libdir=../pari32/lib --with-gmp=${GMPPREFIX}32
    cd Odarwin-i386
    make install-lib-sta
    make install-include
    cd ..
    cp src/language/anal.h ../pari32/include/pari
    export CFLAGS='-mmacosx-version-min=10.5 -arch x86_64'
    ./Configure --prefix=../pari64 --libdir=../pari64/lib --with-gmp=${GMPPREFIX}64 --host=x86_64-darwin
    cd Odarwin-x86_64
    make install
    make install-lib-sta
    cd ..
    if [ ! -d ${PARILIBDIR} ] ; then
	mkdir -p ${PARILIBDIR}
    fi
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
#Windows
    # Neuter win32_set_pdf_viewer so it won't break linking with MSVC.
    patch -p0 < ../../Windows/mingw_c.patch
    # When we build the pari library for linking with Visual C 2014
    # (i.e. for Python 3.5 and 3.6) the Pari configure script has
    # trouble linking some of the little C programs which verify that
    # we have provided the correct gmp configuration in the options to
    # Configure.  Also, the msys2 uname produces something Pari does
    # not recognize.  Since we are not lying about our gmp
    # configuration we just patch get_gmp and arch-osname to give the
    # right answers.
    patch -p1 < ../../Windows/pari_config.patch
    # This allows using C99 format specifications in printf.
    if [ "$1" = "pari32u" ] || [ "$1" = "pari64u" ] ; then
	export CFLAGS='-DUNIVERSAL_CRT -D__USE_MINGW_ANSI_STDIO -Dprintf=__MINGW_PRINTF_FORMAT'
    else
	export CFLAGS='-D__USE_MINGW_ANSI_STDIO -Dprintf=__MINGW_PRINTF_FORMAT'
    fi
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --with-gmp=${GMPPREFIX}

    # Pari's Configure script screws up the paths if you specify
    # an absolute prefix within the msys64 environment.
    # At least the pattern is easy to recognize.
    cd Omingw-*
    sed -i -e 's/C:.*C:/C:/g' Makefile
    sed -i -e 's/C:.*C:/C:/g' pari.cfg
    sed -i -e 's/C:.*C:/C:/g' pari.nsi
    sed -i -e 's/C:.*C:/C:/g' paricfg.h
    cd ..
    make install-lib-sta
    
    # We cannot build the dll for Pythons > 3.4, because mingw can't
    # handle the Universal CRT.  So we also cannot build gp. But we
    # need gphelp.  So do a partial install.
    cd Omingw-*
    make install-include
    make install-cfg
    make install-doc
    cd ..

    # Pari's Configure will also screw up the path in the gphelp script.
    sed -i -e 's/C:.*C:/C:/g' ${PARIPREFIX}/bin/gphelp

    # Remove the .o files, since Pari always builds in the same directory.
    make clean
    
else
# linux
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --with-gmp=${GMPPREFIX}
    make install
    make install-lib-sta
fi

# We need this "private" header file.
cp src/language/anal.h $PARIPREFIX/include/pari

# Fix some non-prototype function declarations (until Pari 2.9.2 is released).
sed -i -e s/\(\)\;/\(void\)\;/ $PARIPREFIX/include/pari/paripriv.h
