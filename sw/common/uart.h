/* uart.h -- polled UART I/O and a small printf for the RV32I soft core. */
#ifndef UART_H
#define UART_H

int  putchar(int c);              /* blocks while the transmitter is busy */
int  getchar(void);               /* blocks until a byte arrives */
int  uart_ready(void);            /* 1 if a received byte is waiting */
int  puts(const char *s);         /* string + newline */
int  printf(const char *fmt, ...);/* supports %c %s %d %u %x %08x %% */
int  readline(char *buf, int max);/* reads a line with echo and backspace */

#endif
