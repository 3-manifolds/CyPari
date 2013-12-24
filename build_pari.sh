#! /bin/bash
#
# This builds a fat pari library for OS X > 10.3 or a normal binary
# for Linux or Windows.  In the case of OS X, the includes that are 
# installed are those for i386, which are definitely different from
# those for ppc (especially the assembly language in pariinl.h), but
# we don't use the parts where they differ.  Eventually we need a
# switch for choosing the host.  Probably we can get some help from
# distutils, but I need to understand eggs a little better to see how
# to do that.

set -e

if [ ! -e pari-2.5.1.tar.gz ]; then
    echo "Downloading Pari 2.5.1..."
    python -c 'import urllib; urllib.urlretrieve("http://pari.math.u-bordeaux.fr/pub/pari/unix/pari-2.5.1.tar.gz", "pari-2.5.1.tar.gz")'
fi

echo "Untarring Pari..."
tar xzf pari-2.5.1.tar.gz

cd pari-2.5.1

echo "Building Pari libary..." 
if [ "$(uname)" = "Darwin" ] ; then  # OS X
    export CFLAGS='-arch i386 -mmacosx-version-min=10.4 '
    ./Configure --prefix=`pwd` --without-gmp --host=i386-darwin
    cd Odarwin-i386
    make install-lib-sta
    make install-include
    cd ..
    mv lib/libpari.a lib/i386-libpari.a
    mv include include32
#
    export CFLAGS='-arch x86_64'
    ./Configure --prefix=`pwd` --without-gmp --host=x86_64-darwin
    cd Odarwin-x86_64
    make install-lib-sta
    make install-include
    cd ..
    mv lib/libpari.a lib/x86_64-libpari.a
    mv include include64
#
    lipo lib/i386-libpari.a lib/x86_64-libpari.a -create -output lib/libpari.a
    ranlib lib/*.a
    ln -s include32 include

elif [[ "$(uname)" = *MINGW32* ]] ; then # MinGW on Windows
    ./Configure --prefix=`pwd` --libdir=lib --without-gmp --host=i386-mingw
    cd Omingw-i386
    make install-lib-sta
    make install-include
else  # Linux
    ./Configure --prefix=`pwd` --without-gmp
    cd Olinux-*
    make install-lib-sta
    make install-include
fi 
