from symbol_table import *

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

label_counter = {
    "label": 0,
    "float": 0,
    "int": 0,
    "string": 0,
    "bool": 0,
    "if": 0,
    "else": 0,
    "endif": 0,
    "while": 0,
    "endwhile": 0,
    "for": 0,
    "endfor": 0,
}

labels = {}


def new_label(value, base="label"):
    label_counter[base] += 1
    labels[value] = [base, f"{base}_{label_counter[base]}"]
    return list(labels.values())[-1]


def generate_code(function_list, local_tables, global_table):
    for i, function in enumerate(function_list):
        generate_func(function, local_tables[i], global_table)
        print()

    # Generate read-only data section
    generate_rodata()


def generate_func(node, table, global_table):
    size = table.return_by_index(-1).offset

    print(f".global {node.value}")
    print(f"{node.value}:")
    print(f"    push %rbp")
    print(f"    mov %rsp, %rbp")
    print(f"    sub ${size * -1}, %rsp\n")  # Reserve space for local variables

    for child in node.children[-2].children:
        generate_assembly(child, table, global_table)


def generate_assembly(node, table, global_table):
    if node.nodetype == "assignment_expression":
        code = assignment_handler(node, table)
        print(code)

    elif node.nodetype == "declaration":
        decls_handler(node.children[1], table, global_table)

    elif node.nodetype == "print":
        code = print_handler(node, table)
        print(code)

    elif node.nodetype in ["binary_expression", "relational_expression", "logical_expression"]:
        expr_code = expression_handler(node, table)
        print(expr_code)

    elif node.nodetype == "call_function_expression":
        if node.children[-2].nodetype == "expression_list":
            code = call_expression_handler(node.children[-2], table, node.children[0].value)
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
    code = ""
    var_name = node.children[0].value
    expr = node.children[2]

    if expr.nodetype == "number":
        code += f"    movq ${expr.value}, {table.lookup(var_name).offset}(%rbp)\n"
    elif expr.nodetype == "string":
        if expr.value not in labels:
            new_label(expr.value, "string")
        code += f"    lea {labels[expr.value][1]}(%rip), %rax\n"
        code += f"    movq %rax, {table.lookup(var_name).offset}(%rbp)\n"
    elif expr.nodetype == "boolean":
        if expr.value == "verdadeiro":
            code += f"    movb $1, {table.lookup(var_name).offset}(%rbp)\n"
        else:
            code += f"    movb $0, {table.lookup(var_name).offset}(%rbp)\n"
    elif expr.nodetype in ["binary_expression", "logical_expression", "relational_expression"]:
        code += expression_handler(expr, table)
        code += f"    movq %rax, {table.lookup(var_name).offset}(%rbp)\n"

    return code


def decls_handler(node, table, global_table):
    if node.nodetype == "declarations":
        for child in node.children:
            if child.nodetype == "atribuition":
                var_name = node.children[0].value
                expr = node.children[2]

                if expr.nodetype == "number":
                    print(f"    # {node.children[0].value} = {node.children[2].value}")
                    print(f"    movq ${expr.value}, {table.lookup(var_name).offset}(%rbp)\n")

                elif expr.nodetype == "string":
                    print(f"    # {node.children[0].value} = {node.children[2].value}")
                    if expr.value not in labels:
                        new_label(expr.value, "string")
                    print(f"    lea {labels[expr.value][0]}(%rip), %rax")
                    print(f"    movq %rax, {table.lookup(var_name).offset}(%rbp)\n")

                elif expr.nodetype == "boolean":
                    print(f"    # {node.children[0].value} = {node.children[2].value}")
                    if expr.value == "verdadeiro":
                        print(f"    movb $1, {table.lookup(var_name).offset}(%rbp)\n")
                    else:
                        print(f"    movb $0, {table.lookup(var_name).offset}(%rbp)\n")

            if child.nodetype in ["binary_expression", "logical_expression", "relational_expression"]:
                expr_code = expression_handler(child, table)
                print(expr_code)
                print(f"    movq %rax, {table.lookup(var_name).offset}(%rbp)\n")

            if child.nodetype == "declarations":
                decls_handler(child, table, global_table)


def print_handler(node, table):
    print(f"    # {node.children[0].value} ({node.children[2].value})")
    code = ""
    if node.children[2].nodetype == "identifier":
        var_name = node.children[2].value
        code += f"    movq {table.lookup(var_name).offset}(%rbp), %rdi\n"
        code += "    call syscall_print\n"
    elif node.children[2].nodetype == "string":
        if node.children[2].value not in labels:
            new_label(node.children[2].value, "string")
        code += f"    lea {labels[node.children[2].value][1]}(%rip), %rdi\n"
        code += "    call syscall_print\n"

    return code


def expression_handler(node, table):
    if node.nodetype == "number":
        return f"    movq ${node.value}, %rax\n"

    elif node.nodetype == "identifier":
        offset = table.lookup(node.value).offset
        return f"    movq {offset}(%rbp), %rax\n"

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

        if op == "&&":
            code += "    andq %rbx, %rax\n"
        elif op == "||":
            code += "    orq %rbx, %rax\n"

        return code

    return f"    # Unhandled expression: {node.nodetype}\n"


def call_expression_handler(node, table, func_name):
    print(f"    # {func_name}({', '.join([arg.value for arg in node.children])})")
    code = ""
    arg_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
    args = node.children

    # Store generated expressions temporarily
    arg_codes = [expression_handler(arg, table) for arg in args]

    # Split into register and stack-passed args
    reg_args = arg_codes[:6]
    stack_args = arg_codes[6:]

    # Push stack arguments (right to left)
    for expr_code in reversed(stack_args):
        code += expr_code
        code += "    push %rax\n"

    # Move register arguments
    for i, expr_code in enumerate(reg_args):
        code += expr_code
        code += f"    movq %rax, {arg_regs[i]}\n"

    # Make the function call
    code += f"    call {func_name}\n"

    # Clean up the stack if any extra args were pushed
    if stack_args:
        code += f"    addq ${len(stack_args) * 8}, %rsp\n"

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

    if op == "++":
        code += f"    movq {table.lookup(var_name).offset}(%rbp), %rax\n"
        code += f"    addq $1, %rax\n"
        code += f"    movq %rax, {table.lookup(var_name).offset}(%rbp)\n"
    elif op == "--":
        code += f"    movq {table.lookup(var_name).offset}(%rbp), %rax\n"
        code += f"    subq $1, %rax\n"
        code += f"    movq %rax, {table.lookup(var_name).offset}(%rbp)\n"

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
