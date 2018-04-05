/*
 The 64 bit version of Pari contains this amazing statement in parigen.h:
 #define long long long
 Needless to say, this wreaks havoc with any C program on a 64 bit
 Windows system which links with libpari, since a long is always 32
 bits on Windows.
*/ 
#undef long

/* And some key macros need to be redefined if longs are longs. */
#if defined(MS_WIN64)
 #undef signe
 #define signe(x)      (((long long)((x)[1])) >> SIGNSHIFT)
 #undef evalsigne
 #define evalsigne(x)  (((unsigned long long)(x)) << SIGNSHIFT)
#endif

