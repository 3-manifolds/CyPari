# On macOS this builds both arm and x86_64 PARI librariies for OS X >=
# 10.9.  On Windows it uses the ucrt64 toolchain in Msys2. On linux
# the default system gcc is used to build for the host architecture.

set -e

PARIURL=http://pari.math.u-bordeaux.fr/pub/pari/unix/
PARIVERSION=pari-2.15.4
GMPURL=https://ftp.gnu.org/gnu/gmp/
GMPVERSION=gmp-6.3.0

if [[ $(pwd) =~ " " ]]; then
    echo "Fatal Error: Sorry, the path:"
    echo "             $(pwd)"
    echo "             has a space in it, preventing GMP from building"
    echo "             because of a limitation of libtool."
    exit 1
fi

PARIPREFIX=$(pwd)/libcache/pari
PARILIBDIR=$(pwd)/libcache/pari/lib
GMPPREFIX=$(pwd)/libcache/gmp

echo Building gmp ...

if [ ! -e ${GMPPREFIX} ] ; then
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
	# Use the old linker for x86_64 to avoid a spurious "branch8 out of range" error.
	if [ `/usr/bin/ld -ld_classic 2> >(grep -c warning)` != "0" ] ; then
	    export LDFLAGS="-ld_classic"
	fi
	export CFLAGS="-arch x86_64 -mmacosx-version-min=10.9 -mno-avx -mno-avx2 -mno-bmi2"
	./configure --with-pic --build=${BUILD_SYSTEM} --host=x86_64-none-darwin --enable-fat --prefix=${GMPPREFIX}/intel
	make install
        make distclean
	export CFLAGS="-arch arm64 -mmacosx-version-min=10.9"
        export LDFLAGS=""
	./configure --with-pic --build=${BUILD_SYSTEM} --host=arm64-none-darwin --prefix=${GMPPREFIX}/arm
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
	    export PATH=/c/msys64/ucrt64/bin:$PATH
	    export MSYSTEM=UCRT64
	    export CC=/c/msys64/ucrt64/bin/gcc
	    export ABI=64
	    BUILD=x86_64-pc-mingw64
	else
	# linux
	    export ABI=64
	    BUILD=x86_64-none-none
	fi
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
    export PATH=/c/msys64/ucrt64/bin:$PATH
    export MSYSTEM=UCRT64
    export CC=/c/msys64/ucrt64/bin/gcc
    # Disable avx and sse2.
    export CFLAGS="-U HAS_AVX -U HAS_AVX512 -U HAS_SSE2"
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --without-readline --with-gmp=${GMPPREFIX}
    cd Omingw-*
    make install-lib-sta
    make install-include
    make install-doc
    make install-cfg
    make install-bin-sta
else
# linux
    ./Configure --prefix=${PARIPREFIX} --libdir=${PARILIBDIR} --with-gmp=${GMPPREFIX}
    make install
    make install-lib-sta
fi

