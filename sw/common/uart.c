/* uart.c -- polled UART driver and a small printf.
 * Much smaller than newlib's printf, so programs fit in 16 KB.
 * Supported formats: %c %s %d %u %x %X %p %%, with optional zero padding and
 * width, e.g. %08x.
 */
#include <stdarg.h>
#include <stdint.h>
#include "mmio.h"
#include "uart.h"

int putchar(int c)
{
    if (c == '\n')
        putchar('\r');                    /* terminals expect CR LF */
    while (UART_STATUS & UART_TX_BUSY)
        ;
    UART_TX = (uint32_t)(c & 0xFF);
    return c;
}

int uart_ready(void)
{
    return (UART_STATUS & UART_RX_READY) != 0;
}

int getchar(void)
{
    while (!uart_ready())
        ;
    return (int)(UART_RX & 0xFF);
}

static void put_str(const char *s)
{
    while (*s)
        putchar(*s++);
}

int puts(const char *s)
{
    put_str(s);
    putchar('\n');
    return 0;
}

/* Print an unsigned number in base 10 or 16 with optional width/zero pad. */
static void put_num(uint32_t v, unsigned base, int width, int zero_pad, int upper)
{
    const char *digits = upper ? "0123456789ABCDEF" : "0123456789abcdef";
    char buf[11];
    int n = 0;
    do {
        buf[n++] = digits[v % base];      /* without M, % and / call libgcc's __umodsi3/__udivsi3 */
        v /= base;
    } while (v);
    while (n < width--)
        putchar(zero_pad ? '0' : ' ');
    while (n)
        putchar(buf[--n]);
}

int printf(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    for (; *fmt; fmt++) {
        if (*fmt != '%') {
            putchar(*fmt);
            continue;
        }
        fmt++;
        int zero_pad = 0, width = 0;
        if (*fmt == '0') {
            zero_pad = 1;
            fmt++;
        }
        while (*fmt >= '0' && *fmt <= '9')
            width = width * 10 + (*fmt++ - '0');
        switch (*fmt) {
        case 'c': putchar(va_arg(ap, int)); break;
        case 's': put_str(va_arg(ap, const char *)); break;
        case 'u': put_num(va_arg(ap, uint32_t), 10, width, zero_pad, 0); break;
        case 'x': put_num(va_arg(ap, uint32_t), 16, width, zero_pad, 0); break;
        case 'X': put_num(va_arg(ap, uint32_t), 16, width, zero_pad, 1); break;
        case 'p': put_str("0x"); put_num(va_arg(ap, uint32_t), 16, 8, 1, 0); break;
        case 'd': {
            int32_t v = va_arg(ap, int32_t);
            if (v < 0) {
                putchar('-');
                if (width) width--;
                put_num((uint32_t)(-(v + 1)) + 1u, 10, width, zero_pad, 0);
            } else {
                put_num((uint32_t)v, 10, width, zero_pad, 0);
            }
            break;
        }
        case '%': putchar('%'); break;
        case '\0': fmt--; break;          /* trailing '%' */
        default: putchar('%'); putchar(*fmt); break;
        }
    }
    va_end(ap);
    return 0;
}

int readline(char *buf, int max)
{
    int n = 0;
    for (;;) {
        int c = getchar();
        if (c == '\r' || c == '\n') {
            putchar('\n');
            break;
        }
        if ((c == '\b' || c == 0x7F) && n > 0) {   /* backspace or delete */
            n--;
            put_str("\b \b");
            continue;
        }
        if (c >= ' ' && n < max - 1) {
            buf[n++] = (char)c;
            putchar(c);
        }
    }
    buf[n] = '\0';
    return n;
}
