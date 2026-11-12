"""Moves values between %rax and the stack slots of variables, with the instruction that fits the size of each type."""

from pampa_compiler.core.type_sizes import TYPE_SIZES

# reading a slot into all of %rax: sign-extending 'inteiro', zero-extending the one-byte types
LOAD_INSTRUCTIONS = {1: "movzbq", 4: "movslq", 8: "movq"}

# writing only the low bytes of %rax that fit the slot
STORE_INSTRUCTIONS = {1: ("movb", "%al"), 4: ("movl", "%eax"), 8: ("movq", "%rax")}


def load_variable(variable):
    """Returns the instruction that copies the slot of variable (a symbol) into %rax."""
    instruction = LOAD_INSTRUCTIONS[TYPE_SIZES[variable.type]]
    return f"    {instruction} {variable.offset}(%rbp), %rax\n"


def store_variable(variable):
    """Returns the instruction that copies %rax into the slot of variable (a symbol)."""
    instruction, register = STORE_INSTRUCTIONS[TYPE_SIZES[variable.type]]
    return f"    {instruction} {register}, {variable.offset}(%rbp)\n"
