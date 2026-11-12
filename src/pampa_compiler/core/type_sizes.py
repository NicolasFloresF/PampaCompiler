"""Holds the size in bytes of a value of each type, shared by the stack layout and the code generator."""

# 'inteiro' has 32 bits, like the int of Java that Portugol Studio runs on;
# 'caracter' holds the address of a string literal
TYPE_SIZES = {
    "inteiro": 4,
    "real": 8,
    "logico": 1,
    "caracter": 8,
}
