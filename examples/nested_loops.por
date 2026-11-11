programa {
  funcao inicio() {
    inteiro pairs = 0
    inteiro i
    inteiro j
    para (i = 0; i < 10; i++) {
      para (j = 0; j < 10; j++) {
        se (i < j) {
          pairs++
        }
      }
    }
    retorne pairs
  }
}
