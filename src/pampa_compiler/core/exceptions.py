class CompilerError(Exception):
    """Base class for all compiler errors"""

    def __init__(self, msg, lineno=None):
        if lineno is not None:
            msg = f"[Line {lineno}]: {msg}"
        super().__init__(msg)


class SymbolNotFound(CompilerError):
    """Exception raised when a symbol is not found in the symbol table"""

    pass


class RedeclarationError(CompilerError):
    """Exception raised when a symbol is redeclared"""

    pass


class TypeMismatchError(CompilerError):
    """Exception raised when there is a type mismatch"""

    pass


class InvalidForLoopError(CompilerError):
    """Raised when a for-loop has invalid expressions"""

    pass


class ParamCountError(CompilerError):
    """Raised when the number of parameters is incorrect"""

    pass
