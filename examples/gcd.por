programa {
  funcao inicio() {
    inteiro a = 48
    inteiro b = 18
    escreva("gcd(", a, ", ", b, ") = ")
    enquanto (a != b) {
      se (a > b) {
        a = a - b
      }
      senao {
        b = b - a
      }
    }
    escreva(a, "\n")
  }
}
