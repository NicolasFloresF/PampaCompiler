programa {
  funcao inicio() {
    inteiro a = 3
    inteiro b = 7
    inteiro hits = 0
    logico inside = falso
    se ((a < 5) e (b > 5)) {
      inside = verdadeiro
    }
    se (inside) {
      hits++
    }
    se ((a == b) ou (b > a)) {
      hits++
    }
    se ((a > b) ou (b < a)) {
      hits++
    }
    escreva("inside = ", inside, "\n")
    escreva("hits = ", hits, "\n")
  }
}
