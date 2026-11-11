programa {
  funcao inicio() {
    inteiro count = 0
    inteiro n
    inteiro d
    logico prime
    para (n = 2; n < 30; n++) {
      prime = verdadeiro
      para (d = 2; d * d <= n; d++) {
        se (n - n / d * d == 0) {
          prime = falso
        }
      }
      se (prime) {
        count++
      }
    }
    retorne count
  }
}
