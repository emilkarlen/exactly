from exactly_lib.cli.argument_parsing_of_act_phase_setup import INTERPRETER_FOR_TEST
from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_ACTOR
from exactly_lib.default import default_main_program as sut
from exactly_lib.default.program_modes.test_suite.reporting import DefaultRootSuiteReporterFactory
from exactly_lib.test_case.instruction_setup import InstructionsSetup
from exactly_lib_test.cli.test_resources.test_case_handling_setup import test_case_handling_setup
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles

ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE = (OPTION_FOR_ACTOR, INTERPRETER_FOR_TEST)

ARGUMENTS_FOR_TEST_INTERPRETER = list(ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE)


def arguments_for_test_interpreter_and_more_tuple(additional_args: iter) -> tuple:
    return ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE + tuple(additional_args)


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


EMPTY_INSTRUCTIONS_SETUP = InstructionsSetup(
    {},
    {},
    {},
    {},
    {})


def execute_main_program(arguments: list,
                         instructions_setup: InstructionsSetup = EMPTY_INSTRUCTIONS_SETUP) -> SubProcessResult:
    str_std_out_files = StringStdOutFiles()
    program = sut.MainProgram(str_std_out_files.stdout_files,
                              name_argument_splitter,
                              instructions_setup,
                              test_case_handling_setup(),
                              DefaultRootSuiteReporterFactory())
    exit_status = program.execute(arguments)
    str_std_out_files.finish()
    return SubProcessResult(exit_status,
                            str_std_out_files.stdout_contents,
                            str_std_out_files.stderr_contents)
