programa {
  // shows every type: cadeia, caracter, inteiro, real and logico, joined into one text
  funcao inicio() {
    cadeia name = "Ana"
    caracter initial = 'A'
    inteiro age = 20
    real height = 1.75
    logico student = verdadeiro
    escreva(name + " (" + initial + "), " + age + " years, " + height + " m, student: " + student + "\n")
    escreva("Average of 7 and 8.5: ", average(7, 8.5), "\n")
  }

  funcao real average(inteiro a, real b) {
    retorne (a + b) / 2
  }
}
