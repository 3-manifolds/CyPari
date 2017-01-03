/*
 The 64 bit version of Pari contains this amazing statement in parigen.h:
 #define long long long
 Needless to say, this wreaks havoc with any C program on a 64 bit
 Windows system, since long is always a 32-bit int on Windows.
*/ 
#undef long
