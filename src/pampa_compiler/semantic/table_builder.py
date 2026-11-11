"""Builds the global table of the functions and the local table of the variables of each function."""

import sys

from pampa_compiler.core.symbol_table import *
from pampa_compiler.core.ast_node import ASTnode
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


def build_local_table(node, global_table, table=None, var_type=None):
    if table is None:
        table = symbol_table(parent=node.value)

    if isinstance(node, ASTnode):
        if node.nodetype == "function":
            param = next((child for child in node.children if child.nodetype == "param"), None)

            if param:
                params_extract(param, table)

            block = next((child for child in node.children if child.nodetype == "commands"), None)
            if block:
                for cmd in block.children:
                    build_local_table(cmd, global_table, table)
        elif node.nodetype in ["if", "while", "for"]:
            # registering declarations made inside blocks in the function table, as there is no block scope
            for block in node.children:
                if block.nodetype == "commands":
                    for cmd in block.children:
                        build_local_table(cmd, global_table, table)
        elif node.nodetype == "declaration":
            var_type = node.children[0].value
            decls = node.children[1]
            try:
                declarations_extract(decls, table, var_type, global_table)
            except CompilerError as e:
                print(f"{e}")
                sys.exit(1)

    return table


def declarations_extract(decls, table, var_type, global_table):
    if decls.nodetype == "declarations":
        for idx, child in enumerate(decls.children):
            if child.nodetype == "identifier":
                dic = symbol_table.return_table(table)
                offset = calculate_offset(dic, var_type)

                try:
                    table.define(child.value, symbol(child.value, var_type, child.lineno, offset=offset))
                except RedeclarationError as e:
                    print(f"{e}")
                    sys.exit(1)
            elif child.nodetype == "atribuition":
                expr = decls.children[idx + 1]
                try:
                    expr_type = evaluate_expr_type(expr, table, global_table)
                except CompilerError as e:
                    print(f"{e}")
                    sys.exit(1)
                if expr_type != var_type:
                    raise TypeMismatchError(
                        f"Type mismatch: Symbol [{decls.children[idx - 1].value}] expected type '{var_type}' but get type '{expr_type}' instead",
                        child.lineno,
                    )
            elif child.nodetype == "declarations":
                try:
                    declarations_extract(child, table, var_type, global_table)
                except CompilerError as e:
                    print(f"{e}")
                    sys.exit(1)


def params_extract(param, table):
    if param.nodetype == "param":
        var_type = param.children[0].value

        dic = symbol_table.return_table(table)
        offset = calculate_offset(dic, var_type)

        try:
            table.define(
                param.children[1].value,
                symbol(param.children[1].value, var_type, param.children[1].lineno, offset=offset),
            )
        except RedeclarationError as e:
            print(f"{e}")
            sys.exit(1)
        if param.children[-1].nodetype == "param":
            params_extract(param.children[-1], table)


def calculate_offset(dic, var_type):
    # giving every type 8 bytes, because the code generator moves values with 64-bit instructions (movq)
    basic_sizes = {
        "inteiro": 8,
        "real": 8,
        "logico": 8,
        "caracter": 8,
    }[var_type]
    if not dic:
        return -basic_sizes
    else:
        last_offset = list(dic.values())[-1].offset
        return last_offset - basic_sizes


def param_type_extract(param, types=None):
    if types is None:
        types = []
    if param.nodetype == "param":
        types.append(param.children[0].value)
        if param.children[-1].nodetype == "param":
            param_type_extract(param.children[-1], types)
    return types
