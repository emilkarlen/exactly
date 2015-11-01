from shellcheck_lib.cli import default_main_program as sut
from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib_test.util.str_std_out_files import StringStdOutFiles
from shellcheck_lib_test.util.process import SubProcessResult


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


instructions_setup = InstructionsSetup(
    {},
    {},
    {},
    {})


def execute_main_program(arguments: list) -> SubProcessResult:
    str_std_out_files = StringStdOutFiles()
    program = sut.MainProgram(str_std_out_files.stdout_files,
                              name_argument_splitter,
                              instructions_setup)
    exit_status = program.execute(arguments)
    str_std_out_files.finish()
    return SubProcessResult(exit_status,
                            str_std_out_files.stdout_contents,
                            str_std_out_files.stderr_contents)
