programa {
  funcao inicio() {
    inteiro a = 3
    inteiro b = 7
    inteiro hits = 0
    logico inside = falso
    se ((a < 5) && (b > 5)) {
      inside = verdadeiro
    }
    se (inside) {
      hits++
    }
    se ((a == b) || (b > a)) {
      hits++
    }
    se ((a > b) || (b < a)) {
      hits++
    }
    retorne hits
  }
}
