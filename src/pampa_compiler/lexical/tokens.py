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
    "logico": "BOOLEAN",
    "verdadeiro": "TRUE",
    "falso": "FALSE",
    "retorne": "RETURN",
    "funcao": "FUNCTION",
    "vazio": "VOID",
    "programa": "PROGRAM",
    "retorne": "RETURN",
}

relational_operators = [
    "ATTRIBUTION",
    "AND",
    "OR",
    "NOT",
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
t_AND = r"\&&"
t_OR = r"\|\|"
t_NOT = r"\!"
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
    r"([-]|[+])?\d+([.]\d+)?([E]([+]|[-])?\d+)?"
    try:
        t.value = int(t.value)
    except ValueError:
        t.value = float(t.value)
    return t


def t_STRING(t):
    r'".*"'
    t.type = "STRING"
    return t


def t_COMMENT(t):
    r"//.*"
    t.type = "COMMENT"
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Illegal character {t.value[0]}")
    t.lexer.skip(1)


def t_ID(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "ID")
    return t
