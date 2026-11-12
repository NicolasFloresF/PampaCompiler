"""Generates the x86-64 assembly (GNU as, AT&T syntax) and appends the runtime behind escreva, leia and strings."""

# Unique labels and string literals
from .labels import *

# Loads and stores of variables, by type size
from .variables import *

# Expressions and function calls
from .expressions import *

# Functions, commands and the whole program
from .code_generator import *
