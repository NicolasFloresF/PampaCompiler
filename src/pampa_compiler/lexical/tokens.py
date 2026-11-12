import sys

import ply.lex as lex

# lexic analysis for the language portugol

# reserved words
reserved = {
    "se": "IF",
    "senao": "ELSE",
    "enquanto": "WHILE",
    "para": "FOR",
    "faca": "DO",
    "escreva": "PRINT",
    "leia": "READ",
    "inteiro": "INTEGER",
    "real": "FLOAT",
    "caracter": "CHAR",
    "cadeia": "STRING_TYPE",
    "logico": "BOOLEAN",
    "verdadeiro": "TRUE",
    "falso": "FALSE",
    "retorne": "RETURN",
    "funcao": "FUNCTION",
    "vazio": "VOID",
    "programa": "PROGRAM",
    "retorne": "RETURN",
    "e": "AND",
    "ou": "OR",
    "nao": "NOT",
}

relational_operators = [
    "ATTRIBUTION",
    "EQUAL",
    "DIFFERENT",
    "LESS_THAN",
    "LESS_EQUAL",
    "GREATER_THAN",
    "GREATER_EQUAL",
]

operations = [
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "INCREMENT",
    "DECREMENT",
]

literal = [
    "STRING",
    "CHAR_LITERAL",
    "COMMENT",
]

# tokens
tokens = (
    [
        "NUMBER",
        "ID",
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "LBRACE",
        "RBRACE",
        "COMMA",
        "SEMICOLON",
    ]
    + operations
    + relational_operators
    + literal
    + list(reserved.values())
)

t_EQUAL = r"\=="
t_DIFFERENT = r"\!="
t_LESS_EQUAL = r"\<="
t_GREATER_EQUAL = r"\>="
t_GREATER_THAN = r"\>"
t_LESS_THAN = r"\<"
t_ATTRIBUTION = r"\="
t_PLUS = r"\+"
t_MINUS = r"\-"
t_TIMES = r"\*"
t_DIVIDE = r"\/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_COMMA = r"\,"
t_SEMICOLON = r"\;"
t_INCREMENT = r"\+\+"
t_DECREMENT = r"\-\-"


t_ignore = " \t"


def t_NUMBER(t):
    # digit = \d+
    # decimal = [.]digit
    # exponent = E[+-]digit
    # number = digit | digit decimal | digit exponent | digit decimal exponent
    # leaving the sign out: '-' and '+' are operators, so 'x-1' is a subtraction
    r"\d+([.]\d+)?([E]([+]|[-])?\d+)?"
    try:
        t.value = int(t.value)
    except ValueError:
        t.value = float(t.value)
    return t


def t_STRING(t):
    # ending at the first quote that is not escaped, so several strings can share a line
    r'"([^"\\\n]|\\.)*"'
    t.type = "STRING"
    return t


# character each escape sequence stands for, as Portugol Studio accepts them
CHAR_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "'": "'", '"': '"', "\\": "\\"}


def t_CHAR_LITERAL(t):
    r"'([^'\\\n]|\\.)'"
    text = t.value[1:-1]
    if text.startswith("\\"):
        if text[1] not in CHAR_ESCAPES:
            print(f"[Line {t.lexer.lineno}]: Invalid escape sequence {text} in a caracter")
            sys.exit(1)
        text = CHAR_ESCAPES[text[1]]
    # keeping the character code, which prints safely in the assembly comments even for '\\n'
    t.value = ord(text)
    return t


def t_COMMENT(t):
    r"//.*|/\*(.|\n)*?\*/"
    # discarding the comment (PLY drops tokens whose rule returns nothing), but counting the lines a block comment spans
    t.lexer.lineno += t.value.count("\n")


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"[Line {t.lexer.lineno}]: Illegal character {t.value[0]}")
    # stopping at the first illegal character: skipping it would compile a different program
    sys.exit(1)


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "ID")
    return t
