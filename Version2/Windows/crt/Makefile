# Extract the object files from the mingw C runtime which are referenced
# by object files in libpari.a and put them into a separate static library.

gcc64_objs = _chkstk_ms.o

gcc32_objs = _chkstk_ms.o _divdi3.o _udivdi3.o _umoddi3.o

mingw64_objs = lib64_libmingwex_a-gettimeofday.o\
	lib64_libmingwex_a-log2.o \
	lib64_libmingwex_a-exp2.o \
	lib64_libmingwex_a-mingw_pformat.o \
	lib64_libmingwex_a-mingw_vfprintf.o \
	lib64_libmingwex_a-mingw_vsprintf.o \
	lib64_libmingwex_a-gdtoa.o \
	lib64_libmingwex_a-misc.o \
	lib64_libmingwex_a-dmisc.o \
	lib64_libmingwex_a-gmisc.o

mingw32_objs = lib32_libmingwex_a-gettimeofday.o\
	lib32_libmingwex_a-log2.o \
	lib32_libmingwex_a-exp2.o \
	lib32_libmingwex_a-mingw_pformat.o \
	lib32_libmingwex_a-mingw_vfprintf.o \
	lib32_libmingwex_a-mingw_vsprintf.o \
	lib32_libmingwex_a-gdtoa.o \
	lib32_libmingwex_a-misc.o \
	lib32_libmingwex_a-dmisc.o \
	lib32_libmingwex_a-gmisc.o

TOOLCHAIN32 = /c/mingw-w64/i686-6.3.0-posix-dwarf-rt_v5-rev1/mingw32
TOOLCHAIN64 = /c/mingw-w64/x86_64-6.3.0-posix-seh-rt_v5-rev1/mingw64
GCC_VERSION = 6.3.0
BIN32 = ${TOOLCHAIN32}/bin
BIN64 = ${TOOLCHAIN64}/bin
mingwex32 = ${TOOLCHAIN32}/i686-w64-mingw32/lib/libmingwex.a
mingwex64 = ${TOOLCHAIN64}/x86_64-w64-mingw32/lib/libmingwex.a
libgcc32 = ${TOOLCHAIN32}/lib/gcc/i686-w64-mingw32/${GCC_VERSION}/libgcc.a
libgcc64 = ${TOOLCHAIN64}/lib/gcc/x86_64-w64-mingw32/${GCC_VERSION}/libgcc.a


STDIO32 = ${TOOLCHAIN32}/x86_64-w64-mingw32/include/stdio.h
STDIO64 = ${TOOLCHAIN64}/x86_64-w64-mingw32/include/stdio.h

all: libparicrt32 libparicrt64 get_output_format32.o get_output_format64.o

libparicrt32:
	ar -x ${libgcc32} ${gcc32_objs}
	ar -r libparicrt32.a ${gcc32_objs}
	rm *.o

libparicrt64:
	ar -x ${libgcc64} ${gcc64_objs}
	ar -r libparicrt64.a ${gcc64_objs}
	rm *.o

get_output_format32.o: get_output_format.c
	(PATH=${BIN32};gcc -c -oget_output_format32.o get_output_format.c)

get_output_format64.o: get_output_format.c
	(PATH=${BIN64};gcc -c -oget_output_format64.o get_output_format.c)

clean:
	rm *.o
	rm *.a

save-stdio:
	cp -n ${STDIO32} ${STDIO32}.orig
	cp -n ${STDIO64} ${STDIO64}.orig

install-stdio:
	cp stdio.h ${STDIO32}
	cp stdio.h ${STDIO64}
