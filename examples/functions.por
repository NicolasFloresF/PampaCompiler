programa {
  // returns 3 * 3 + 4 * 4 = 25, or 0 if that sum were even
  funcao inicio() {
    inteiro a = 3
    inteiro b = 4
    inteiro total = sum(square(a), square(b))
    se (is_even(total)) {
      retorne 0
    }
    retorne total
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
