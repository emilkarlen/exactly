import io
import sys

from exactly_lib import program_info
from exactly_lib.cli import main_program
from exactly_lib.cli.test_case_def import TestCaseDefinitionForMainProgram
from exactly_lib.cli_default.program_modes import test_suite
from exactly_lib.cli_default.program_modes.test_case import builtin_symbols, default_instructions_setup, \
    test_case_handling_setup
from exactly_lib.common import instruction_name_and_argument_splitter
from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.util.file_utils.std import StdOutputFiles


def default_main_program() -> main_program.MainProgram:
    return main_program.MainProgram(test_case_handling_setup.setup(),
                                    sandbox_dir_resolving.mk_tmp_dir_with_prefix(program_info.PROGRAM_NAME + '-'),
                                    TestCaseDefinitionForMainProgram(
                                        TestCaseParsingSetup(instruction_name_and_argument_splitter.splitter,
                                                             default_instructions_setup.INSTRUCTIONS_SETUP,
                                                             ActPhaseParser()),
                                        builtin_symbols.ALL,
                                    ),
                                    test_suite.test_suite_definition(),
                                    io.DEFAULT_BUFFER_SIZE)


def default_output() -> StdOutputFiles:
    return StdOutputFiles(sys.stdout,
                          sys.stderr)


def main() -> int:
    return default_main_program().execute(sys.argv[1:], default_output())
