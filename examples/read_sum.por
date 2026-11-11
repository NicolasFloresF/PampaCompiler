programa {
  // reads how many numbers to add, then each number, and prints their sum
  funcao inicio() {
    inteiro count
    inteiro number
    inteiro total = 0
    inteiro i
    escreva("How many numbers? ")
    leia(count)
    para (i = 1; i <= count; i++) {
      escreva("Number ", i, ": ")
      leia(number)
      total = total + number
    }
    escreva("Sum = ", total, "\n")
  }
}
