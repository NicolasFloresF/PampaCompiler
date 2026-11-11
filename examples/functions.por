programa {
  // prints 3 * 3 + 4 * 4 and whether it is even
  funcao inicio() {
    inteiro a = 3
    inteiro b = 4
    inteiro total = sum(square(a), square(b))
    escreva(a, " * ", a, " + ", b, " * ", b, " = ", total, "\n")
    se (is_even(total)) {
      escreva(total, " is even\n")
    }
    senao {
      escreva(total, " is odd\n")
    }
  }

  funcao inteiro square(inteiro x) {
    retorne x * x
  }

  funcao inteiro sum(inteiro x, inteiro y) {
    retorne x + y
  }

  /* there is no modulo operator:
     x is even when x - (x / 2) * 2 is zero */
  funcao logico is_even(inteiro x) {
    retorne x - x / 2 * 2 == 0
  }
}
