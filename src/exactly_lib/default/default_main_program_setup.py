import sys

from exactly_lib.cli import main_program
from exactly_lib.default import instruction_name_and_argument_splitter
from exactly_lib.default.default_main_program import MainProgram, TestCaseDefinitionForMainProgram
from exactly_lib.default.program_modes import test_suite
from exactly_lib.default.program_modes.test_case import builtin_symbols
from exactly_lib.default.program_modes.test_case import default_instructions_setup
from exactly_lib.default.program_modes.test_case.test_case_handling_setup import test_case_handling_setup
from exactly_lib.util.std import StdOutputFiles


def default_main_program() -> main_program.MainProgram:
    return MainProgram(StdOutputFiles(sys.stdout,
                                      sys.stderr),
                       TestCaseDefinitionForMainProgram(instruction_name_and_argument_splitter.splitter,
                                                        default_instructions_setup.INSTRUCTIONS_SETUP,
                                                        builtin_symbols.ALL,
                                                        ),
                       test_suite.test_suite_definition(),
                       test_case_handling_setup())


def main() -> int:
    return default_main_program().execute(sys.argv[1:])
