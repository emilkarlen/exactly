from shellcheck_lib.cli.argument_parsing_of_act_phase_setup import INTERPRETER_FOR_TEST
from shellcheck_lib.default import default_main_program as sut
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib_test.util.process import SubProcessResult
from shellcheck_lib_test.util.str_std_out_files import StringStdOutFiles

ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE = ('--interpreter', INTERPRETER_FOR_TEST)

ARGUMENTS_FOR_TEST_INTERPRETER = list(ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE)


def arguments_for_test_interpreter_and_more_tuple(additional_args: iter) -> tuple:
    return ARGUMENTS_FOR_TEST_INTERPRETER_TUPLE + tuple(additional_args)


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


empty_instructions_setup = InstructionsSetup(
        {},
        {},
        {},
        {})


def execute_main_program(arguments: list,
                         instructions_setup: InstructionsSetup = empty_instructions_setup) -> SubProcessResult:
    str_std_out_files = StringStdOutFiles()
    program = sut.MainProgram(str_std_out_files.stdout_files,
                              name_argument_splitter,
                              instructions_setup)
    exit_status = program.execute(arguments)
    str_std_out_files.finish()
    return SubProcessResult(exit_status,
                            str_std_out_files.stdout_contents,
                            str_std_out_files.stderr_contents)
