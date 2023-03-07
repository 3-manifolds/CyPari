#! /bin/bash

# On macOS this builds both arm and x86_64 PARI librariies for OS X >=
# 10.9.  On Windows it uses the clang32 or ucrt64 toolchains,
# depending on the MSys2 environment.  On linux the default system gcc
# is used to build for the host architecture.  There are two required
# arguments, to specify word sizes for gmp and pari.  For macOS these
# arguments should be pari and gmp.

set -e

if [ $# != 2 ]; then
    usage=failed;
fi
if [ "$1" != "pari32" ] && [ "$1" != "pari64" ] && [ "$1" != "pari" ]; then
    usage=failed;
fi
if [ "$2" != "gmp32" ] && [ "$2" != "gmp64" ] && [ "$2" != "gmp" ]; then
    usage=failed;
fi
if [ "$usage" = "failed" ]; then
    echo "usage: build_pari.sh pari32|pari64|pari gmp32|gmp64|gmp"
    echo "For macOS use pari and gmp as arguments to build universal binaries."
    exit
fi

#PARIURL=https://pari.math.u-bordeaux.fr/pub/pari/OLD/2.11/
#PARIVERSION=pari-2.11.4
PARIURL=http://pari.math.u-bordeaux.fr/pub/pari/unix/
PARIVERSION=pari-2.15.2
GMPURL=https://ftp.gnu.org/gnu/gmp/
GMPVERSION=gmp-6.2.1

if [[ $(pwd) =~ " " ]]; then
    echo "Fatal Error: Sorry, the path:"
    echo "             $(pwd)"
    echo "             has a space in it, preventing GMP from building"
    echo "             because of a limitation of libtool."
    exit 1
fi

PARIPREFIX=$(pwd)/libcache/$1
PARILIBDIR=$(pwd)/libcache/$1/lib
GMPPREFIX=$(pwd)/libcache/$2

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
	export ABI=64
        if /usr/bin/machine | grep arm > /dev/null ; then
	    BUILD_SYSTEM=arm64-none-darwin
	else
            BUILD_SYSTEM=x86_64-none-darwin
        fi
	export CFLAGS="-arch arm64 -mmacosx-version-min=10.9"
	./configure --with-pic --build=${BUILD_SYSTEM} --host=arm64-none-darwin --prefix=${GMPPREFIX}/arm
	make install
	make distclean
	export CFLAGS="-arch x86_64 -mmacosx-version-min=10.9 -mno-avx -mno-avx2 -mno-bmi2"
	./configure --with-pic --build=${BUILD_SYSTEM} --host=x86_64-none-darwin --enable-fat --prefix=${GMPPREFIX}/intel
	make install
        make distclean
	cd ../../libcache
        mkdir -p gmp/lib
        mv $2/arm/{include,share} gmp
	lipo -create $2/arm/lib/libgmp.10.dylib $2/intel/lib/libgmp.10.dylib -output gmp/lib/libgmp.dylib
	lipo -create $2/arm/lib/libgmp.a $2/intel/lib/libgmp.a -output gmp/lib/libgmp.a
	cd ..
    else
	if [ `python -c "import sys; print(sys.platform)"` = 'win32' ] ; then
	# Windows
	    if [ "$2" = "gmp32" ] ; then
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
	echo compiler is `which gcc`
	echo linker is `which ld`
	echo Configuring gmp with ./configure --build=${BUILD} --prefix=${GMPPREFIX} --with-pic
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
    # Add a guard against multiple includes of paristio.h and fix uispsp.
    patch -p0 < ../../patches/pari_2.15.patch
else
    cd build/pari_src
    # Add a guard against multiple includes of paristio.h and fix uispsp.
    patch -p0 < ../../patches/pari_2.15.patch
fi

export DESTDIR=
if [ $(uname) = "Darwin" ] ; then
    rm -rf Odarwin*
    export CFLAGS="-arch x86_64 -arch arm64 -mmacosx-version-min=10.9"
# For debugging:
#   export CFLAGS="-g -arch x86_64 -arch arm64 -mmacosx-version-min=10.9"
    ./Configure --host=universal-darwin --prefix=${PARIPREFIX} --with-gmp=${GMPPREFIX}
    cd Odarwin-universal
    make install
    make install-lib-sta
    make clean
elif [ `python -c "import sys; print(sys.platform)"` = 'win32' ] ; then
#Windows
    # Get rid of win32_set_pdf_viewer so it won't break linking with MSVC.
    patch -N -p0 < ../../Windows/mingw_c.patch || true
    # When we build the pari library for linking with Visual C 2014
    # the Pari configure script has trouble linking some of the little
    # C programs which verify that we have provided the correct gmp
    # configuration in the options to Configure.  Also, the msys2
    # uname produces something Pari does not recognize.  Since we are
    # not lying about our gmpntf configuration we just patch get_gmp
    # and arch-osname to give the right answers.
    patch -N -p0 < ../../Windows/pari_config.patch
    if [ "$2" = "gmp32" ] ; then
	export MSYSTEM=CLANG32
    else
	export MSYSTEM=MINGW64
    fi
    # The dlltool that is provided by clang32 does not accept the
    # --version option.  This confuses Pari's config tools.  So we let
    # Pari use the dlltool in the mingw32 toolchain.
    if [ "$1" == "pari32" ]; then
	export DLLTOOL="/c/msys64/mingw32/bin/dlltool"
    fi
    # Disable avx and sse2.
    if [ "$1" == "pari64" ]; then
        export CFLAGS="-UHAS_AVX -UHAS_AVX512 -UHAS_SSE2"
    fi
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --without-readline --with-gmp=${GMPPREFIX}
    cd Omingw-*
    # When building for x86 with clang32, the Makefile uses the -rpath option
    # which is not recognized by the clang32 linker, and causes an error.
    if [ "$1" == "pari32" ]; then
	sed -i s/$\(RUNPTH\)//g Makefile
	sed -i s/$\(RUNPTH_FINAL\)//g Makefile
    fi
    make install-lib-sta
    make install-include
    make install-doc
    make install-cfg
    # Also the clang32 linker does not require the .def file, and just gets
    # confused by it.
    if [ "$1" == "pari32" ]; then
	cat /dev/null > libpari_exe.def
    fi
    make install-bin-sta
else
# linux
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --with-gmp=${GMPPREFIX}
    make install
    make install-lib-sta
fi

