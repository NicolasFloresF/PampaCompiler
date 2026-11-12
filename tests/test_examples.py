"""Compiles every program in examples/, runs it and checks its output.

Run from the repository root with: uv run python -m unittest discover tests
"""

import os
import subprocess
import sys
import tempfile
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TESTS_DIR)
EXAMPLES_DIR = os.path.join(REPO_DIR, "examples")

# Expected standard output of each example.
EXPECTED_OUTPUT = {
    "arithmetic.por": "20 + 6 = 26\n20 - 6 = 14\n20 * 6 = 120\n20 / 6 = 3\n",
    "precedence.por": "2 + 3 * 4 - (2 + 3) * 2 = 4\n",
    "conditionals.por": "Score 75 is level 2\n",
    "while_sum.por": "1 + 2 + ... + 10 = 55\n",
    "for_factorial.por": "5! = 120\n",
    "nested_loops.por": "Pairs (i, j) below 10 with i < j: 45\n",
    "gcd.por": "gcd(48, 18) = 6\n",
    "logic.por": "inside = verdadeiro\nhits = 2\n",
    "primes.por": "2 3 5 7 11 13 17 19 23 29 \n10 primes below 30\n",
    "functions.por": "3 * 3 + 4 * 4 = 25\n25 is odd\n",
    "fibonacci.por": "0 1 1 2 3 5 8 13 21 34 55 \n",
    "hello_world.por": "Ola, mundo!\n3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n",
    "read_sum.por": "How many numbers? Number 1: Number 2: Number 3: Sum = 13\n",
    "types.por": "Ana (A), 20 years, 1.75 m, student: verdadeiro\nAverage of 7 and 8.5: 7.75\n",
}

# Standard input of the examples that read with leia; the others read nothing.
EXAMPLE_INPUT = {
    "read_sum.por": "3\n10\n-4\n7\n",
}


def run_command(command: list[str], work_dir: str, stdin: str = "") -> subprocess.CompletedProcess:
    """Runs a command inside work_dir.

    Args:
        command (list[str]): Program and arguments.
        work_dir (str): Directory the command runs in.
        stdin (str): Text sent to the standard input of the command.

    Returns:
        subprocess.CompletedProcess: Exit status and captured text output.
    """
    return subprocess.run(command, cwd=work_dir, input=stdin, capture_output=True, text=True, timeout=10, check=False)


def compile_program(source: str, work_dir: str) -> subprocess.CompletedProcess:
    """Writes source to work_dir/program.por and compiles it into work_dir/program.asm.

    Args:
        source (str): Portugol source code.
        work_dir (str): Directory that receives the source, the assembly and ast.png.

    Returns:
        subprocess.CompletedProcess: Result of the compiler run.
    """
    program_path = os.path.join(work_dir, "program.por")
    with open(program_path, "w") as program_file:
        program_file.write(source)
    return run_command([sys.executable, "-m", "pampa_compiler", "--file", program_path], work_dir)


def assemble_and_link(work_dir: str) -> subprocess.CompletedProcess:
    """Assembles work_dir/program.asm and links it into the standalone executable work_dir/program.

    Args:
        work_dir (str): Directory holding program.asm.

    Returns:
        subprocess.CompletedProcess: Result of the first step that failed, or of the link.
    """
    steps = [
        ["as", "program.asm", "-o", "program.o"],
        ["ld", "program.o", "-o", "program"],
    ]
    for step in steps:
        result = run_command(step, work_dir)
        if result.returncode != 0:
            return result
    return result


def build_and_run(test_case: unittest.TestCase, source: str, stdin: str = "") -> subprocess.CompletedProcess:
    """Compiles, links and runs source, failing test_case at the first step that fails.

    Args:
        test_case (unittest.TestCase): Test that receives the failure.
        source (str): Portugol source code.
        stdin (str): Text the program reads with leia.

    Returns:
        subprocess.CompletedProcess: Exit status and output of the program.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        compiled = compile_program(source, work_dir)
        test_case.assertEqual(compiled.returncode, 0, f"compiler failed:\n{compiled.stdout}{compiled.stderr}")

        linked = assemble_and_link(work_dir)
        test_case.assertEqual(linked.returncode, 0, f"assembler or linker failed:\n{linked.stderr}")

        return run_command(["./program"], work_dir, stdin)


class ExamplesTest(unittest.TestCase):
    def test_every_example_has_an_expected_output(self):
        example_names = sorted(name for name in os.listdir(EXAMPLES_DIR) if name.endswith(".por"))
        self.assertEqual(example_names, sorted(EXPECTED_OUTPUT))

    def test_examples_print_expected_output(self):
        for example_name, expected_output in EXPECTED_OUTPUT.items():
            with self.subTest(example=example_name):
                with open(os.path.join(EXAMPLES_DIR, example_name)) as example_file:
                    source = example_file.read()
                executed = build_and_run(self, source, EXAMPLE_INPUT.get(example_name, ""))
                self.assertEqual(executed.returncode, 0)
                self.assertEqual(executed.stdout, expected_output)


if __name__ == "__main__":
    unittest.main()
