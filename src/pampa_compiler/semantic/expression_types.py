"""Finds the type of each expression and checks function calls against their declarations."""

import sys

from pampa_compiler.core.symbol_table import *


def evaluate_expr_type(expr, table, global_table):
    """Returns the type of an expression and keeps it on the node, where the code generator reads it."""
    expr.expr_type = find_expr_type(expr, table, global_table)
    return expr.expr_type


def find_expr_type(expr, table, global_table):
    if expr.nodetype == "number":
        if isinstance(expr.value, int):
            # refusing what does not fit the 32 bits of 'inteiro', as Portugol Studio does
            if not -(2**31) <= expr.value < 2**31:
                raise TypeMismatchError(
                    f"Integer out of range: {expr.value} does not fit 'inteiro' (-2147483648 to 2147483647)",
                    expr.lineno,
                )
            return "inteiro"
        elif isinstance(expr.value, float):
            return "real"
    elif expr.nodetype == "string":
        return "caracter"
    elif expr.nodetype == "boolean":
        return "logico"
    elif expr.nodetype == "identifier":
        try:
            sym = table.lookup(expr.value)
        except SymbolNotFound as e:
            print(f"[Line {expr.lineno}]: {e}")
            sys.exit(1)
        return sym.type
    elif expr.nodetype in ["binary_expression", "logical_expression", "relational_expression"]:
        try:
            left_type = evaluate_expr_type(expr.children[0], table, global_table)
            right_type = evaluate_expr_type(expr.children[2], table, global_table)
        except TypeMismatchError as e:
            print(f"{e}")
            sys.exit(1)

        numbers = ["inteiro", "real"]
        if expr.nodetype == "binary_expression":
            if left_type in numbers and right_type in numbers:
                if left_type == right_type:
                    return left_type
                else:
                    return "real"
            else:
                raise TypeMismatchError(
                    f"Type mismatch: {expr.nodetype} ({expr.value}) expected types 'inteiro' or 'real', but get type '{left_type}' and '{right_type}' instead",
                    expr.lineno,
                )
        if expr.nodetype == "logical_expression":
            if left_type == right_type == "logico":
                return "logico"
            else:
                raise TypeMismatchError(
                    f"Type mismatch: {expr.nodetype} ({expr.value}) expected type 'logico', but get type '{left_type}' and '{right_type}' instead",
                    expr.lineno,
                )
        if expr.nodetype == "relational_expression":
            # comparing numbers with any operator, and values of the same type for equality only
            both_numbers = left_type in numbers and right_type in numbers
            if both_numbers or (expr.value in ["==", "!="] and left_type == right_type):
                return "logico"
            raise TypeMismatchError(
                f"Type mismatch: {expr.nodetype} ({expr.value}) cannot compare type '{left_type}' with type '{right_type}'",
                expr.lineno,
            )
    elif expr.nodetype == "unary_expression":
        operand_type = evaluate_expr_type(expr.children[0], table, global_table)
        if operand_type not in ["inteiro", "real"]:
            raise TypeMismatchError(
                f"Type mismatch: unary minus expected type 'inteiro' or 'real', but get type '{operand_type}' instead",
                expr.lineno,
            )
        return operand_type
    elif expr.nodetype == "not_expression":
        operand_type = evaluate_expr_type(expr.children[0], table, global_table)
        if operand_type != "logico":
            raise TypeMismatchError(
                f"Type mismatch: nao expected type 'logico', but get type '{operand_type}' instead",
                expr.lineno,
            )
        return "logico"
    elif expr.nodetype == "call_function_expression":
        return_type = check_call(expr, table, global_table)
        if return_type == "vazio":
            raise TypeMismatchError(
                f"Type mismatch: Function '{expr.children[0].value}' returns no value, so it cannot be used in an expression",
                expr.lineno,
            )
        return return_type
    else:
        raise TypeMismatchError(
            f"Type mismatch: {expr.nodetype} ({expr.value}) expected types 'inteiro', 'real', 'logico' or expression, but get type 'unknown' instead",
            expr.lineno,
        )


def check_call(node, table, global_table):
    """Checks that a called function exists and that the arguments match its parameters.

    Args:
        node (ASTnode): The call_function_expression node.
        table (symbol_table): Local table of the calling function.
        global_table (symbol_table): Table of the program functions.

    Returns:
        str: The return type of the called function ('vazio' when it returns nothing).
    """
    func_name = node.children[0].value
    try:
        declared = global_table.lookup(func_name)
    except SymbolNotFound as e:
        print(f"[Line {node.children[0].lineno}]: {e}")
        sys.exit(1)
    params = next((child for child in node.children if child.nodetype == "expression_list"), None)
    if params:
        arg_list = args_extract(params.children, table, global_table)
    else:
        arg_list = []

    # Check if the number of arguments matches
    if len(arg_list) != len(declared.params):
        raise ParamCountError(
            f"Param count error: Function '{func_name}' expected {len(declared.params)} arguments, but got {len(arg_list)} instead",
            node.lineno,
        )

    # check argument types
    for i in range(len(arg_list)):
        if arg_list[i] != declared.params[i]:
            raise TypeMismatchError(
                f"Type mismatch: Argument {i + 1} of function '{func_name}' expected type '{declared.params[i]}', but got '{arg_list[i]}' instead",
                node.lineno,
            )

    return declared.type


def args_extract(children, table, global_table, param_list=None):
    if param_list is None:
        param_list = []

    for child in children:
        if child.nodetype in [
            "number",
            "string",
            "boolean",
            "identifier",
            "binary_expression",
            "logical_expression",
            "relational_expression",
            "not_expression",
            "unary_expression",
            "call_function_expression",
        ]:
            try:
                id_type = evaluate_expr_type(child, table, global_table)
            except SymbolNotFound as e:
                print(f"[Line {child.lineno}]: {e}")
                sys.exit(1)

            param_list.append(id_type)
        elif child.nodetype == "expression_list":
            param_list = args_extract(child.children, table, global_table, param_list)

    return param_list
