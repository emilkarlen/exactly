import argparse
import pathlib
import shlex

from exactly_lib import program_info
from exactly_lib.cli.argument_parsing_of_act_phase_setup import resolve_act_phase_setup_from_argparse_argument
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.cli.program_modes.test_case.settings import Output, TestCaseExecutionSettings
from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.cli_syntax.render.cli_program_syntax import short_option_syntax


def parse(default: TestCaseHandlingSetup,
          argv: list,
          commands: dict) -> TestCaseExecutionSettings:
    """
    :param default_preprocessor:
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
    act_phase_setup = resolve_act_phase_setup_from_argparse_argument(default.act_phase_setup,
                                                                     namespace.actor)
    preprocessor = _parse_preprocessor(default.preprocessor,
                                       namespace.preprocessor)
    actual_handling_setup = TestCaseHandlingSetup(act_phase_setup, preprocessor)
    return TestCaseExecutionSettings(pathlib.Path(namespace.file),
                                     pathlib.Path(namespace.file).parent.resolve(),
                                     output,
                                     actual_handling_setup,
                                     is_keep_execution_directory_root=is_keep_execution_directory_root)


def _new_argument_parser(commands: dict) -> argparse.ArgumentParser:
    def command_description(n_d) -> str:
        return '%s - %s' % (n_d[0], n_d[1])

    command_descriptions = '\n'.join(map(command_description, commands.items()))
    ret_val = argparse.ArgumentParser(prog=program_info.PROGRAM_NAME,
                                      description='Execute %s test case or test suite.' % program_info.PROGRAM_NAME)
    ret_val.add_argument('--version', action='version', version='%(prog)s ' + program_info.VERSION)

    ret_val.add_argument('file',
                         metavar='[FILE|COMMAND]',
                         type=str,
                         help="""A test case file, or one of the commands {commands}.
                         {command_descriptions}
                         """.format(commands='|'.join(commands.keys()),
                                    command_descriptions=command_descriptions))
    ret_val.add_argument(short_option_syntax(opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT),
                         long_option_syntax(opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG),
                         default=False,
                         action="store_true",
                         help="""\
                        Executes a test case as normal, but Execution Directory Structure is preserved,
                        and it's root directory is the only output on stdout.""")
    ret_val.add_argument(long_option_syntax(opt.OPTION_FOR_EXECUTING_ACT_PHASE__LONG),
                         default=False,
                         action="store_true",
                         help="""\
                        Executes the full test case, but instead of "reporting" the result,
                        the output from the act phase script is emitted:
                        Output on stdout/stderr from the script is printed to stdout/stderr.
                        The exit code from the act script becomes the exit code from the program.""")
    ret_val.add_argument(long_option_syntax(opt.OPTION_FOR_ACTOR__LONG),
                         metavar=opt.ACTOR_OPTION_ARGUMENT,
                         nargs=1,
                         help="""\
                        Executable that executes the script of the "act" phase.

                        The executable is given a single command line argument, which is the file
                        that contains the contents of the act phase.""")
    ret_val.add_argument(long_option_syntax(opt.OPTION_FOR_PREPROCESSOR__LONG),
                         metavar=opt.PREPROCESSOR_OPTION_ARGUMENT,
                         nargs=1,
                         help="""\
                        Command that preprocesses the test case before it is parsed.

                        The name of the test case file is given to the command as the last argument.

                        The command should output the processed test case on stdout.

                        {preprocessor} is parsed according to shell syntax.

                        If the exit code from the preprocessor is non-zero,
                        then processing is considered to have failed.
                        """.format(preprocessor=opt.PREPROCESSOR_OPTION_ARGUMENT))
    return ret_val


def _parse_preprocessor(default_preprocessor: Preprocessor,
                        preprocessor_argument) -> Preprocessor:
    if preprocessor_argument is None:
        return default_preprocessor
    else:
        return PreprocessorViaExternalProgram(shlex.split(preprocessor_argument[0]))
