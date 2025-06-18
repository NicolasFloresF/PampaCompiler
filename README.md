# 🧾 PampaCompiler

**Autores:** Eduardo Carvalho, Guilherme Bragaia e Nicolas Flores  
**Disciplina:** Compiladores — Ciência da Computação, UNIPAMPA  
**Orientador:** Prof. Claudio Schepke  
**Ano:** 2025

---

## 📘 Descrição

**PampaCompiler** é um **compilador educacional** desenvolvido em Python, com suporte à linguagem **Portugol**.  
Ele realiza **análise léxica** e **análise sintática** utilizando a biblioteca [`PLY`](https://www.dabeaz.com/ply/), processando código-fonte em Portugol e identificando estruturas válidas conforme uma gramática definida.

Esse projeto foi criado como parte da disciplina de **Compiladores**, no curso de Ciência da Computação da **Universidade Federal do Pampa (UNIPAMPA)**, com foco em ensino e experimentação de conceitos fundamentais de compiladores.

---

## 💡 Exemplo de Entrada

Dado um código como:

```portugol
inteiro x;
x := 10;
```

O PampaCompiler:

- Reconhece os tokens: `inteiro`, `x`, `:=`, `10`, `;`
- Valida a estrutura gramatical
- (Opcionalmente: prepara para futuras fases como interpretação ou geração de código)

---

## 📁 Estrutura do Projeto

| Arquivo         | Função                                                                 |
|-----------------|------------------------------------------------------------------------|
| `__main__.py`   | Ponto de entrada do compilador.                                        |
| `tokens.py`     | Definição dos tokens e expressões regulares.                           |
| `grammar.py`    | Regras gramaticais para análise sintática.                             |
| `ex1.por`       | Exemplo de código em Portugol.                                          |
| `Readme.txt`    | Anotações e informações complementares.                                |
| `.gitignore`    | Arquivos/diretórios ignorados pelo Git.                                |
| `pyproject.toml`| Configuração do projeto com o Poetry.                                  |

---

## ⚙️ Requisitos

- Python **3.10+**
- [`Poetry`](https://python-poetry.org/) instalado
- Biblioteca `PLY` (instalada automaticamente via Poetry)

### 📦 Instalação das dependências

```bash
poetry install
```

### 🚪 Acesso ao ambiente virtual

```bash
poetry shell
```

---

## ▶️ Como Executar

Para rodar o compilador com um arquivo de exemplo:

```bash
python __main__.py ex1.por
```

O compilador irá processar `ex1.por`, reconhecer os tokens, aplicar a gramática definida e exibir os resultados no console.

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
