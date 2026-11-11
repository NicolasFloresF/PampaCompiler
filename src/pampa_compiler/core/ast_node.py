import ply.yacc as yacc
from graphviz import Digraph


class ASTnode:
    def __init__(self, nodetype, children=None, value=None, lineno=None):
        self.nodetype = nodetype
        self.children = children if children is not None else []
        self.lineno = lineno
        self.value = value
        self.childnum = len(self.children)

    def __repr__(self, level=0):
        indent = "  " * level
        ret = f"{indent}{self.nodetype}"
        if self.value is not None:
            ret += f": {self.value}"
        if self.lineno is not None:
            ret += f" (Line {self.lineno})"
        ret += "\n"

        for child in self.children:
            if isinstance(child, ASTnode):
                ret += child.__repr__(level + 1)
            else:
                ret += "  " * (level + 1) + repr(child) + "\n"
        return ret

    def to_graphviz(self, dot=None, parent=None, counter=None):
        if dot is None:
            dot = Digraph()
            dot.attr(rankdir="TB")
            counter = [0]

        node_id = f"node{counter[0]}"
        label = f"{self.nodetype}"
        if self.value is not None:
            label += f"\\n{self.value}"
        dot.node(node_id, label)
        counter[0] += 1

        if parent is not None:
            dot.edge(parent, node_id)

        for child in self.children:
            if isinstance(child, ASTnode):
                child.to_graphviz(dot, node_id, counter)
            else:
                child_id = f"node{counter[0]}"
                dot.node(child_id, str(child))
                dot.edge(node_id, child_id)
                counter[0] += 1

        return dot
