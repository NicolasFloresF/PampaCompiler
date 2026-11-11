programa {
  funcao inicio() {
    inteiro score = 75
    inteiro level
    se (score >= 90) {
      level = 3
    }
    senao {
      se (score >= 70) {
        level = 2
      }
      senao {
        level = 1
      }
    }
    escreva("Score ", score, " is level ", level, "\n")
  }
}
