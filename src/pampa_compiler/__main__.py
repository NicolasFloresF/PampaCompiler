# import third-party modules
from argparse import ArgumentParser
import os, sys

# import project modules
from pampa_compiler.lexical.tokens import *
from pampa_compiler.syntax.grammar import *
from pampa_compiler.semantic.semantic_analyzer import *
from pampa_compiler.assembly.code_generator import *


def read_file(file_name):
    file = open(file_name, "r")

    return file.read()


def print_tokens(lexer, debug):
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok, file=debug)


def print_table(table, debug):
    for name, symbol in table.symbols.items():
        print(f"{name}: {symbol}", file=debug)


def main():
    # get the CLI (stdout) and debug file name
    stdout = sys.stdout
    debug = open(args.debug, "w")

    # instantiate the lexer and run it on the input data
    lexer = lex.lex()
    lexer.input(data)

    # print the tokens to the debug file
    print("Tokens:", file=debug)
    print_tokens(lexer, debug)

    # reset line number and do the syntax parsing
    lexer.lineno = 1
    parser = yacc.yacc(debug=False)
    syntaxParsing = parser.parse(data, lexer=lexer)

    # print the syntax tree to the debug file
    print("AST:", file=debug)
    print(syntaxParsing, file=debug)

    # plot the syntax tree in a graphviz format
    dot = syntaxParsing.to_graphviz()
    dot.render("ast", format="png", cleanup=True)

    # get the function list from syntax tree
    function_list = syntaxParsing.children[1].children

    # define the symbol tables
    local_tables: list[symbol_table] = []
    global_table = build_global_table(function_list)

    # print the global table to the debug file
    print(f"Parent: {global_table.return_parent()}", file=debug)
    print_table(global_table, debug=debug)

    # itarate through the function list, build local tables and do semantic analysis
    for function in function_list:
        local_tables.append(build_local_table(function, global_table))
        semantic_analysis(function, local_tables[-1], global_table)

    # print the local tables to the debug file
    for table in local_tables:
        # to get global table function from a local table, do global_table.return_table()[table.return_parent()
        print(f"Parent: {table.return_parent()}", file=debug)
        print(f"Details: {global_table.return_table()[table.return_parent()]}", file=debug)
        print_table(table, debug)

    with open(args.file[:-4] + ".asm", "w") as sys.stdout:
        generate_code(function_list, local_tables, global_table)

    print("Compilation finished successfully!", file=stdout)


if __name__ == "__main__":
    parser = ArgumentParser(description="Compiler for the Por language")
    parser.add_argument("--file", type=str, required=True, help="Input data file")
    parser.add_argument(
        "--debug",
        default=os.devnull,
        action="store_const",
        const="compile.out",
        help="Enable compile.out file",
    )
    args = parser.parse_args()
    data = read_file(args.file)
    main()
