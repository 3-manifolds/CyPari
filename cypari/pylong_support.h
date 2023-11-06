#include "Python.h"

/*
 * The Python3 struct _longobject is on a trajectory to become an
 * opaque type.  Part of this move towards opacity was begun in the
 * release of Python 3.12.  However, efficient conversion from a
 * Pari GEN to a Python int requires access to the array of digits
 * within the _longobject and an understanding of how those digits
 * are formatted. (Currently they are base 2^30 digits, each being
 * stored in a 32 bit int.) Functions defined in this file are copied
 * from internal Python code, and depend on the Python version.
 * Note that the code below calls the function Py_SET_SIZE which
 * was introduced in Python 3.9.
 */

/*
 * Prior to Python 3.12 the ob_size field in in the HEAD of the
 * struct _longobject was used to store the number of digits and
 * the sign of the integer.  A negative size indicated a negative
 * integer and the number of digits was equal to the abolute value
 * of ob_size.
 *
 * struct _longobject {
 *    PyObject_VAR_HEAD
 *    digit ob_digit[1];
 * };
 *
 * Starting with Python 3.12 the sign and the number of digits
 * were encoded in a separate field, along with some other
 * information about the integer.
 *
 * typedef struct _PyLongValue {
 *     uintptr_t lv_tag; // Number of digits, sign and flags
 *     digit ob_digit[1];
 * } _PyLongValue;
 *
 * struct _longobject {
 *     PyObject_HEAD
 *    _PyLongValue long_value;
 * };
 *
 * See longintrepr.h for more details.
 */

#if PY_MINOR_VERSION < 9

static inline void _Py_SET_SIZE(PyVarObject *ob, Py_ssize_t size) {
    ob->ob_size = size;
}
#define Py_SET_SIZE(ob, size) _Py_SET_SIZE(_PyVarObject_CAST(ob), size)

#endif

typedef struct _longobject* py_long;

inline Py_ssize_t CyPari_Sign(PyObject *op) {
    return _PyLong_Sign(op);
}

#if PY_VERSION_HEX >= 0x030C00A5

#define OB_DIGIT(obj) (obj->long_value.ob_digit)
#define NON_SIZE_BITS 3
#define SIGN_MASK 3
#define TAG_FROM_SIGN_AND_SIZE(sign, size) ((1 - (sign)) | ((size) << NON_SIZE_BITS))
inline void
CyPari_SetSignAndDigitCount(PyLongObject *op, int sign, Py_ssize_t size)
{
    assert(size >= 0);
    assert(-1 <= sign && sign <= 1);
    assert(sign != 0 || size == 0);
    op->long_value.lv_tag = TAG_FROM_SIGN_AND_SIZE(sign, (size_t)size);
}
inline Py_ssize_t
CyPari_DigitCount(PyLongObject *op)
{
    assert(PyLong_Check(op));
    return op->long_value.lv_tag >> NON_SIZE_BITS;
}
#else

#define OB_DIGIT(o) (o->ob_digit)
inline void
CyPari_SetSignAndDigitCount(PyLongObject *op, int sign, Py_ssize_t size)
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
CyPari_DigitCount(PyLongObject *op)
{
    assert(PyLong_Check(op));
    return labs(Py_SIZE(op));
}
#endif

/*
 * In Windows longs are 32 bits.
 */

#if defined(_WIN32) || defined(WIN32) || defined(MS_WINDOWS)
#define LONG_MAX 2147483647L
#define LONG_MIN -2147483648L
#else
#include <limits.h>
#endif
