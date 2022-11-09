# distutils: libraries = gmp pari
"""
Declarations for private functions from PARI

Ideally, we shouldn't use these, but for technical reasons, we have to.
"""

from .types cimport *

cdef extern from "pari/paripriv.h":
    int t_FF_FpXQ, t_FF_Flxq, t_FF_F2xq

    int gpd_QUIET, gpd_TEST, gpd_EMACS, gpd_TEXMACS

    struct pariout_t:
        char format  # e,f,g
        long fieldw  # 0 (ignored) or field width
        long sigd    # -1 (all) or number of significant digits printed
        int sp       # 0 = suppress whitespace from output
        int prettyp  # output style: raw, prettyprint, etc
        int TeXstyle

    struct gp_data:
        pariout_t *fmt
        unsigned long flags
        unsigned long primelimit

cdef extern from *:
    """
    /* C code which Cython inserts verbatim into _pari.c.  This provides
     * access to literals which are defined in pari header files.
     */
    static gp_data *pari_GP_DATA = GP_DATA;
    """
    gp_data* pari_GP_DATA

cdef extern from "pari/paridecl.h":
    char* closure_func_err()

cdef extern from "long_hack.h":
    pass
