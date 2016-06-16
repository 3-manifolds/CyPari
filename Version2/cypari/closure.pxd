include "sage.pxi"
IF SAGE == True:
    from sage.libs.pari.gen cimport gen
ELSE:
    from gen cimport gen
    
cpdef gen objtoclosure(f)
