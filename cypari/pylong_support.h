#include "Python.h"

/*
The (signed) size is stored in ob_size in the HEAD for Python 3.11
Note that the HEAD type changed in 3.12.  Also, the size is stored
in the lv_tag for 3.12.

Excerpt from longintrepr.h:

Python 3.11:
struct _longobject {
    PyObject_VAR_HEAD
    digit ob_digit[1];
};

Python 3.12
 Long integer representation.
   The absolute value of a number is equal to
        SUM(for i=0 through abs(ob_size)-1) ob_digit[i] * 2**(SHIFT*i)
   Negative numbers are represented with ob_size < 0;
   zero is represented by ob_size == 0.
   In a normalized number, ob_digit[abs(ob_size)-1] (the most significant
   digit) is never zero.  Also, in all cases, for all valid i,
        0 <= ob_digit[i] <= MASK.
   The allocation function takes care of allocating extra memory
   so that ob_digit[0] ... ob_digit[abs(ob_size)-1] are actually available.
   We always allocate memory for at least one digit, so accessing ob_digit[0]
   is always safe. However, in the case ob_size == 0, the contents of
   ob_digit[0] may be undefined.

   CAUTION:  Generic code manipulating subtypes of PyVarObject has to
   aware that ints abuse  ob_size's sign bit.
*/

/*
typedef struct _PyLongValue {
    uintptr_t lv_tag; // Number of digits, sign and flags
    digit ob_digit[1];
} _PyLongValue;

struct _longobject {
    PyObject_HEAD
    _PyLongValue long_value;
};
*/

typedef struct _longobject* py_long;
#if PY_VERSION_HEX >= 0x030C00A5

#define OB_DIGIT(obj) (obj->long_value.ob_digit)
#define NON_SIZE_BITS 3
#define SIGN_MASK 3
#define TAG_FROM_SIGN_AND_SIZE(sign, size) ((1 - (sign)) | ((size) << NON_SIZE_BITS))
inline void
_PyLong_SetSignAndDigitCount(PyLongObject *op, int sign, Py_ssize_t size)
{
    assert(size >= 0);
    assert(-1 <= sign && sign <= 1);
    assert(sign != 0 || size == 0);
    op->long_value.lv_tag = TAG_FROM_SIGN_AND_SIZE(sign, (size_t)size);
}
inline Py_ssize_t
_PyLong_DigitCount(PyLongObject *op)
{
    assert(PyLong_Check(op));
    return op->long_value.lv_tag >> NON_SIZE_BITS;
}
#else

#define OB_DIGIT(o) (o->ob_digit)
inline void
_PyLong_SetSignAndDigitCount(PyLongObject *op, int sign, Py_ssize_t size)
{
    assert(size >= 0);
    assert(-1 <= sign && sign <= 1);
    assert(sign != 0 || size == 0);
    if (sign >= 0) {
	Py_SET_SIZE(op, size);
    } else {
	Py_SET_SIZE(op, -size);
    }
}
inline Py_ssize_t
_PyLong_DigitCount(PyLongObject *op)
{
    assert(PyLong_Check(op));
    return Py_SIZE(op);
}

/*
inline Py_ssize_t
_PyLong_Sign(const PyLongObject *op) {
    Py_ssize_t size = Py_SIZE(x);
    if (size == 0) {
        return 0;
    } else if (size > 0) {
	return 1;
    } else {
	return -1;
    }
}
*/
#endif

#if defined(_WIN32) || defined(WIN32) || defined(MS_WINDOWS)
int LONG_MAX = 2147483647
int LONG_MIN = -2147483648
#else
#include <limits.h>
#endif
