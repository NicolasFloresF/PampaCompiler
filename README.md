# 🔍 PampaCompiler

**Autores:** Eduardo Carvalho, Guilherme Bragaia e Nicolas Flores  
**Disciplina:** Compiladores — Ciência da Computação, UNIPAMPA  
**Orientador:** Prof. Claudio Schepke  
**Ano:** 2025

---

## 📘 Descrição

Este projeto é um **analisador léxico e sintático completo chamado PampaCompiler** desenvolvido em Python, utilizando a biblioteca [`PLY`](https://www.dabeaz.com/ply/) (Python Lex-Yacc). Seu objetivo é processar arquivos de entrada com base em uma gramática definida, reconhecendo tokens e estruturas sintáticas, além de realizar análise de estruturas e regras mais complexas da linguagem.

Faz parte das atividades práticas da disciplina de **Compiladores**, no curso de Ciência da Computação da **Universidade Federal do Pampa (UNIPAMPA)**.

---

## 📁 Estrutura do Projeto

| Arquivo         | Função                                                                 |
|-----------------|------------------------------------------------------------------------|
| `__main__.py`   | Ponto de entrada do analisador.                                         |
| `tokens.py`     | Definição dos tokens e expressões regulares.                           |
| `grammar.py`    | Regras gramaticais para análise sintática.                             |
| `ex1.por`       | Arquivo de exemplo com código em pseudolinguagem.                      |
| `Readme.txt`    | Anotações e informações complementares do projeto.                     |
| `.gitignore`    | Arquivos/diretórios ignorados pelo Git.                                |
| `pyproject.toml`| Arquivo de configuração do Poetry.                                     |

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

Para rodar o analisador com um arquivo de exemplo:

```bash
python __main__.py ex1.por
```

O analisador irá processar `ex1.por`, reconhecer os tokens válidos, aplicar a gramática definida e exibir os resultados no console.

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
