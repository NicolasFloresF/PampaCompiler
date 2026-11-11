import sys

import ply.yacc as yacc
from pampa_compiler.core.ast_node import ASTnode

# !Remember: expression is a tree node, but commands is not

precedence = (
    ("nonassoc", "EQUAL", "DIFFERENT"),
    ("nonassoc", "LESS_THAN", "LESS_EQUAL", "GREATER_THAN", "GREATER_EQUAL"),
    ("left", "AND", "OR"),
    ("left", "NOT"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "UMINUS"),
)


def p_por_program(p):
    """program : PROGRAM LBRACE function_list RBRACE"""
    children = [
        ASTnode("LBRACE", value=p[2], lineno=p.lineno(2)),
        ASTnode("function_list", p[3], lineno=p.lineno(3)),
        ASTnode("RBRACE", value=p[4], lineno=p.lineno(4)),
    ]
    p[0] = ASTnode("program", children=children, lineno=p.lineno(1))


def p_function_list(p):
    """function_list : function
    | function function_list"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_function(p):
    """function : FUNCTION return_type ID LPAREN RPAREN LBRACE commands RBRACE
    | FUNCTION return_type ID LPAREN param RPAREN LBRACE commands RBRACE"""
    if len(p) == 9:
        children = [
            ASTnode("return_type", value=p[2], lineno=p.lineno(1)),
            ASTnode("identifier", value=p[3], lineno=p.lineno(3)),
            ASTnode("LPAREN", value=p[4], lineno=p.lineno(4)),
            ASTnode("RPAREN", value=p[5], lineno=p.lineno(5)),
            ASTnode("LBRACE", value=p[6], lineno=p.lineno(6)),
            ASTnode("commands", p[7], lineno=p.lineno(7)),
            ASTnode("RBRACE", value=p[8], lineno=p.lineno(8)),
        ]
        p[0] = ASTnode("function", children=children, value=p[3], lineno=p.lineno(3))
    elif len(p) == 10:
        children = [
            ASTnode("return_type", value=p[2], lineno=p.lineno(1)),
            ASTnode("identifier", value=p[3], lineno=p.lineno(3)),
            ASTnode("LPAREN", value=p[4], lineno=p.lineno(4)),
            p[5],
            ASTnode("RPAREN", value=p[6], lineno=p.lineno(6)),
            ASTnode("LBRACE", value=p[7], lineno=p.lineno(7)),
            ASTnode("commands", p[8], lineno=p.lineno(8)),
            ASTnode("RBRACE", value=p[9], lineno=p.lineno(9)),
        ]
        p[0] = ASTnode("function", children=children, value=p[3], lineno=p.lineno(3))


def p_return_type(p):
    """return_type : type
    | VOID
    | empty"""
    # functions declared without a type return nothing, like the 'vazio' ones
    if p[1] is None:
        p[0] = "vazio"
    else:
        p[0] = p[1]


def p_empty(p):
    """empty :"""
    pass


def p_param(p):
    """param : type ID
    | type ID COMMA param"""
    if len(p) == 3:
        children = [
            ASTnode("type", value=p[1], lineno=p.lineno(1)),
            ASTnode("identifier", value=p[2], lineno=p.lineno(2)),
        ]
        p[0] = ASTnode("param", children=children, lineno=p.lineno(1))
    elif len(p) == 5:
        children = [
            ASTnode("type", value=p[1], lineno=p.lineno(1)),
            ASTnode("identifier", value=p[2], lineno=p.lineno(2)),
            ASTnode("COMMA", value=p[3], lineno=p.lineno(3)),
            p[4],
        ]
        p[0] = ASTnode("param", children=children, lineno=p.lineno(1))


def p_commands(p):
    """commands : command
    | command commands"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [p[1]] + p[2]


def p_command(p):
    """command : expression
    | declaration
    | if_statement
    | while_statement
    | for_statement
    | read_statement
    | write_statement"""
    p[0] = p[1]


def p_binary_expression(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression"""
    children = [
        p[1],
        ASTnode("binary_operator", value=p[2], lineno=p.lineno(2)),
        p[3],
    ]
    p[0] = ASTnode("binary_expression", children=children, value=p[2], lineno=p.lineno(2))


def p_expr_uminus(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = ASTnode("unary_expression", [p[2]], p.lineno(1))


def p_logical_expression(p):
    """expression : expression AND expression
    | expression OR expression"""
    children = [
        p[1],
        ASTnode("logical_operator", value=p[2], lineno=p.lineno(2)),
        p[3],
    ]
    p[0] = ASTnode("logical_expression", children=children, value=p[2], lineno=p.lineno(2))


def p_relational_expression(p):
    """expression : expression LESS_THAN expression
    | expression LESS_EQUAL expression
    | expression GREATER_THAN expression
    | expression GREATER_EQUAL expression
    | expression EQUAL expression
    | expression DIFFERENT expression"""
    children = [
        p[1],
        ASTnode("relational_operator", value=p[2], lineno=p.lineno(2)),
        p[3],
    ]
    p[0] = ASTnode("relational_expression", children=children, value=p[2], lineno=p.lineno(2))


def p_assignment_expression(p):
    """expression : ID ATTRIBUTION expression"""
    children = [
        ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
        ASTnode("atribuition", value=p[2], lineno=p.lineno(2)),
        p[3],
    ]
    p[0] = ASTnode("assignment_expression", children=children, value=p[2], lineno=p.lineno(1))


def p_expression_group(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_expression_id(p):
    """expression : ID"""
    p[0] = ASTnode("identifier", value=p[1], lineno=p.lineno(1))


def p_expression_number(p):
    """expression : NUMBER"""
    p[0] = ASTnode("number", value=p[1], lineno=p.lineno(1))


def p_expression_boolean(p):
    """expression : TRUE
    | FALSE"""
    p[0] = ASTnode("boolean", value=p[1], lineno=p.lineno(1))


def p_expression_string(p):
    """expression : STRING"""
    p[0] = ASTnode("string", value=p[1], lineno=p.lineno(1))


def p_increment_expressionb(p):
    """expression : ID INCREMENT
    | ID DECREMENT"""
    children = [
        ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
        ASTnode("increment", value=p[2], lineno=p.lineno(2)),
    ]
    p[0] = ASTnode("increment_expression", children=children, value=p[2], lineno=p.lineno(1))


def p_return_expression(p):
    """expression : RETURN expression"""
    children = [
        ASTnode("RETURN", value=p[1], lineno=p.lineno(1)),
        p[2],
    ]
    p[0] = ASTnode("return_expression", children=children, lineno=p.lineno(1))


def p_call_function_expression(p):
    """expression : ID LPAREN RPAREN
    | ID LPAREN expression_list RPAREN"""
    if len(p) == 4:
        children = [
            ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
            ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
            ASTnode("RPAREN", value=p[3], lineno=p.lineno(3)),
        ]
        p[0] = ASTnode("call_function_expression", children=children, lineno=p.lineno(1))
    else:
        children = [
            ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
            ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
            ASTnode("expression_list", p[3], lineno=p.lineno(3)),
            ASTnode("RPAREN", value=p[4], lineno=p.lineno(4)),
        ]
        p[0] = ASTnode("call_function_expression", children=children, lineno=p.lineno(1))


def p_expression_list(p):
    """expression_list : expression
    | expression COMMA expression_list"""
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]


def p_declaration(p):
    """declaration : type declaration_list"""
    children = [
        ASTnode("type", value=p[1], lineno=p.lineno(1)),
        p[2],
    ]
    p[0] = ASTnode("declaration", children=children, lineno=p.lineno(1))


def p_type(p):
    """type : INTEGER
    | FLOAT
    | STRING
    | BOOLEAN"""
    p[0] = p[1]


def p_declaration_list(p):
    """declaration_list : ID
    | ID COMMA declaration_list
    | ID ATTRIBUTION expression
    | ID ATTRIBUTION expression COMMA declaration_list"""
    if len(p) == 2:
        children = [
            ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
        ]
        p[0] = ASTnode("declarations", children=children, lineno=p.lineno(1))
    elif len(p) == 4 and p[2] == ",":
        children = [
            ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
            ASTnode("COMMA", value=p[2], lineno=p.lineno(2)),
            p[3],
        ]
        p[0] = ASTnode("declarations", children=children, lineno=p.lineno(1))
    elif len(p) == 4 and p[2] == "=":
        children = [
            ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
            ASTnode("atribuition", value=p[2], lineno=p.lineno(2)),
            p[3],
        ]
        p[0] = ASTnode("declarations", children=children, lineno=p.lineno(1))
    elif len(p) == 6:
        children = [
            ASTnode("identifier", value=p[1], lineno=p.lineno(1)),
            ASTnode("atribuition", value=p[2], lineno=p.lineno(2)),
            p[3],
            ASTnode("COMMA", value=p[4], lineno=p.lineno(4)),
            p[5],
        ]
        p[0] = ASTnode("declarations", children=children, lineno=p.lineno(1))


def p_read_statement(p):
    """read_statement : READ LPAREN identifier_list RPAREN"""
    # placing the identifiers between the parentheses, so the variables are children[1:-1]
    children = [
        ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
        *p[3],
        ASTnode("RPAREN", value=p[4], lineno=p.lineno(4)),
    ]
    p[0] = ASTnode("read", children=children, lineno=p.lineno(1))


def p_identifier_list(p):
    """identifier_list : ID
    | ID COMMA identifier_list"""
    if len(p) == 2:
        p[0] = [ASTnode("identifier", value=p[1], lineno=p.lineno(1))]
    elif len(p) == 4:
        p[0] = [ASTnode("identifier", value=p[1], lineno=p.lineno(1))] + p[3]


def p_write_statement(p):
    """write_statement : PRINT LPAREN expression_list RPAREN"""
    children = [
        ASTnode("PRINT", value=p[1], lineno=p.lineno(1)),
        ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
        ASTnode("expression_list", p[3], lineno=p.lineno(3)),
        ASTnode("RPAREN", value=p[4], lineno=p.lineno(4)),
    ]
    p[0] = ASTnode("print", children=children, lineno=p.lineno(1))


def p_if_statement(p):
    """if_statement : IF LPAREN expression RPAREN LBRACE commands RBRACE
    | IF LPAREN expression RPAREN LBRACE commands RBRACE ELSE LBRACE commands RBRACE"""
    if len(p) == 8:
        children = [
            ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
            p[3],
            ASTnode("RPAREN", value=p[4], lineno=p.lineno(4)),
            ASTnode("LBRACE", value=p[5], lineno=p.lineno(5)),
            ASTnode("commands", p[6], lineno=p.lineno(6)),
            ASTnode("RBRACE", value=p[7], lineno=p.lineno(7)),
        ]
        p[0] = ASTnode("if", children=children, lineno=p.lineno(1))
    else:
        children = [
            ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
            p[3],
            ASTnode("RPAREN", value=p[4], lineno=p.lineno(4)),
            ASTnode("LBRACE", value=p[5], lineno=p.lineno(5)),
            ASTnode("commands", p[6], lineno=p.lineno(6)),
            ASTnode("RBRACE", value=p[7], lineno=p.lineno(7)),
            ASTnode("ELSE", value=p[8], lineno=p.lineno(8)),
            ASTnode("LBRACE", value=p[9], lineno=p.lineno(9)),
            ASTnode("commands", p[10], lineno=p.lineno(10)),
            ASTnode("RBRACE", value=p[11], lineno=p.lineno(11)),
        ]
        p[0] = ASTnode("if", children=children, lineno=p.lineno(1))


def p_while_statement(p):
    """while_statement : WHILE LPAREN expression RPAREN LBRACE commands RBRACE"""
    children = [
        ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
        p[3],
        ASTnode("RPAREN", value=p[4], lineno=p.lineno(4)),
        ASTnode("LBRACE", value=p[5], lineno=p.lineno(5)),
        ASTnode("commands", p[6], lineno=p.lineno(6)),
        ASTnode("RBRACE", value=p[7], lineno=p.lineno(7)),
    ]
    p[0] = ASTnode("while", children=children, lineno=p.lineno(1))


def p_for_statement(p):
    """for_statement : FOR LPAREN expression SEMICOLON expression SEMICOLON expression RPAREN LBRACE commands RBRACE"""
    children = [
        ASTnode("LPAREN", value=p[2], lineno=p.lineno(2)),
        p[3],
        ASTnode("SEMICOLON", value=p[4], lineno=p.lineno(4)),
        p[5],
        ASTnode("SEMICOLON", value=p[6], lineno=p.lineno(6)),
        p[7],
        ASTnode("RPAREN", value=p[8], lineno=p.lineno(8)),
        ASTnode("LBRACE", value=p[9], lineno=p.lineno(9)),
        ASTnode("commands", p[10], lineno=p.lineno(10)),
        ASTnode("RBRACE", value=p[11], lineno=p.lineno(11)),
    ]
    p[0] = ASTnode("for", children=children, lineno=p.lineno(1))


def p_error(p):
    # stopping at the first error, because the grammar has no error recovery rules
    if p is None:
        print("Syntax error: unexpected end of file")
    else:
        print(f"[Line {p.lineno}]: Syntax error at '{p.value}'")
    sys.exit(1)
