"""Holds what every phase shares: the syntax tree node, the symbol tables, the compiler errors and the type sizes."""

# Compiler errors
from .exceptions import *

# Syntax tree
from .ast_node import *

# Symbol tables
from .symbols import *

# Size in bytes of each type
from .type_sizes import *
