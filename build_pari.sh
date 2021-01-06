#! /bin/bash

# On macOS this builds a x86_64 PARI library for OS X > 10.5.
# On Windows it uses mingw32 or mingw64, depending on the MSys2 environment.
# On linux the default system gcc is used to build for the host architecture.

set -e

PARIURL=https://pari.math.u-bordeaux.fr/pub/pari/OLD/2.11/
PARIVERSION=pari-2.11.4
GMPURL=https://ftp.gnu.org/gnu/gmp/
GMPVERSION=gmp-6.2.0

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

if [ "$2" != "nogmp" ] && [ ! -e ${GMPPREFIX} ] ; then
    if [ ! -e ${GMPVERSION}.tar.bz2 ] ; then
        echo "Downloading GMP source archive ..." ;
        curl -O ${GMPURL}${GMPVERSION}.tar.bz2 ;
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
    #macOS -- build 64bits only
	export CFLAGS='-mmacosx-version-min=10.5 -arch x86_64'
	export ABI=64
	./configure --with-pic --build=x86_64-none-darwin --prefix=${GMPPREFIX}
	make install
        make distclean
	cd ../..
    else
	if [ $(uname | cut -b -5) = "MINGW" ] ; then
	# Windows
	    if [ "$2" = "gmp32u" ] || [ "$2" = "gmp64u" ] ; then
		export CFLAGS='-DUNIVERSAL_CRT'
	    fi
	    if [ "$2" = "gmp32" ] || [ "$2" = "gmp32u" ] ; then
		export MSYSTEM=MINGW32
		export ABI=32
		BUILD=i686-w32-mingw32
	    else
		export MSYSTEM=MINGW64
		export ABI=64
		BUILD=x86_64-pc-mingw64
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
        curl -O ${PARIURL}${PARIVERSION}.tar.gz ;
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
#macOS -- build 64bits only
    export CFLAGS='-mmacosx-version-min=10.5 -arch x86_64'
    ./Configure --prefix=${PARIPREFIX} --with-gmp=${GMPPREFIX} --host=x86_64-darwin
    cd Odarwin-x86_64
    make install
    make install-lib-sta
    cd ${PARIPREFIX}
    cd ../../build/pari_src
    
elif [ $(uname | cut -b -5) = "MINGW" ] ; then
#Windows
    # Neuter win32_set_pdf_viewer so it won't break linking with MSVC.
    patch -N -p0 < ../../Windows/mingw_c.patch || true
    # When we build the pari library for linking with Visual C 2014
    # (i.e. for Python 3.5 and 3.6) the Pari configure script has
    # trouble linking some of the little C programs which verify that
    # we have provided the correct gmp configuration in the options to
    # Configure.  Also, the msys2 uname produces something Pari does
    # not recognize.  Since we are not lying about our gmpntf
    # configuration we just patch get_gmp and arch-osname to give the
    # right answers.
    patch -N -p1 < ../../Windows/pari_config.patch || true
    # This allows using C99 format specifications in printf.
    if [ "$1" = "pari32u" ] || [ "$1" = "pari64u" ] ; then
	export CFLAGS='-DUNIVERSAL_CRT -D__USE_MINGW_ANSI_STDIO'
    else
	export CFLAGS=export CFLAGS='-D__USE_MINGW_ANSI_STDIO -Dprintf=__MINGW_PRINTF_FORMAT'
    fi
    if [ "$2" = "gmp32" ] || [ "$2" = "gmp32u" ] ; then
	export MSYSTEM=MINGW32
    else
	export MSYSTEM=MINGW64
    fi
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --with-gmp=${GMPPREFIX}

    # When building for x86_64 parigen.h says #define long long long
    # and that macro breaks the bison compiler compiler.
    if [ "$1" == "pari64" ] || [ "$1" == "pari64u" ] ; then
	patch -N -p0 < ../../Windows/parigen.h.patch || true
    fi
    cd Omingw-*
    make install-lib-sta
    make install-include
    make install-doc
    make install-cfg
    make install-bin-sta
    cd ..
else
# linux
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --with-gmp=${GMPPREFIX}
    make install
    make install-lib-sta
fi

# We need this "private" header file.
if [ -d src64 ] ; then
    cp src64/language/anal.h ${PARIPREFIX}/include/pari/
else
    cp src/language/anal.h $PARIPREFIX/include/pari	
fi


    

