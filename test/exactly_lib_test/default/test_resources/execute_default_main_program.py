from exactly_lib.cli import main_program
from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.default.program_modes.test_suite import test_suite_definition
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.cli.test_resources.main_program_runner_utils import \
    first_char_is_name_and_rest_is_argument__splitter, EMPTY_INSTRUCTIONS_SETUP
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles


def execute_default_main_program(arguments: list,
                                 the_test_case_handling_setup: TestCaseHandlingSetup,
                                 instructions_setup: InstructionsSetup = EMPTY_INSTRUCTIONS_SETUP,
                                 name_and_argument_splitter=first_char_is_name_and_rest_is_argument__splitter,
                                 builtin_symbols: list = (),
                                 ) -> SubProcessResult:
    str_std_out_files = StringStdOutFiles()
    program = main_program.MainProgram(str_std_out_files.stdout_files,
                                       the_test_case_handling_setup,
                                       TestCaseDefinitionForMainProgram(
                                           name_and_argument_splitter,
                                           instructions_setup,
                                           list(builtin_symbols),
                                       ),
                                       test_suite_definition())
    exit_status = program.execute(arguments)
    str_std_out_files.finish()
    return SubProcessResult(exit_status,
                            str_std_out_files.stdout_contents,
                            str_std_out_files.stderr_contents)
