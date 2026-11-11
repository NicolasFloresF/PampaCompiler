# Minimal runtime linked with the compiled programs by the tests, while the
# compiler does not emit its own entry point.

    .text
    .global _start
_start:
    # calling inicio and exiting with its return value as the process exit status
    call inicio
    mov %rax, %rdi
    mov $60, %rax
    syscall

    # ignoring escreva: the compiler passes integers and string addresses the
    # same way, so this routine cannot tell which one it received
    .global syscall_print
syscall_print:
    ret
