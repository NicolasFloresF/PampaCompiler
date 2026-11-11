programa {
  // returns the 10th Fibonacci number, 55
  funcao inicio() {
    retorne fibonacci(10)
  }

  funcao inteiro fibonacci(inteiro n) {
    se (n < 2) {
      retorne n
    }
    retorne fibonacci(n - 1) + fibonacci(n - 2)
  }
}
