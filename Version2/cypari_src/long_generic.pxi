ctypedef long pari_longword
ctypedef unsigned long pari_ulongword
cdef pari_ulongword pos_max = <pari_ulongword>LONG_MAX
cdef pari_ulongword neg_max = -(<pari_ulongword>LONG_MIN + 1) + 1
cdef pari_longword_to_int(pari_longword x):
    return int(x)
