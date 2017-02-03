from .gen import gen as pari_gen, pari, PariError
# These should be sufficient for most people.
__all__ = ['pari_gen', 'pari', 'PariError']
# But these might come in handy for tinkerers.
from .gen import (prec_words_to_dec, prec_words_to_bits, prec_bits_to_dec, prec_dec_to_bits)


