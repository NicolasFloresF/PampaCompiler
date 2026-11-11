"""Compiles every program in examples/, runs it and checks its exit status.

Run from the repository root with: python -m unittest discover tests
"""

import os
import subprocess
import sys
import tempfile
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(TESTS_DIR)
EXAMPLES_DIR = os.path.join(REPO_DIR, "examples")
COMPILER = os.path.join(REPO_DIR, "__main__.py")
RUNTIME = os.path.join(TESTS_DIR, "runtime.s")

# Expected exit status of each example: the value its inicio function returns.
EXPECTED_EXIT_STATUS = {
    "arithmetic.por": 52,
    "precedence.por": 4,
    "conditionals.por": 2,
    "while_sum.por": 55,
    "for_factorial.por": 120,
    "nested_loops.por": 45,
    "gcd.por": 6,
    "logic.por": 2,
    "primes.por": 10,
}


def run_command(command: list[str], work_dir: str) -> subprocess.CompletedProcess:
    """Runs a command inside work_dir.

    Args:
        command (list[str]): Program and arguments.
        work_dir (str): Directory the command runs in.

    Returns:
        subprocess.CompletedProcess: Exit status and captured text output.
    """
    return subprocess.run(command, cwd=work_dir, capture_output=True, text=True, timeout=10, check=False)


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
    return run_command([sys.executable, COMPILER, "--file", program_path], work_dir)


def assemble_and_link(work_dir: str) -> subprocess.CompletedProcess:
    """Assembles work_dir/program.asm with the runtime and links them into work_dir/program.

    Args:
        work_dir (str): Directory holding program.asm.

    Returns:
        subprocess.CompletedProcess: Result of the first step that failed, or of the link.
    """
    steps = [
        ["as", "program.asm", "-o", "program.o"],
        ["as", RUNTIME, "-o", "runtime.o"],
        ["ld", "program.o", "runtime.o", "-o", "program"],
    ]
    for step in steps:
        result = run_command(step, work_dir)
        if result.returncode != 0:
            return result
    return result


def build_and_run(test_case: unittest.TestCase, source: str) -> int:
    """Compiles, links and runs source, failing test_case at the first step that fails.

    Args:
        test_case (unittest.TestCase): Test that receives the failure.
        source (str): Portugol source code.

    Returns:
        int: Exit status of the program, that is, the value returned by inicio.
    """
    with tempfile.TemporaryDirectory() as work_dir:
        compiled = compile_program(source, work_dir)
        test_case.assertEqual(compiled.returncode, 0, f"compiler failed:\n{compiled.stdout}{compiled.stderr}")

        linked = assemble_and_link(work_dir)
        test_case.assertEqual(linked.returncode, 0, f"assembler or linker failed:\n{linked.stderr}")

        return run_command(["./program"], work_dir).returncode


class ExamplesTest(unittest.TestCase):
    def test_every_example_has_an_expected_status(self):
        example_names = sorted(name for name in os.listdir(EXAMPLES_DIR) if name.endswith(".por"))
        self.assertEqual(example_names, sorted(EXPECTED_EXIT_STATUS))

    def test_examples_return_expected_status(self):
        for example_name, expected_status in EXPECTED_EXIT_STATUS.items():
            with self.subTest(example=example_name):
                with open(os.path.join(EXAMPLES_DIR, example_name)) as example_file:
                    source = example_file.read()
                self.assertEqual(build_and_run(self, source), expected_status)


if __name__ == "__main__":
    unittest.main()
