/* Include the relevant PARI includes in a safe way */
#include <pari/paricfg.h>
#include <pari/pari.h>

#undef coeff  /* Conflicts with NTL */


/* Array element assignment */
#define set_gel(x, n, z)         (gel(x,n) = z)
#define set_gmael(x, i, j, z)    (gmael(x,i,j) = z)
#define set_gcoeff(x, i, j, z)   (gcoeff(x,i,j) = z)


/* These are declared extern in Pari.
 *
 * Since we are statically linking with libpari.a, we DO NOT define
 * them here. (This is a difference from the Sage version.)
 *
 * THREAD VOLATILE int PARI_SIGINT_block;
 * THREAD VOLATILE int PARI_SIGINT_pending;
 */
