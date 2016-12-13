import sys

from exactly_lib.act_phase_setups import command_line
from exactly_lib.cli import main_program
from exactly_lib.default.default_main_program import MainProgram
from exactly_lib.default.program_modes.test_case import default_instructions_setup, \
    instruction_name_and_argument_splitter
from exactly_lib.processing.preprocessor import IdentityPreprocessor
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.util.std import StdOutputFiles


def default_main_program() -> main_program.MainProgram:
    return MainProgram(StdOutputFiles(sys.stdout,
                                      sys.stderr),
                       instruction_name_and_argument_splitter.splitter,
                       default_instructions_setup.INSTRUCTIONS_SETUP,
                       TestCaseHandlingSetup(command_line.act_phase_setup(),
                                             IdentityPreprocessor()))


def main() -> int:
    return default_main_program().execute(sys.argv[1:])
