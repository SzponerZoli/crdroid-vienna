/* Freestanding AArch64 wrapper: send stdout/stderr to /tmp/rerr.log, then exec
 * the real recovery so dynamic-linker errors are captured. Raw syscalls only. */
typedef unsigned long u64;
static long sc3(long n, long a, long b, long c) {
    register long x8 __asm__("x8") = n, x0 __asm__("x0") = a, x1 __asm__("x1") = b, x2 __asm__("x2") = c;
    __asm__ volatile("svc #0" : "+r"(x0) : "r"(x8), "r"(x1), "r"(x2) : "memory");
    return x0;
}
static long sc4(long n, long a, long b, long c, long d) {
    register long x8 __asm__("x8") = n, x0 __asm__("x0") = a, x1 __asm__("x1") = b, x2 __asm__("x2") = c, x3 __asm__("x3") = d;
    __asm__ volatile("svc #0" : "+r"(x0) : "r"(x8), "r"(x1), "r"(x2), "r"(x3) : "memory");
    return x0;
}
#define SYS_dup3 24
#define SYS_openat 56
#define SYS_write 64
#define SYS_exit 93
#define SYS_execve 221
static const char banner[] = "rwrap: exec /system/bin/recovery.real\n";
__attribute__((noreturn, used)) void cstart(long *sp) {
    long argc = sp[0];
    char **argv = (char **)(sp + 1);
    char **envp = argv + argc + 1;
    /* O_WRONLY|O_CREAT|O_APPEND|O_CLOEXEC off: 01|0100|02000 */
    long fd = sc4(SYS_openat, -100, (long)"/tmp/rerr.log", 01 | 0100 | 02000, 0644);
    if (fd >= 0) {
        sc3(SYS_dup3, fd, 1, 0);
        sc3(SYS_dup3, fd, 2, 0);
    }
    sc3(SYS_write, 2, (long)banner, sizeof(banner) - 1);
    argv[0] = "/system/bin/recovery.real";
    long r = sc3(SYS_execve, (long)"/system/bin/recovery.real", (long)argv, (long)envp);
    static const char fail[] = "rwrap: execve failed\n";
    sc3(SYS_write, 2, (long)fail, sizeof(fail) - 1);
    (void)r;
    sc3(SYS_exit, 127, 0, 0);
    __builtin_unreachable();
}
__asm__(".global _start\n_start:\n mov x0, sp\n bl cstart\n");
