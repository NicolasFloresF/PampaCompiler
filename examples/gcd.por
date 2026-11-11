programa {
  funcao inicio() {
    inteiro a = 48
    inteiro b = 18
    enquanto (a != b) {
      se (a > b) {
        a = a - b
      }
      senao {
        b = b - a
      }
    }
    retorne a
  }
}
