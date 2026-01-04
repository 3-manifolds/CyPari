/*
 * Pari's workaround fo the fact that Windows has a 32 bit long
 * and a 64 bit long long, while Unix uses 64 bit integers for
 * both, is the following, amazingly dangerous, hack:
 *     #define long long long
 * Amazingly, the only Python header in which this hack currently
 * wreaks havoc is  internal/pycore_lock.h, introduced in
 * Python 3.13. Our hack to work around Pari's hack is to place
 * a patched replacement for internal/pycore_lock.h in this directory,
 * where the compiler will find it before it finds the python
 * version.  The patch undoes the "long" macro at the beginning of
 * the file and restores it at the end.
 * Note: There are also Windows headers which are broken by
 * the Pari hack.  Those are dealt with in setup.py.
 */
#include "patchlevel.h"
#undef long
#if PY_MINOR_VERSION == 13
  #include "internal/313/pycore_lock.h"
#endif
#if PY_MINOR_VERSION == 14
  #include "internal/314/pycore_lock.h"
#endif 
#define long long long
