#ifndef PARI_ERRORS_H
#define PARI_ERRORS_H

/* global flag set whenever setjmp is called */
int setjmp_active;

/* global variable which holds the current pari error number */
int pari_error_number;

/* counter to check whether our sig-ons balance our sig-offs. */
int sig_on_sig_off;
 
/* declarations of PARI's error callbacks */
void (*cb_pari_ask_confirm)(const char *);
int  (*cb_pari_handle_exception)(long);
int  (*cb_pari_whatnow)(PariOUT *out, const char *, int);
void (*cb_pari_sigint)(void);
void (*cb_pari_err_recover)(long);

/* Declaraton of PARI's error handler */
void pari_err(int numerr, ...);

/* Declaration of our signal setter */
#ifdef __cplusplus
extern "C" {
#endif
void set_pari_signals(void);

/* A flag we can check to see if an interrupt occured */
int interrupt_flag = 0;

/* A message for pari_err */
const char *interrupt_msg = "user interrupt\n";

void set_error_handler( int (*handler)(long) ) {
  cb_pari_handle_exception = handler;
}

void set_error_recoverer( void (*recoverer)(long) ) {
  cb_pari_err_recover = recoverer;
}

void set_sigint_handler(void (*handler)(void)) {
  cb_pari_sigint = handler;
}

#ifdef __cplusplus
}
#endif

#ifdef __MINGW32__

#define SIG_ON_MACRO() {			\
    setjmp_active = 1;				\
    if ( setjmp(jmp_env) ) {			\
      return NULL;				\
    }						\
  }						\

#else

#define SIG_ON_MACRO() {			\
    set_pari_signals();				\
    setjmp_active = 1;				\
    if ( setjmp(jmp_env) ) {			\
      return NULL;				\
    }						\
  }						\

#endif

#endif
