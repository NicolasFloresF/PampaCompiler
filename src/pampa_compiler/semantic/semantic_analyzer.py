import sys

from pampa_compiler.core.symbol_table import *
from pampa_compiler.core.ast_node import ASTnode
from pampa_compiler.semantic.expression_types import *


def semantic_analysis(node, table, global_table):
    """This function performs semantic analysis in each function in AST, using the local symbol table.
    It checks for type mismatches, undeclared variables, and other semantic errors.

    Args:
        node (ASTnode): The AST node to analyze.
        table (symbol_table): The symbol table to use for semantic analysis.
    """
    if isinstance(node, ASTnode):
        if node.nodetype == "function":
            check_function(node, table, global_table)

        elif node.nodetype == "assignment_expression":
            check_assignment(node, table, global_table)

        elif node.nodetype == "increment_expression":
            check_increment(node, table)

        elif node.nodetype == "return_expression":
            check_return(node, table, global_table)

        elif node.nodetype == "call_function_expression":
            check_call(node, table, global_table)

        elif node.nodetype == "print":
            check_print(node, table, global_table)

        elif node.nodetype == "read":
            check_read(node, table)

        elif node.nodetype in ["if", "while"]:
            check_if_while(node, table, global_table)

        elif node.nodetype == "for":
            check_for(node, table, global_table)

        elif node.nodetype == "declaration":
            # skipping declarations: build_local_table already checked them
            pass

        else:
            # refusing other expressions as commands, as Portugol Studio does: their value would be lost,
            # and an unknown word (such as a keyword this compiler lacks) would be silently ignored
            raise InvalidCommandError(
                f"Invalid command: {node.nodetype} ({node.value}) is not a function call or an assignment",
                node.lineno,
            )


def check_commands(block, table, global_table):
    """Checks every command of a block, stopping the compilation at the first error."""
    for cmd in block.children:
        try:
            semantic_analysis(cmd, table, global_table)
        except Exception as e:
            print(f"{e}")
            sys.exit(1)


def check_function(node, table, global_table):
    """Checks the commands of a function."""
    block = next((child for child in node.children if child.nodetype == "commands"), None)
    if block:
        check_commands(block, table, global_table)


def check_assignment(node, table, global_table):
    """Checks that the assigned variable is declared and that the value has its type."""
    try:
        declared = table.lookup(node.children[0].value)
    except SymbolNotFound as e:
        print(f"[Line {node.children[0].lineno}]: {e}")
        sys.exit(1)

    try:
        expr_type = evaluate_expr_type(node.children[2], table, global_table)
    except TypeMismatchError as e:
        print(f"{e}")
        sys.exit(1)

    if expr_type != declared.type:
        raise TypeMismatchError(
            f"Type mismatch: Symbol [{node.children[0].value}] expected type '{declared.type}' but get type '{expr_type}' instead",
            node.lineno,
        )


def check_increment(node, table):
    """Checks that the incremented or decremented variable is a declared 'inteiro'."""
    try:
        declared = table.lookup(node.children[0].value)
    except SymbolNotFound as e:
        print(f"[Line {node.children[0].lineno}]: {e}")
        sys.exit(1)

    if declared.type != "inteiro":
        raise TypeMismatchError(
            f"Type mismatch: Increment operation only allowed on 'inteiro' type, but got '{declared.type}' instead'",
            node.lineno,
        )


def check_return(node, table, global_table):
    """Checks that the returned value has the return type of the function."""
    try:
        expr_type = evaluate_expr_type(node.children[1], table, global_table)
    except SymbolNotFound as e:
        print(f"[Line {node.children[0].lineno}]: {e}")
        sys.exit(1)

    # checking the value against the function type; functions without a type ('vazio') return nothing
    return_type = global_table.lookup(table.return_parent()).type
    if return_type == "vazio":
        raise TypeMismatchError(
            f"Type mismatch: Function '{table.return_parent()}' has no return type, so it cannot return a value",
            node.lineno,
        )
    if expr_type != return_type:
        raise TypeMismatchError(
            f"Type mismatch: Function '{table.return_parent()}' must return type '{return_type}', but get type '{expr_type}' instead",
            node.lineno,
        )


def check_print(node, table, global_table):
    """Checks the arguments of escreva and stores the type of each one."""
    try:
        # keeping the type on each argument, as the code generator picks the print routine by it
        for arg in node.children[2].children:
            arg.expr_type = evaluate_expr_type(arg, table, global_table)
    except TypeMismatchError as e:
        print(f"{e}")
        sys.exit(1)


def check_read(node, table):
    """Checks that every variable of leia is declared with a type leia can read."""
    for variable in node.children[1:-1]:
        try:
            declared = table.lookup(variable.value)
        except SymbolNotFound as e:
            print(f"[Line {variable.lineno}]: {e}")
            sys.exit(1)

        if declared.type not in ["inteiro", "logico", "cadeia"]:
            raise TypeMismatchError(
                f"Type mismatch: leia only reads 'inteiro', 'logico' and 'cadeia' values, but Symbol [{declared.name}] has type '{declared.type}'",
                node.lineno,
            )


def check_if_while(node, table, global_table):
    """Checks the condition of a 'se' or 'enquanto' and the commands of its blocks."""
    condition = node.children[1]
    try:
        condition_type = evaluate_expr_type(condition, table, global_table)
    except TypeMismatchError as e:
        print(f"{e}")
        sys.exit(1)

    if condition_type != "logico":
        raise TypeMismatchError(
            f"Type mismatch: {node.nodetype} Condition must be of type 'logico', but got '{condition_type}' instead'",
            node.lineno,
        )
    # visiting every block, so the 'senao' block of an 'if' is checked too
    for block in node.children:
        if block.nodetype == "commands":
            check_commands(block, table, global_table)


def check_for(node, table, global_table):
    """Checks the initialization, condition and step of a 'para' loop and the commands of its body."""
    init_expr = node.children[1]
    cond_expr = node.children[3]
    step_expr = node.children[5]

    # first expression (initialization)
    if init_expr.nodetype == "assignment_expression":
        try:
            semantic_analysis(init_expr, table, global_table)
        except Exception as e:
            print(f"{e}")
            sys.exit(1)
    else:
        raise InvalidForLoopError(
            f"Invalid para loop: Invalid initialization expression in [para] loop", init_expr.lineno
        )

    # second expression (condition)
    try:
        cond_type = evaluate_expr_type(cond_expr, table, global_table)
    except TypeMismatchError as e:
        print(f"{e}")
        sys.exit(1)
    if cond_type != "logico":
        raise TypeMismatchError(
            f"Type mismatch: Condition of 'para' loop must be of type 'logico', but got '{cond_type}' instead'",
            cond_expr.lineno,
        )

    # third expression (step)
    if step_expr.nodetype in ["increment_expression", "assignment_expression"]:
        try:
            semantic_analysis(step_expr, table, global_table)
        except Exception as e:
            print(f"{e}")
            sys.exit(1)
    else:
        raise InvalidForLoopError(f"Invalid para loop: Invalid step expression in [para] loop", step_expr.lineno)

    # loop body
    block = next((child for child in node.children if child.nodetype == "commands"), None)
    if block:
        check_commands(block, table, global_table)
