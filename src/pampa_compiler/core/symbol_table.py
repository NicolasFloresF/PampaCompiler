from pampa_compiler.core.exceptions import *


class symbol_table:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, value):
        if name in self.symbols:
            raise RedeclarationError(
                f"Redeclaration error: Symbol [{name}] already declared", self.symbols[name].lineno
            )
        self.symbols[name] = value

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        else:
            raise SymbolNotFound(f"Missing declaration error: Symbol [{name}] is not declared")

    def return_by_index(self, index):
        if index < len(self.symbols):
            return list(self.symbols.values())[index]
        else:
            raise IndexError("Index out of range")

    def return_table(self):
        return self.symbols

    def return_parent(self):
        return self.parent


class symbol:
    def __init__(self, name, type, lineno=None, offset=None, params=None):
        self.name = name
        self.type = type
        self.lineno = lineno
        self.offset = offset
        self.params = params

    def __repr__(self):
        return f"Symbol(name={self.name}, type={self.type}, lineno={self.lineno}, offset={self.offset}, params={self.params})"
