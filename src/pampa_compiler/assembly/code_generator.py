import os

from pampa_compiler.core.symbol_table import *
from pampa_compiler.assembly.labels import *
from pampa_compiler.assembly.expressions import *
from pampa_compiler.assembly.variables import *


# entry point and routines behind escreva and leia, appended to every program
RUNTIME_PATH = os.path.join(os.path.dirname(__file__), "runtime.s")

# Registers and their usage:

# %rax -> Accumulator register, used for arithmetic operations and return values.
# %rbx -> Base register, often used as a general-purpose register.
# %rcx -> Counter register, commonly used for loops and string operations.
# %rdx -> Data register, used in I/O operations and for multiplication/division.
# %rdi -> First argument register in function calls (calling convention).
# %rsi -> Second argument register in function calls (calling convention).
# %rbp -> Base pointer, used to point to the base of the current stack frame.
# %rsp -> Stack pointer, points to the top of the stack.
# %r8  -> General-purpose register, used for additional function arguments.
# %r9  -> General-purpose register, used for additional function arguments.
# %r10 -> General-purpose register, caller-saved.
# %r11 -> General-purpose register, caller-saved.
# %r12 -> General-purpose register, callee-saved.
# %r13 -> General-purpose register, callee-saved.
# %r14 -> General-purpose register, callee-saved.
# %r15 -> General-purpose register, callee-saved.


def generate_code(function_list, local_tables, global_table):
    for i, function in enumerate(function_list):
        generate_func(function, local_tables[i], global_table)
        print()

    # Generate read-only data section
    generate_rodata()

    with open(RUNTIME_PATH) as runtime_file:
        print(runtime_file.read())


def generate_func(node, table, global_table):
    # reserving no stack space when the function has no variables or parameters
    size = 0
    if table.return_table():
        size = table.return_by_index(-1).offset * -1
    # rounding the frame up to a multiple of 16, as the x86-64 ABI requires a 16-byte aligned stack
    size = (size + 15) // 16 * 16

    print(f".global {node.value}")
    print(f"{node.value}:")
    print(f"    push %rbp")
    print(f"    mov %rsp, %rbp")
    print(f"    sub ${size}, %rsp\n")  # Reserve space for local variables

    # copying each parameter into its slot: the first six arrive in registers, the others on the caller's stack
    params = global_table.lookup(node.value).params
    for index in range(len(params)):
        if index < len(arg_regs):
            print(f"    movq {arg_regs[index]}, %rax")
        else:
            print(f"    movq {16 + (index - len(arg_regs)) * 8}(%rbp), %rax")
        print(store_variable(table.return_by_index(index)), end="")
    if params:
        print()

    for child in node.children[-2].children:
        generate_assembly(child, table, global_table)

    # returning 0 when the function does not end with 'retorne', instead of running into the code after it
    if node.children[-2].children[-1].nodetype != "return_expression":
        print("    movq $0, %rax")
        print("    leave")
        print("    ret")


def generate_assembly(node, table, global_table):
    if node.nodetype == "assignment_expression":
        code = assignment_handler(node, table)
        print(code)

    elif node.nodetype == "declaration":
        decls_handler(node.children[1], table, global_table)

    elif node.nodetype == "print":
        code = print_handler(node, table)
        print(code)

    elif node.nodetype == "read":
        code = read_handler(node, table)
        print(code)

    elif node.nodetype in ["binary_expression", "relational_expression", "logical_expression"]:
        expr_code = expression_handler(node, table)
        print(expr_code)

    elif node.nodetype == "call_function_expression":
        code = expression_handler(node, table)
        print(code)

    elif node.nodetype == "return_expression":
        code = return_expression_handler(node, table)
        print(code)

    elif node.nodetype == "increment_expression":
        code = increment_expression_handler(node, table)
        print(code)

    elif node.nodetype == "if":
        if_handler(node, table, global_table)

    elif node.nodetype == "while":
        while_handler(node, table, global_table)

    elif node.nodetype == "for":
        for_handler(node, table, global_table)


def assignment_handler(node, table):
    print(f"    # {node.children[0].value} = {node.children[2].value}")
    var_name = node.children[0].value
    code = expression_handler(node.children[2], table)
    code += store_variable(table.lookup(var_name))
    return code


def decls_handler(node, table, global_table):
    if node.nodetype == "declarations":
        # storing an initializer like an assignment: both are the name, '=' and the expression
        if len(node.children) > 1 and node.children[1].nodetype == "atribuition":
            print(assignment_handler(node, table))

        if node.children[-1].nodetype == "declarations":
            decls_handler(node.children[-1], table, global_table)


def print_handler(node, table):
    args = node.children[2].children
    print(f"    # {node.children[0].value} ({', '.join([str(arg.value) for arg in args])})")
    # choosing the runtime routine of each argument by the type the semantic analysis found for it
    routines = {"inteiro": "pampa_print_int", "logico": "pampa_print_bool", "caracter": "pampa_print_string"}
    code = ""
    for arg in args:
        if arg.expr_type not in routines:
            code += f"    # Unhandled print of type {arg.expr_type}\n"
            continue
        code += expression_handler(arg, table)
        code += "    movq %rax, %rdi\n"
        code += f"    call {routines[arg.expr_type]}\n"

    return code


def read_handler(node, table):
    # choosing the runtime routine by the type of each variable
    routines = {"inteiro": "pampa_read_int", "logico": "pampa_read_bool"}
    code = ""
    for variable in node.children[1:-1]:
        declared = table.lookup(variable.value)
        code += f"    # leia ({variable.value})\n"
        code += f"    call {routines[declared.type]}\n"
        code += store_variable(declared)
    return code


def return_expression_handler(node, table):
    print(f"    # return")
    expr_code = expression_handler(node.children[1], table)
    code = expr_code
    code += "    leave\n"
    code += "    ret\n"
    return code


def increment_expression_handler(node, table):
    print(f"    # {node.children[0].value} {node.children[1].value}")
    code = ""
    var_name = node.children[0].value
    op = node.children[1].value

    variable = table.lookup(var_name)
    code += load_variable(variable)
    if op == "++":
        code += "    addq $1, %rax\n"
    elif op == "--":
        code += "    subq $1, %rax\n"
    code += store_variable(variable)

    return code


def if_handler(node, table, global_table):
    condition = node.children[1]
    then_block = node.children[4]
    else_block = node.children[8] if len(node.children) == 10 else None

    else_label = new_label("else", "else")
    endif_label = new_label("endif", "endif")

    print(expression_handler(condition, table))
    print(f"    cmpq $0, %rax")
    if else_block:
        print(f"    je {else_label[1]}\n")
    else:
        print(f"    je {endif_label[1]}\n")

    for child in then_block.children:
        generate_assembly(child, table, global_table)

    print(f"    jmp {endif_label[1]}\n")
    if else_block:
        print(f"{else_label[1]}:")

        for child in else_block.children:
            generate_assembly(child, table, global_table)

        print(f"{endif_label[1]}:")
    else:
        print(f"{endif_label[1]}:")


def while_handler(node, table, global_table):
    condition = node.children[1]
    block = node.children[4]

    while_label = new_label("while", "while")
    endwhile_label = new_label("endwhile", "endwhile")

    print(f"{while_label[1]}:")
    print(expression_handler(condition, table))
    print(f"    cmpq $0, %rax")
    print(f"    je {endwhile_label[1]}\n")

    for child in block.children:
        generate_assembly(child, table, global_table)

    print(f"    jmp {while_label[1]}\n")
    print(f"{endwhile_label[1]}:\n")


def for_handler(node, table, global_table):
    init_expr = node.children[1]
    condition = node.children[3]
    step_expr = node.children[5]
    block = node.children[8]

    for_label = new_label("for", "for")
    endfor_label = new_label("endfor", "endfor")

    print(assignment_handler(init_expr, table))
    print(f"{for_label[1]}:")
    print(expression_handler(condition, table))
    print(f"    cmpq $0, %rax")
    print(f"    je {endfor_label[1]}\n")

    for child in block.children:
        generate_assembly(child, table, global_table)

    if step_expr.nodetype == "increment_expression":
        print(increment_expression_handler(step_expr, table))
    elif step_expr.nodetype == "assignment_expression":
        print(assignment_handler(step_expr, table))

    print(f"    jmp {for_label[1]}\n")
    print(f"{endfor_label[1]}:\n")


def generate_rodata():
    print(".section .rodata")
    for label, value in labels.items():
        if value[0] == "string":
            print(f"{value[1]}:")
            print(f"    .string {label}")
        elif value[0] == "float":
            print(f"{value[1]}:")
            print(f"    .float {label}")
        elif value[0] == "int":
            print(f"{value[1]}:")
            print(f"    .int {label}")
