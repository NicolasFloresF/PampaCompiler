# 🧾 PampaCompiler

**Autores:** Eduardo Carvalho, Guilherme Bragaia e Nicolas Flores  
**Disciplina:** Compiladores — Ciência da Computação, UNIPAMPA  
**Orientador:** Prof. Claudio Schepke  
**Ano:** 2025

---

## 📘 Descrição

**PampaCompiler** é um **compilador educacional** desenvolvido em Python, com suporte a um subconjunto da linguagem **Portugol** (no dialeto do Portugol Studio).  
Ele realiza **análise léxica** e **análise sintática** utilizando a biblioteca [`PLY`](https://www.dabeaz.com/ply/), faz a **análise semântica** (declarações e tipos) e **gera código assembly x86-64** que, montado e ligado, vira um executável Linux independente.

Esse projeto foi criado como parte da disciplina de **Compiladores**, no curso de Ciência da Computação da **Universidade Federal do Pampa (UNIPAMPA)**, com foco em ensino e experimentação de conceitos fundamentais de compiladores.

---

## 🔄 Sobre esta versão

O código deste repositório **não é o mesmo que foi apresentado na disciplina**. Depois da entrega, o projeto foi refatorado e recebeu novas funcionalidades, entre elas:

- Reorganização do código em um pacote, com uma pasta por fase do compilador
- Migração do Poetry para o [`uv`](https://docs.astral.sh/uv/)
- Correção de defeitos: assembly que não montava, falhas do compilador e erros de análise
- Executáveis independentes, com `escreva` e `leia` feitos por chamadas de sistema do Linux
- Funções com tipo de retorno, parâmetros e recursão
- Tipos `cadeia` (com concatenação por `+`), `caracter` (`'a'`) e `real`, além de `inteiro` (32 bits) e `logico`
- Escopo de bloco: cada variável vale do ponto da declaração até o fim do seu bloco
- Comentários `//` e `/* */`
- Operadores lógicos `e`, `ou` e `nao`, com a precedência do Portugol Studio
- Testes automatizados sobre os programas da pasta `examples/`

A versão apresentada continua no histórico do git, marcada com a tag `apresentacao-2025` (commit `a534725`).

---

## 💡 Exemplo de Entrada

Dado um código como:

```portugol
programa {
  funcao inicio() {
    inteiro x = 10
    escreva("x = ", x, "\n")
  }
}
```

O PampaCompiler:

- Reconhece os tokens: `programa`, `funcao`, `inicio`, `inteiro`, `x`, `=`, `10`, `escreva`, ...
- Valida a estrutura gramatical e monta a árvore sintática (AST)
- Verifica declarações e tipos
- Gera o código assembly, que vira um programa que imprime `x = 10`

---

## 📁 Estrutura do Projeto

| Arquivo                                      | Função                                                        |
|----------------------------------------------|---------------------------------------------------------------|
| `src/pampa_compiler/__main__.py`             | Ponto de entrada do compilador.                               |
| `src/pampa_compiler/lexical/`                | Definição dos tokens e expressões regulares.                  |
| `src/pampa_compiler/syntax/`                 | Regras gramaticais para análise sintática.                    |
| `src/pampa_compiler/semantic/`               | Tabelas de símbolos e verificação de declarações e tipos.     |
| `src/pampa_compiler/assembly/`               | Geração do assembly e rotinas de execução (`runtime.s`).      |
| `src/pampa_compiler/core/`                   | Árvore sintática, tabela de símbolos e erros do compilador.   |
| `examples/`                                  | Exemplos de código em Portugol.                               |
| `tests/`                                     | Testes que compilam e executam os exemplos.                   |
| `.gitignore`                                 | Arquivos/diretórios ignorados pelo Git.                       |
| `pyproject.toml`                             | Configuração do projeto com o uv.                             |

---

## ⚙️ Requisitos

- Linux x86-64
- Python **3.12+**
- [`uv`](https://docs.astral.sh/uv/) instalado
- [Graphviz](https://graphviz.org/) (programa `dot`, usado para desenhar a AST)
- GNU binutils (`as` e `ld`, para montar e ligar o assembly gerado)
- Bibliotecas `PLY` e `graphviz` (instaladas automaticamente pelo uv)

### 📦 Instalação das dependências

```bash
uv sync
```

### 🚪 Acesso ao ambiente virtual

Os comandos abaixo usam `uv run`, que já executa dentro do ambiente virtual do projeto. Para ativá-lo manualmente:

```bash
source .venv/bin/activate
```

---

## ▶️ Como Executar

Para compilar um arquivo de exemplo:

```bash
uv run python -m pampa_compiler --file examples/hello_world.por
```

O compilador gera `examples/hello_world.asm` e desenha a AST em `ast.png`. Com a opção `--debug`, ele também grava os tokens, a AST e as tabelas de símbolos em `compile.out`.

Para montar, ligar e executar o programa gerado (na pasta `build/`, ignorada pelo git):

```bash
mkdir -p build
as examples/hello_world.asm -o build/hello_world.o
ld build/hello_world.o -o build/hello_world
./build/hello_world
```

---

## 🧪 Testes

```bash
uv run python -m unittest discover tests
```

Os testes compilam, montam e executam cada programa de `examples/`, conferindo o código de saída e o que o programa imprime.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Para colaborar:

1. Faça um **fork** do projeto.
2. Crie uma nova branch:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça suas alterações e envie um **pull request**.

---

## 📄 Licença

Distribuído sob a **Licença MIT**. Veja o arquivo [`LICENSE`](LICENSE) para mais informações.

---

<div align="center">

🧠 *"Construir um compilador é entender como o pensamento vira máquina."*

</div>
