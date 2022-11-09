# -*- coding: utf-8 -*-
r"""
Conversion functions for bytes/unicode
"""

import sys
encoding = sys.getfilesystemencoding()

cpdef bytes to_bytes(s):
    """
    Converts bytes and unicode ``s`` to bytes.

    Examples:

    >>> from cypari import to_bytes
    >>> s1 = to_bytes(b'hello')
    >>> s2 = to_bytes('hello')
    >>> s3 = to_bytes(u'hello')
    >>> type(s1) is type(s2) is type(s3) is bytes
    True
    >>> s1 == s2 == s3 == b'hello'
    True

    >>> type(to_bytes(1234)) is bytes
    True
    >>> int(to_bytes(1234))
    1234
    """
    cdef int convert
    for convert in range(2):
        if convert:
            s = str(s)
        if isinstance(s, bytes):
            return <bytes> s
        elif isinstance(s, str):
            return (<str> s).encode(encoding)
    raise AssertionError(f"str() returned {type(s)}")


cpdef str to_string(s):
    r"""
    Converts bytes and unicode ``s`` to unicode.

    Examples:

    >>> from cypari import to_string
    >>> s1 = to_string(b'hello')
    >>> s2 = to_string('hello')
    >>> s3 = to_string(u'hello')
    >>> type(s1) is type(s2) is type(s3) is type(u"")
    True
    >>> s1 == s2 == s3 == u'hello'
    True

    >>> print(to_string(1234))
    1234
    >>> type(to_string(1234)) is type(u"")
    True
    """
    if isinstance(s, bytes):
        return (<bytes> s).decode(encoding)
    elif isinstance(s, str):
        return <str> s
    return str(s)
