
# Runtime appended to every compiled program: the entry point and the routines
# behind escreva and leia, using Linux system calls only. Routine names start
# with pampa_ so they do not clash with the functions of the program.

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
    call pampa_text_length
    mov %rdi, %rsi
    mov %rax, %rdx
    jmp pampa_write

# Returns in %rax the length of the zero-terminated string at %rdi.
pampa_text_length:
    xor %rax, %rax
pampa_text_length_next:
    cmpb $0, (%rdi,%rax)
    je pampa_text_length_end
    inc %rax
    jmp pampa_text_length_next
pampa_text_length_end:
    ret

# Writes the decimal digits of the signed integer %rdi backwards, ending just before the
# address %rsi, and returns in %rax the address of the first character (at most 20 bytes).
pampa_format_int:
    mov %rdi, %rax
    mov $10, %rcx
    xor %r8, %r8                    # %r8 = 1 when the number is negative
    test %rax, %rax
    jns pampa_format_int_digit
    neg %rax
    mov $1, %r8
pampa_format_int_digit:
    xor %rdx, %rdx
    div %rcx                        # unsigned, so the most negative number still comes out right
    add $48, %dl                    # '0'
    dec %rsi
    mov %dl, (%rsi)
    test %rax, %rax
    jnz pampa_format_int_digit
    test %r8, %r8
    jz pampa_format_int_end
    dec %rsi
    movb $45, (%rsi)                # '-'
pampa_format_int_end:
    mov %rsi, %rax
    ret

# Writes the signed integer in %rdi in decimal.
pampa_print_int:
    push %rbp
    mov %rsp, %rbp
    sub $32, %rsp
    mov %rbp, %rsi                  # the digits end where the frame ends
    call pampa_format_int
    mov %rax, %rsi
    mov %rbp, %rdx
    sub %rsi, %rdx                  # length: from the first character to the end of the frame
    call pampa_write
    leave
    ret

# Returns in %rax a new zero-terminated string with the decimal digits of %rdi.
pampa_int_to_text:
    push %rdi
    mov $24, %rdi
    call pampa_alloc
    pop %rdi
    lea 23(%rax), %rsi
    movb $0, (%rsi)
    call pampa_format_int
    ret

# Returns in %rax the address of "verdadeiro" when %rdi is not zero, of "falso" otherwise.
pampa_bool_to_text:
    lea pampa_true(%rip), %rax
    test %rdi, %rdi
    jnz pampa_bool_to_text_end
    lea pampa_false(%rip), %rax
pampa_bool_to_text_end:
    ret

# Writes "verdadeiro" when %rdi is not zero, "falso" otherwise.
pampa_print_bool:
    call pampa_bool_to_text
    mov %rax, %rdi
    jmp pampa_print_string

# Returns in %rax the address of %rdi new bytes from the heap, which grows with the brk system
# call and is never freed; consecutive calls return consecutive addresses. Changes %rdi.
pampa_alloc:
    mov pampa_heap_top(%rip), %rax
    test %rax, %rax
    jnz pampa_alloc_reserve
    push %rdi
    mov $12, %rax                   # brk
    xor %rdi, %rdi                  # 0: asking for the current end of the data segment
    syscall
    pop %rdi
    mov %rax, pampa_heap_top(%rip)
    mov %rax, pampa_heap_end(%rip)
pampa_alloc_reserve:
    lea (%rax,%rdi), %r8            # %r8 = top of the heap after this allocation
    cmp pampa_heap_end(%rip), %r8
    jbe pampa_alloc_done
    push %rax
    push %r8
    lea 65536(%r8), %rdi            # growing 64 KiB past what is needed
    mov $12, %rax                   # brk
    syscall
    pop %r8
    cmp %r8, %rax
    jb pampa_alloc_failed           # the kernel keeps the old end when it cannot grow
    mov %rax, pampa_heap_end(%rip)
    pop %rax
pampa_alloc_done:
    mov %r8, pampa_heap_top(%rip)
    ret
pampa_alloc_failed:
    mov $1, %rax                    # write
    mov $2, %rdi                    # standard error
    lea pampa_no_memory(%rip), %rsi
    mov $pampa_no_memory_length, %rdx
    syscall
    mov $60, %rax                   # exit
    mov $1, %rdi
    syscall

# Returns in %rax a new zero-terminated string with the string at %rdi followed by the one at %rsi.
pampa_concat:
    push %rbp
    mov %rsp, %rbp
    sub $32, %rsp
    mov %rdi, -8(%rbp)              # first string
    mov %rsi, -16(%rbp)             # second string
    call pampa_text_length
    mov %rax, -24(%rbp)             # length of the first
    mov -16(%rbp), %rdi
    call pampa_text_length
    mov %rax, -32(%rbp)             # length of the second
    lea 1(%rax), %rdi
    add -24(%rbp), %rdi
    call pampa_alloc
    mov %rax, %rdi                  # copying the first string, then the second with its zero
    mov %rax, %r8
    mov -8(%rbp), %rsi
    mov -24(%rbp), %rcx
    rep movsb
    mov -16(%rbp), %rsi
    mov -32(%rbp), %rcx
    inc %rcx
    rep movsb
    mov %r8, %rax
    leave
    ret

# Returns 1 in %rax when the zero-terminated strings at %rdi and %rsi are equal, 0 otherwise.
pampa_text_equal:
    xor %rcx, %rcx
pampa_text_equal_next:
    movb (%rdi,%rcx), %al
    cmpb (%rsi,%rcx), %al
    jne pampa_text_equal_different
    test %al, %al
    jz pampa_text_equal_same
    inc %rcx
    jmp pampa_text_equal_next
pampa_text_equal_same:
    mov $1, %rax
    ret
pampa_text_equal_different:
    xor %rax, %rax
    ret

# Reads one line from the standard input and returns in %rax a new zero-terminated string with
# it, without the '\n' and ignoring '\r'; the end of the input also ends the line.
pampa_read_string:
    push %rbp
    mov %rsp, %rbp
    sub $16, %rsp
    xor %rdi, %rdi
    call pampa_alloc                # 0 bytes: the address where the string starts
    mov %rax, -16(%rbp)
pampa_read_string_next:
    mov $0, %rax                    # read
    mov $0, %rdi                    # standard input
    lea -1(%rbp), %rsi
    mov $1, %rdx
    syscall
    cmp $1, %rax
    jne pampa_read_string_end       # end of the input or error
    movzbq -1(%rbp), %rax
    cmp $10, %rax                   # '\n'
    je pampa_read_string_end
    cmp $13, %rax                   # '\r'
    je pampa_read_string_next
    mov $1, %rdi
    call pampa_alloc
    movb -1(%rbp), %cl
    movb %cl, (%rax)
    jmp pampa_read_string_next
pampa_read_string_end:
    mov $1, %rdi
    call pampa_alloc
    movb $0, (%rax)
    mov -16(%rbp), %rax
    leave
    ret

# Reads one line from the standard input and returns it in %rax as a signed
# integer. Reads byte by byte, so the next leia finds the following line;
# skips characters that are not digits; an empty line or the end of the
# input gives 0.
pampa_read_int:
    push %rbp
    mov %rsp, %rbp
    sub $16, %rsp
    xor %r8, %r8                    # %r8 = value read so far
    xor %r9, %r9                    # %r9 = 1 when a '-' was read
pampa_read_int_next:
    mov $0, %rax                    # read
    mov $0, %rdi                    # standard input
    lea -1(%rbp), %rsi
    mov $1, %rdx
    syscall
    cmp $1, %rax
    jne pampa_read_int_done         # end of the input or error
    movzbq -1(%rbp), %rax
    cmp $10, %rax                   # '\n'
    je pampa_read_int_done
    cmp $45, %rax                   # '-'
    jne pampa_read_int_digit
    mov $1, %r9
    jmp pampa_read_int_next
pampa_read_int_digit:
    sub $48, %rax                   # '0'
    cmp $9, %rax
    ja pampa_read_int_next          # not a digit (unsigned compare also catches bytes below '0')
    imul $10, %r8
    add %rax, %r8
    jmp pampa_read_int_next
pampa_read_int_done:
    mov %r8, %rax
    test %r9, %r9
    jz pampa_read_int_end
    neg %rax
pampa_read_int_end:
    leave
    ret

# Reads one line from the standard input and returns 1 for "verdadeiro" and 0
# for "falso" in %rax, ignoring spaces and '\r'. Any other line, or the end of
# the input, stops the program with a message and exit status 1.
pampa_read_bool:
    push %rbp
    mov %rsp, %rbp
    sub $32, %rsp                   # -32(%rbp): up to 16 characters; -1(%rbp): byte being read
    xor %r8, %r8                    # %r8 = characters in the line, ignored ones excluded
pampa_read_bool_next:
    mov $0, %rax                    # read
    mov $0, %rdi                    # standard input
    lea -1(%rbp), %rsi
    mov $1, %rdx
    syscall
    cmp $1, %rax
    jne pampa_read_bool_check       # end of the input or error
    movzbq -1(%rbp), %rax
    cmp $10, %rax                   # '\n'
    je pampa_read_bool_check
    cmp $32, %rax                   # ' '
    je pampa_read_bool_next
    cmp $13, %rax                   # '\r'
    je pampa_read_bool_next
    cmp $16, %r8
    jae pampa_read_bool_count       # too long to be a valid word: only counting
    mov %al, -32(%rbp,%r8)
pampa_read_bool_count:
    inc %r8
    jmp pampa_read_bool_next
pampa_read_bool_check:
    lea -32(%rbp), %rdi
    mov %r8, %rsi
    lea pampa_true(%rip), %rdx
    mov $10, %rcx                   # length of "verdadeiro"
    call pampa_same_text
    test %rax, %rax
    jnz pampa_read_bool_end         # %rax = 1
    lea -32(%rbp), %rdi
    mov %r8, %rsi
    lea pampa_false(%rip), %rdx
    mov $5, %rcx                    # length of "falso"
    call pampa_same_text
    test %rax, %rax
    jz pampa_read_bool_invalid
    xor %rax, %rax                  # 0 for falso
pampa_read_bool_end:
    leave
    ret
pampa_read_bool_invalid:
    mov $1, %rax                    # write
    mov $2, %rdi                    # standard error
    lea pampa_invalid_bool(%rip), %rsi
    mov $pampa_invalid_bool_length, %rdx
    syscall
    mov $60, %rax                   # exit
    mov $1, %rdi
    syscall

# Returns 1 in %rax when the %rsi bytes at %rdi are the %rcx bytes at %rdx, 0 otherwise.
pampa_same_text:
    xor %rax, %rax
    cmp %rcx, %rsi
    jne pampa_same_text_end
pampa_same_text_byte:
    test %rcx, %rcx
    jz pampa_same_text_equal
    dec %rcx
    movb (%rdi,%rcx), %r10b
    cmpb (%rdx,%rcx), %r10b
    jne pampa_same_text_end
    jmp pampa_same_text_byte
pampa_same_text_equal:
    mov $1, %rax
pampa_same_text_end:
    ret

    .section .rodata
pampa_true:
    .string "verdadeiro"
pampa_false:
    .string "falso"
pampa_invalid_bool:
    .ascii "Runtime error: leia expected verdadeiro or falso\n"
    .set pampa_invalid_bool_length, . - pampa_invalid_bool
pampa_no_memory:
    .ascii "Runtime error: out of memory\n"
    .set pampa_no_memory_length, . - pampa_no_memory

    .data
pampa_heap_top:
    .quad 0                         # 0 until the first allocation finds the heap
pampa_heap_end:
    .quad 0
