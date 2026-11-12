"""Compiles Portugol programs, in the dialect of Portugol Studio, into standalone x86-64 Linux assembly.

Run it with: python -m pampa_compiler --file program.por [--ast] [--debug]
"""

# Shared structures: syntax tree, symbol tables, errors and type sizes
from .core import *

# Lexical analysis
from .lexical import *

# Syntax analysis
from .syntax import *

# Semantic analysis
from .semantic import *

# Code generation
from .assembly import *
