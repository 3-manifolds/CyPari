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

GCC_VERSION = $(shell gcc -dumpversion)
mingwex32 = /c/msys64/mingw32/i686-w64-mingw32/lib/libmingwex.a
mingwex64 = /c/msys64/mingw64/x86_64-w64-mingw32/lib/libmingwex.a
libgcc32 = /c/msys64/mingw32/lib/gcc/i686-w64-mingw32/$(GCC_VERSION)/libgcc.a
libgcc64 = /c/msys64/mingw64/lib/gcc/x86_64-w64-mingw32/$(GCC_VERSION)/libgcc.a

all: libparicrt32 libparicrt64 get_output_format32.o get_output_format64.o

libparicrt32:
	ar -x $(libgcc32) $(gcc32_objs)
	ar -x $(mingwex32) $(mingw32_objs)
	ar -r libparicrt32.a $(gcc32_objs) $(mingw32_objs)
	rm *.o

libparicrt64:
	ar -x $(libgcc64) $(gcc64_objs)
	ar -x $(mingwex64) $(mingw64_objs)
	ar -r libparicrt64.a $(gcc64_objs) $(mingw64_objs)
	rm *.o

get_output_format32.o: get_output_format.c
	(PATH=/mingw32/bin;gcc -c -oget_output_format32.o get_output_format.c)

get_output_format64.o: get_output_format.c
	(PATH=/mingw64/bin;gcc -c -oget_output_format64.o get_output_format.c)

clean:
	rm *.o
	rm *.a

