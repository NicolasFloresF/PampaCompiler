
# Runtime appended to every compiled program: the entry point and the routines
# behind escreva, using Linux system calls only. Routine names start with
# pampa_ so they do not clash with the functions of the program.

    .text
    .global _start
_start:
    # running inicio and exiting with its return value as the process exit status
    call inicio
    mov %rax, %rdi
    mov $60, %rax                   # exit
    syscall

# Writes %rdx bytes starting at %rsi to the standard output.
pampa_write:
    mov $1, %rax                    # write
    mov $1, %rdi                    # standard output
    syscall
    ret

# Writes the zero-terminated string at %rdi.
pampa_print_string:
    mov %rdi, %rsi
    xor %rdx, %rdx
pampa_print_string_length:
    cmpb $0, (%rsi,%rdx)
    je pampa_print_string_write
    inc %rdx
    jmp pampa_print_string_length
pampa_print_string_write:
    call pampa_write
    ret

# Writes the signed integer in %rdi in decimal.
pampa_print_int:
    push %rbp
    mov %rsp, %rbp
    sub $32, %rsp
    mov %rdi, %rax
    lea -1(%rbp), %rsi              # filling the buffer backwards, from its last byte
    mov $10, %rcx
    xor %r8, %r8                    # %r8 = 1 when the number is negative
    test %rax, %rax
    jns pampa_print_int_digit
    neg %rax
    mov $1, %r8
pampa_print_int_digit:
    xor %rdx, %rdx
    div %rcx                        # unsigned, so the most negative number still prints right
    add $48, %dl                    # '0'
    mov %dl, (%rsi)
    dec %rsi
    test %rax, %rax
    jnz pampa_print_int_digit
    test %r8, %r8
    jz pampa_print_int_write
    movb $45, (%rsi)                # '-'
    dec %rsi
pampa_print_int_write:
    inc %rsi                        # first character
    mov %rbp, %rdx
    sub %rsi, %rdx                  # length: from the first character to the end of the buffer
    call pampa_write
    leave
    ret

# Writes "verdadeiro" when %rdi is not zero, "falso" otherwise.
pampa_print_bool:
    test %rdi, %rdi
    jz pampa_print_bool_false
    lea pampa_true(%rip), %rdi
    jmp pampa_print_string
pampa_print_bool_false:
    lea pampa_false(%rip), %rdi
    jmp pampa_print_string

    .section .rodata
pampa_true:
    .string "verdadeiro"
pampa_false:
    .string "falso"
