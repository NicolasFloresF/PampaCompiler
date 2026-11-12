"""Generates the assembly of expressions and function calls, leaving each value in %rax."""

from pampa_compiler.assembly.labels import *
from pampa_compiler.assembly.variables import *


# registers that carry the first six arguments of a call, in order (System V calling convention)
arg_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]


def expression_handler(node, table):
    if node.nodetype == "number":
        return f"    movq ${node.value}, %rax\n"

    elif node.nodetype == "identifier":
        return load_variable(table.lookup(node.value))

    elif node.nodetype == "string":
        if node.value not in labels:
            new_label(node.value, "string")
        return f"    lea {labels[node.value][1]}(%rip), %rax\n"

    elif node.nodetype == "character":
        return f"    movq ${node.value}, %rax\n"

    elif node.nodetype == "boolean":
        # representing verdadeiro as 1 and falso as 0
        if node.value == "verdadeiro":
            return "    movq $1, %rax\n"
        return "    movq $0, %rax\n"

    elif node.nodetype == "binary_expression" and node.expr_type == "cadeia":
        return concat_handler(node, table)

    elif node.nodetype == "binary_expression":
        left_code = expression_handler(node.children[0], table)
        right_code = expression_handler(node.children[2], table)
        op = node.value

        asm_op = {"+": "addq", "-": "subq", "*": "imulq", "/": "idivq"}.get(op)

        code = left_code
        code += "    push %rax\n"
        code += right_code
        code += "    movq %rax, %rbx\n"  # right operand → %rbx
        code += "    pop %rax\n"  # left operand → %rax

        if op == "/":
            code += "    cqo\n"  # sign-extend %rax into %rdx:%rax
            code += "    idivq %rbx\n"
        else:
            code += f"    {asm_op} %rbx, %rax\n"

        # wrapping an 'inteiro' result to 32 bits, as the int of Java does, and sign-extending it back
        if node.expr_type == "inteiro":
            code += "    cltq\n"

        return code

    elif node.nodetype == "relational_expression":
        left_code = expression_handler(node.children[0], table)
        right_code = expression_handler(node.children[2], table)
        op = node.value

        set_instr = {"==": "sete", "!=": "setne", "<": "setl", "<=": "setle", ">": "setg", ">=": "setge"}[op]

        code = left_code
        code += "    push %rax\n"
        code += right_code
        code += "    movq %rax, %rbx\n"
        code += "    pop %rax\n"

        # comparing the text of two strings, not their addresses
        if node.children[0].expr_type == "cadeia":
            code += "    movq %rax, %rdi\n"
            code += "    movq %rbx, %rsi\n"
            code += "    call pampa_text_equal\n"
            if op == "!=":
                code += "    xorq $1, %rax\n"
            return code

        code += "    cmpq %rbx, %rax\n"
        code += f"    {set_instr} %al\n"
        code += "    movzbq %al, %rax\n"

        return code

    elif node.nodetype == "logical_expression":
        left_code = expression_handler(node.children[0], table)
        right_code = expression_handler(node.children[2], table)
        op = node.value

        code = left_code
        code += "    push %rax\n"
        code += right_code
        code += "    movq %rax, %rbx\n"
        code += "    pop %rax\n"

        if op == "e":
            code += "    andq %rbx, %rax\n"
        elif op == "ou":
            code += "    orq %rbx, %rax\n"

        return code

    elif node.nodetype == "unary_expression":
        code = expression_handler(node.children[0], table)
        code += "    negq %rax\n"
        if node.expr_type == "inteiro":
            code += "    cltq\n"
        return code

    elif node.nodetype == "not_expression":
        # flipping the operand between 1 (verdadeiro) and 0 (falso)
        code = expression_handler(node.children[0], table)
        code += "    xorq $1, %rax\n"
        return code

    elif node.nodetype == "call_function_expression":
        # calls without arguments have no expression_list child
        args = []
        if node.children[-2].nodetype == "expression_list":
            args = node.children[-2].children
        return call_expression_handler(args, table, node.children[0].value)

    return f"    # Unhandled expression: {node.nodetype}\n"


def concat_handler(node, table):
    """Returns the assembly that joins both operands of a '+' into a new string, turning non-text operands into text."""
    code = ""
    for operand in [node.children[0], node.children[2]]:
        code += expression_handler(operand, table)
        code += to_text(operand.expr_type)
        code += "    push %rax\n"
    code += "    pop %rsi\n"
    code += "    pop %rdi\n"
    code += "    call pampa_concat\n"
    return code


def to_text(value_type):
    """Returns the assembly that turns the value of value_type in %rax into the address of its text."""
    routines = {"inteiro": "pampa_int_to_text", "logico": "pampa_bool_to_text", "caracter": "pampa_char_to_text"}
    if value_type not in routines:
        return ""
    return f"    movq %rax, %rdi\n    call {routines[value_type]}\n"


def call_expression_handler(args, table, func_name):
    code = f"    # {func_name}({', '.join([str(arg.value) for arg in args])})\n"

    # Store generated expressions temporarily
    arg_codes = [expression_handler(arg, table) for arg in args]

    # Split into register and stack-passed args
    reg_args = arg_codes[:6]
    stack_args = arg_codes[6:]

    # Push stack arguments (right to left)
    for expr_code in reversed(stack_args):
        code += expr_code
        code += "    push %rax\n"

    # evaluating every register argument before loading any register, because evaluating one
    # (a nested call or a division) overwrites registers that may already hold earlier arguments
    for expr_code in reg_args:
        code += expr_code
        code += "    push %rax\n"
    for i in reversed(range(len(reg_args))):
        code += f"    pop {arg_regs[i]}\n"

    # Make the function call
    code += f"    call {func_name}\n"

    # Clean up the stack if any extra args were pushed
    if stack_args:
        code += f"    addq ${len(stack_args) * 8}, %rsp\n"

    return code
