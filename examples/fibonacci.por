programa {
  // prints the Fibonacci numbers from the 0th to the 10th
  funcao inicio() {
    inteiro i
    para (i = 0; i <= 10; i++) {
      escreva(fibonacci(i), " ")
    }
    escreva("\n")
  }

  funcao inteiro fibonacci(inteiro n) {
    se (n < 2) {
      retorne n
    }
    retorne fibonacci(n - 1) + fibonacci(n - 2)
  }
}
