#!/bin/bash
cd mingw32
/c/msys64/mingw32/bin/dlltool.exe -d ../moldname-msvcrt.def -U --dllname msvcr90.dll -l libmoldname90.a -k --as=/c/msys64/mingw32/bin/as.exe --as-flags=--32

/c/msys64/mingw32/bin/dlltool.exe -d ../moldname-msvcrt.def -U --dllname msvcr100.dll -l libmoldname100.a -k --as=/c/msys64/mingw32/bin/as.exe --as-flags=--32

cd ../mingw64
/c/msys64/mingw64/bin/dlltool.exe -d ../moldname-msvcrt.def -U --dllname msvcr90.dll -l libmoldname90.a -k --as=/c/msys64/mingw64/bin/as.exe --as-flags=--64

/c/msys64/mingw64/bin/dlltool.exe -d ../moldname-msvcrt.def -U --dllname msvcr100.dll -l libmoldname100.a -k --as=/c/msys64/mingw64/bin/as.exe --as-flags=--64

