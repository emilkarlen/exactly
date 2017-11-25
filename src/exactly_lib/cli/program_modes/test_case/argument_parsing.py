import argparse
import pathlib
import shlex

from exactly_lib import program_info
from exactly_lib.cli.argument_parsing_of_act_phase_setup import resolve_act_phase_setup_from_argparse_argument
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.cli.program_modes.test_case.settings import ReportingOption, TestCaseExecutionSettings
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity.actors import SOURCE_INTERPRETER_ACTOR
from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.cli_syntax.render.cli_program_syntax import short_option_syntax
from exactly_lib.util.messages import grammar_options_syntax


def parse(default: TestCaseHandlingSetup,
          argv: list,
          commands: dict) -> TestCaseExecutionSettings:
    """
    :raises ArgumentParsingError Invalid usage
    """
    output = ReportingOption.STATUS_CODE
    argument_parser = _new_argument_parser(commands)
    namespace = argument_parsing_utils.raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                   argv)
    if namespace.act:
        output = ReportingOption.ACT_PHASE_OUTPUT
    elif namespace.keep:
        output = ReportingOption.SANDBOX_DIRECTORY_STRUCTURE_ROOT
    act_phase_setup = resolve_act_phase_setup_from_argparse_argument(default.act_phase_setup,
                                                                     namespace.actor)
    preprocessor = _parse_preprocessor(default.preprocessor,
                                       namespace.preprocessor)
    actual_handling_setup = TestCaseHandlingSetup(act_phase_setup, preprocessor)
    test_case_file_path = pathlib.Path(namespace.file)

    suite_file = None
    if namespace.suite:
        suite_file = pathlib.Path(namespace.suite[0])
        _resolve_and_fail_if_is_not_an_existing_file(suite_file)
    _resolve_and_fail_if_is_not_an_existing_file(test_case_file_path)
    return TestCaseExecutionSettings(test_case_file_path,
                                     _resolve_and_fail_if_is_not_an_existing_file(test_case_file_path.parent),
                                     output,
                                     actual_handling_setup,
                                     suite_to_read_config_from=suite_file)


def _resolve_and_fail_if_is_not_an_existing_file(test_case_file_path) -> pathlib.Path:
    return argument_parsing_utils.resolve_existing_path(test_case_file_path)


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
                         """.format(commands=grammar_options_syntax.alternatives_list(commands.keys()),
                                    command_descriptions=command_descriptions))
    ret_val.add_argument(short_option_syntax(opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT),
                         long_option_syntax(opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG),
                         default=False,
                         action="store_true",
                         help="""\
                        Executes a test case as normal, but Sandbox directory structure is preserved,
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
                         help=_ACTOR_OPTION_DESCRIPTION.format(
                             ARGUMENT=opt.ACTOR_OPTION_ARGUMENT,
                             INTERPRETER_ACTOR_TERM=formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name),
                             ACTOR_CONCEPT=concepts.ACTOR_CONCEPT_INFO.singular_name,
                             shell_syntax_concept=formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
                         ))
    ret_val.add_argument(long_option_syntax(opt.OPTION_FOR_SUITE__LONG),
                         metavar=opt.SUITE_OPTION_METAVAR,
                         nargs=1,
                         help=_SUITE_OPTION_DESCRIPTION)
    ret_val.add_argument(long_option_syntax(opt.OPTION_FOR_PREPROCESSOR__LONG),
                         metavar=opt.PREPROCESSOR_OPTION_ARGUMENT,
                         nargs=1,
                         help="""\
                        Command that preprocesses the test case before it is parsed.

                        The name of the test case file is given to the command as the last argument.

                        The command should output the processed test case on stdout.

                        {preprocessor} is parsed according to {shell_syntax_concept}.

                        If the exit code from the preprocessor is non-zero,
                        then processing is considered to have failed.
                        """.format(preprocessor=opt.PREPROCESSOR_OPTION_ARGUMENT,
                                   shell_syntax_concept=formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
                                   ))
    return ret_val


def _parse_preprocessor(default_preprocessor: Preprocessor,
                        preprocessor_argument) -> Preprocessor:
    if preprocessor_argument is None:
        return default_preprocessor
    else:
        return PreprocessorViaExternalProgram(shlex.split(preprocessor_argument[0]))


_ACTOR_OPTION_DESCRIPTION = """\
Specifies the {INTERPRETER_ACTOR_TERM} {ACTOR_CONCEPT}, by giving the program that serves as the interpreter.

{ARGUMENT} is an absolute path followed by optional arguments (using {shell_syntax_concept}).

Note that an {ACTOR_CONCEPT} specified in the test case has precedence over the
{ACTOR_CONCEPT} given here.
"""

_SUITE_OPTION_DESCRIPTION = """\
A test suite to read configuration from.

The test case is executed as if it were part of the given suite.
"""
