"""Builds the symbol tables, resolves each name in its block scope and checks the types."""

# Type of each expression and checks of function calls
from .expression_types import *

# Global and local symbol tables, with block scope
from .table_builder import *

# Semantic checks of each command
from .semantic_analyzer import *
