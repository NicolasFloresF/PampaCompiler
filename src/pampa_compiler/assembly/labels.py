"""Hands out unique labels for the generated assembly and keeps the string literals that go to .rodata."""

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
    return labels[value]
