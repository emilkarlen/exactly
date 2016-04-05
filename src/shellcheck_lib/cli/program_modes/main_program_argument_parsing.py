import argparse
import pathlib
import shlex

from shellcheck_lib.cli.argument_parsing_of_act_phase_setup import resolve_act_phase_setup_from_argparse_argument
from shellcheck_lib.cli.cli_environment import program_info
from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_KEEPING_SANDBOX_DIRECTORY, \
    OPTION_FOR_PREPROCESSOR
from shellcheck_lib.cli.program_modes.test_case.settings import Output, TestCaseExecutionSettings
from shellcheck_lib.test_case.preprocessor import IdentityPreprocessor, PreprocessorViaExternalProgram
from shellcheck_lib.util import argument_parsing_utils


def _parse_preprocessor(preprocessor_argument):
    if preprocessor_argument is None:
        return IdentityPreprocessor()
    else:
        return PreprocessorViaExternalProgram(shlex.split(preprocessor_argument[0]))


def parse(argv: list,
          commands: dict) -> TestCaseExecutionSettings:
    """
    :raises ArgumentParsingError Invalid usage
    """
    output = Output.STATUS_CODE
    is_keep_execution_directory_root = False
    argument_parser = _new_argument_parser(commands)
    namespace = argument_parsing_utils.raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                   argv)
    if namespace.act:
        output = Output.ACT_PHASE_OUTPUT
    elif namespace.keep:
        output = Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT
        is_keep_execution_directory_root = True
    act_phase_setup = resolve_act_phase_setup_from_argparse_argument(namespace.interpreter)
    preprocessor = _parse_preprocessor(namespace.preprocessor)
    return TestCaseExecutionSettings(pathlib.Path(namespace.file),
                                     pathlib.Path(namespace.file).parent.resolve(),
                                     output,
                                     preprocessor,
                                     act_phase_setup,
                                     is_keep_execution_directory_root=is_keep_execution_directory_root)


def _new_argument_parser(commands: dict) -> argparse.ArgumentParser:
    def command_description(n_d) -> str:
        return '%s - %s' % (n_d[0], n_d[1])

    command_descriptions = '\n'.join(map(command_description, commands.items()))
    ret_val = argparse.ArgumentParser(prog=program_info.PROGRAM_NAME,
                                      description='Execute Shellcheck test case or test suite.')
    ret_val.add_argument('--version', action='version', version='%(prog)s ' + program_info.VERSION)

    ret_val.add_argument('file',
                         metavar='[FILE|COMMAND]',
                         type=str,
                         help="""A test case file, or one of the commands {commands}.
                         {command_descriptions}
                         """.format(commands='|'.join(commands.keys()),
                                    command_descriptions=command_descriptions))
    ret_val.add_argument('-k', OPTION_FOR_KEEPING_SANDBOX_DIRECTORY,
                         default=False,
                         action="store_true",
                         help="""\
                        Executes a test case as normal, but Execution Directory Structure is preserved,
                        and it's root directory is the only output on stdout.""")
    ret_val.add_argument('--act',
                         default=False,
                         action="store_true",
                         help="""\
                        Executes the full test case, but instead of "reporting" the result,
                        the output from the act phase script is emitted:
                        Output on stdout/stderr from the script is printed to stdout/stderr.
                        The exit code from the act script becomes the exit code from the program.""")
    ret_val.add_argument('--interpreter',
                         metavar="INTERPRETER",
                         nargs=1,
                         help="""\
                        Executable that executes the script of the act phase.""")
    ret_val.add_argument(OPTION_FOR_PREPROCESSOR,
                         metavar="SHELL-COMMAND",
                         nargs=1,
                         help="""\
                        Command that preprocesses the test case before it is parsed.

                        The name of the test case file is given to the command as the last argument.

                        The command should output the processed test case on stdout.

                        SHELL-COMMAND is parsed according to shell syntax.

                        If the exit code from the preprocessor is non-zero,
                        then processing is considered to have failed.
                        """)
    return ret_val
