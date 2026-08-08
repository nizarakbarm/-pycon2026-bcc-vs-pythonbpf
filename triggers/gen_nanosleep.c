#define _GNU_SOURCE
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    long n = argc > 1 ? 0 : 10000000;
    if (argc > 1) { char *s = argv[1]; while (*s) n = n*10 + (*s++ - '0'); }
    struct timespec ts = {0, 1}; // 1ns
    for (long i = 0; i < n; i++) nanosleep(&ts, NULL);
    return 0;
}