"""Builds the global table of the functions and the local table of the variables of each function."""

import sys

from pampa_compiler.core.symbols import *
from pampa_compiler.core.ast_node import ASTnode
from pampa_compiler.core.type_sizes import TYPE_SIZES
from pampa_compiler.semantic.expression_types import *


def build_global_table(nodes, table=None):
    for node in nodes:
        if table is None:
            table = symbol_table(parent="programa")

        if isinstance(node, ASTnode):
            if node.nodetype == "function":
                param = next((child for child in node.children if child.nodetype == "param"), None)
                param_types = param_type_extract(param) if param else []

                try:
                    # the type of a function symbol is its return type
                    table.define(
                        node.value,
                        symbol(node.value, node.children[0].value, node.lineno, params=param_types),
                    )
                except RedeclarationError as e:
                    print(f"{e}")
                    sys.exit(1)

    # checking the entry point: every program starts at 'inicio', which takes no parameters
    if "inicio" not in table.return_table():
        print("Missing entry point: the program has no 'inicio' function")
        sys.exit(1)
    if table.lookup("inicio").params:
        print(f"[Line {table.lookup('inicio').lineno}]: Invalid entry point: 'inicio' takes no parameters")
        sys.exit(1)

    return table


def build_local_table(node, global_table):
    """Builds the table of the variables of a function, resolving every name to its declaration.

    Walks the function in order with one scope per block, as Portugol Studio does: a name is visible
    from its declaration to the end of its block, and a block cannot declare a name that is still
    visible. Sibling blocks may reuse a name: each later declaration gets a unique name in the table
    (such as 'total#2'), written into every identifier that refers to it, so the code generator finds
    each variable by name.

    Args:
        node (ASTnode): The function node.
        global_table (symbol_table): Table of the program functions.

    Returns:
        symbol_table: The variables and parameters of the function, by unique name.
    """
    table = symbol_table(parent=node.value)
    scopes = [{}]
    try:
        param = next((child for child in node.children if child.nodetype == "param"), None)
        if param:
            params_extract(param, table, scopes[-1])

        block = next((child for child in node.children if child.nodetype == "commands"), None)
        if block:
            resolve_names(block, table, scopes, global_table)
    except CompilerError as e:
        print(f"{e}")
        sys.exit(1)

    return table


def resolve_names(node, table, scopes, global_table):
    """Declares the variables of node and replaces each identifier by the unique name of its declaration."""
    if node.nodetype == "commands":
        scopes.append({})
        for cmd in node.children:
            resolve_names(cmd, table, scopes, global_table)
        scopes.pop()
    elif node.nodetype == "declaration":
        declare_names(node.children[1], node.children[0].value, table, scopes, global_table)
    elif node.nodetype == "call_function_expression":
        # skipping the function name, which lives in the global table
        for child in node.children[1:]:
            resolve_names(child, table, scopes, global_table)
    elif node.nodetype == "identifier":
        node.value = lookup_name(node, scopes)
    else:
        for child in node.children:
            resolve_names(child, table, scopes, global_table)


def lookup_name(node, scopes):
    """Returns the unique name of the visible declaration of the identifier node, from the innermost scope out."""
    for scope in reversed(scopes):
        if node.value in scope:
            return scope[node.value]
    raise SymbolNotFound(f"Missing declaration error: Symbol [{node.value}] is not declared", node.lineno)


def declare_names(decls, var_type, table, scopes, global_table):
    """Declares each name of a declaration list in the current scope, checking its initializer first."""
    name_node = decls.children[0]
    if len(decls.children) > 1 and decls.children[1].nodetype == "atribuition":
        # resolving the initializer before declaring the name, so 'inteiro a = a' finds no 'a'
        initializer = decls.children[2]
        resolve_names(initializer, table, scopes, global_table)
        expr_type = evaluate_expr_type(initializer, table, global_table)
        if not accepts(var_type, initializer):
            raise TypeMismatchError(
                f"Type mismatch: Symbol [{name_node.value}] expected type '{var_type}' but get type '{expr_type}' instead",
                decls.children[1].lineno,
            )

    define_name(name_node, var_type, table, scopes)

    if decls.children[-1].nodetype == "declarations":
        declare_names(decls.children[-1], var_type, table, scopes, global_table)


def define_name(name_node, var_type, table, scopes):
    """Adds a variable to the table and to the current scope, renaming it when a sibling block used its name."""
    name = name_node.value
    for scope in scopes:
        if name in scope:
            previous = table.lookup(scope[name])
            raise RedeclarationError(f"Redeclaration error: Symbol [{name}] already declared", previous.lineno)

    unique_name = name
    copy_number = 2
    while unique_name in table.return_table():
        unique_name = f"{name}#{copy_number}"
        copy_number += 1

    offset = calculate_offset(table.return_table(), var_type)
    table.define(unique_name, symbol(name, var_type, name_node.lineno, offset=offset))
    scopes[-1][name] = unique_name
    name_node.value = unique_name


def params_extract(param, table, scope):
    if param.nodetype == "param":
        var_type = param.children[0].value
        define_name(param.children[1], var_type, table, [scope])
        if param.children[-1].nodetype == "param":
            params_extract(param.children[-1], table, scope)


def calculate_offset(dic, var_type):
    size = TYPE_SIZES[var_type]
    last_offset = list(dic.values())[-1].offset if dic else 0
    offset = last_offset - size
    # aligning the slot to its own size, rounding down because the slots grow downwards from %rbp
    return offset - offset % size


def param_type_extract(param, types=None):
    if types is None:
        types = []
    if param.nodetype == "param":
        types.append(param.children[0].value)
        if param.children[-1].nodetype == "param":
            param_type_extract(param.children[-1], types)
    return types
