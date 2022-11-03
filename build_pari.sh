#! /bin/bash
# On macOS this builds both arm and x86_64 PARI librariies for OS X >= 10.9.
# On Windows it uses mingw32 or mingw64, depending on the MSys2 environment.
# On linux the default system gcc is used to build for the host architecture.
# There are two required arguments, to specify word sizes for gmp and pari.
# For macOS these arguments should be pari and gmp.

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
    exit
fi

PARIURL=https://pari.math.u-bordeaux.fr/pub/pari/OLD/2.11/
PARIVERSION=pari-2.11.4
GMPURL=https://ftp.gnu.org/gnu/gmp/
GMPVERSION=gmp-6.2.1

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
        mv gmp/arm/{include,share} gmp
	lipo -create gmp/arm/lib/libgmp.10.dylib gmp/intel/lib/libgmp.10.dylib -output gmp/lib/libgmp.dylib
	lipo -create gmp/arm/lib/libgmp.a gmp/intel/lib/libgmp.a -output gmp/lib/libgmp.a
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
else
    cd build/pari_src
fi

export DESTDIR=
if [ $(uname) = "Darwin" ] ; then
    # Run the configure script to build gphelp, needed by autogen.
    ./Configure
    # Pari's Configure script does not support cross compiling unless the build
    # system has an emulator for the target CPU.  But we can compile for multiple
    # architectures if we have the build directories that Pari's Configure script
    # constructs.  So we use canned copies of those build directories.
    rm -rf Odarwin*
    tar xvfz ../../Odarwin.tgz
    cd Odarwin-arm64
    make install
    make install-lib-sta
    make install-doc
    make clean
    cd ../Odarwin-x86_64
    make install
    make install-lib-sta
    make clean
    cd ../../../libcache
    # Glue the two libraries together with lipo.
    mkdir -p pari/lib
    rm -rf pari/{include,share,bin}
    cp -R pari/arm/{include,share,bin} pari
    # Weird Pari glitch - gphelp can't find the doc directory
    ln -s ../share/pari/doc pari/bin
    lipo -create pari/arm/lib/libpari.a pari/intel/lib/libpari.a -output pari/lib/libpari.a
    lipo -create pari/arm/lib/libpari.dylib pari/intel/lib/libpari.dylib -output pari/lib/libpari.dylib
    cd ../build/pari_src
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
    if [ "$2" = "gmp32" ] ; then
	export MSYSTEM=MINGW32
    else
	export MSYSTEM=MINGW64
    fi
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --without-readline --with-gmp=${GMPPREFIX}

    # When building for x86_64 parigen.h says #define long long long
    # and that macro breaks the bison compiler compiler.
    if [ "$1" == "pari64" ]; then
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
