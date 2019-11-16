import argparse
import pathlib
import shlex
from typing import List, Dict, Tuple

from exactly_lib import program_info
from exactly_lib.cli.definitions import common_cli_options as common_opts
from exactly_lib.cli.definitions.program_modes.test_case import command_line_options as opt
from exactly_lib.cli.program_modes.common.argument_parsing_of_actor import \
    resolve_actor_from_argparse_argument
from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.actors import SOURCE_INTERPRETER_ACTOR
from exactly_lib.definitions.entity.concepts import SDS_CONCEPT_INFO
from exactly_lib.definitions.misc_texts import IS_A_SHELL_CMD
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.processing.standalone.settings import ReportingOption, TestCaseExecutionSettings
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.argument_parsing_utils import parse_args__raise_exception_instead_of_exiting_on_error, \
    parse_known_args__raise_exception_instead_of_exiting_on_error
from exactly_lib.util.cli_syntax import short_and_long_option_syntax
from exactly_lib.util.messages import grammar_options_syntax
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse_known_args(
        default: TestCaseHandlingSetup,
        default_sandbox_root_dir_name_resolver: SandboxRootDirNameResolver,
        argv: List[str],
        commands: Dict[str, str]) -> Tuple[TestCaseExecutionSettings, List[str]]:
    """
    :raises ArgumentParsingError Invalid usage
    """
    argument_parser = _new_argument_parser(commands)
    namespace, remaining_args = parse_known_args__raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                              argv)
    settings = _settings_from_namespace(default,
                                        default_sandbox_root_dir_name_resolver,
                                        namespace)
    return settings, remaining_args


def parse(default: TestCaseHandlingSetup,
          default_sandbox_root_dir_name_resolver: SandboxRootDirNameResolver,
          argv: List[str],
          commands: Dict[str, str]) -> TestCaseExecutionSettings:
    """
    :raises ArgumentParsingError Invalid usage
    """
    argument_parser = _new_argument_parser(commands)
    namespace = parse_args__raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                        argv)
    return _settings_from_namespace(default,
                                    default_sandbox_root_dir_name_resolver,
                                    namespace)


def _settings_from_namespace(default: TestCaseHandlingSetup,
                             default_sandbox_root_dir_name_resolver: SandboxRootDirNameResolver,
                             namespace: argparse.Namespace) -> TestCaseExecutionSettings:
    output = ReportingOption.STATUS_CODE

    if namespace.act:
        output = ReportingOption.ACT_PHASE_OUTPUT
    elif namespace.keep:
        output = ReportingOption.SANDBOX_DIRECTORY_STRUCTURE_ROOT
    actor = resolve_actor_from_argparse_argument(default.actor,
                                                 namespace.actor)
    preprocessor = _parse_preprocessor(default.preprocessor,
                                       namespace.preprocessor)
    actual_handling_setup = TestCaseHandlingSetup(ActPhaseSetup(actor), preprocessor)
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
                                     sandbox_root_dir_resolver=default_sandbox_root_dir_name_resolver,
                                     run_as_part_of_explicit_suite=suite_file)


def _resolve_and_fail_if_is_not_an_existing_file(test_case_file_path) -> pathlib.Path:
    return argument_parsing_utils.resolve_existing_path(test_case_file_path)


def _new_argument_parser(commands: Dict[str, str]) -> argparse.ArgumentParser:
    def command_description(n_d) -> str:
        return '%s - %s' % (n_d[0], n_d[1])

    command_descriptions = '\n'.join(map(command_description, commands.items()))
    ret_val = argparse.ArgumentParser(prog=program_info.PROGRAM_NAME,
                                      description='Runs an {pgm} test case or test suite.'.format(
                                          pgm=formatting.program_name(program_info.PROGRAM_NAME)))
    ret_val.add_argument('--version', action='version', version='%(prog)s ' + program_info.VERSION)

    ret_val.add_argument('file',
                         metavar='[FILE|COMMAND]',
                         type=str,
                         help="""A test case file, or one of the commands {commands}.
                         {command_descriptions}
                         """.format(commands=grammar_options_syntax.alternatives_list(commands.keys()),
                                    command_descriptions=command_descriptions))
    ret_val.add_argument(short_and_long_option_syntax.short_syntax(opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT),
                         short_and_long_option_syntax.long_syntax(opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG),
                         default=False,
                         action="store_true",
                         help=TEXT_PARSER.format(KEEPING_SANDBOX_OPTION_DESCRIPTION))
    ret_val.add_argument(short_and_long_option_syntax.long_syntax(opt.OPTION_FOR_EXECUTING_ACT_PHASE__LONG),
                         default=False,
                         action="store_true",
                         help=TEXT_PARSER.format(EXECUTING_ACT_PHASE_OPTION_DESCRIPTION))
    ret_val.add_argument(short_and_long_option_syntax.long_syntax(
        common_opts.OPTION_FOR_ACTOR__LONG),
        metavar=common_opts.ACTOR_OPTION_ARGUMENT,
        nargs=1,
        help=TEXT_PARSER.format(ACTOR_OPTION_DESCRIPTION))
    ret_val.add_argument(short_and_long_option_syntax.long_syntax(opt.OPTION_FOR_SUITE__LONG),
                         metavar=opt.SUITE_OPTION_METAVAR,
                         nargs=1,
                         help=TEXT_PARSER.format(SUITE_OPTION_DESCRIPTION))
    ret_val.add_argument(short_and_long_option_syntax.long_syntax(opt.OPTION_FOR_PREPROCESSOR__LONG),
                         metavar=opt.PREPROCESSOR_OPTION_ARGUMENT,
                         nargs=1,
                         help=TEXT_PARSER.format(PREPROCESSOR_OPTION_DESCRIPTION))
    return ret_val


def _parse_preprocessor(default_preprocessor: Preprocessor,
                        preprocessor_argument) -> Preprocessor:
    if preprocessor_argument is None:
        return default_preprocessor
    else:
        return PreprocessorViaExternalProgram(shlex.split(preprocessor_argument[0]))


ACTOR_OPTION_DESCRIPTION = """\
Specifies the {INTERPRETER_ACTOR_TERM} {ACTOR_CONCEPT}, by giving the program that serves as the interpreter.


{interpreter_program} {is_a_shell_cmd}


Note that an {ACTOR_CONCEPT} specified in the test case has precedence over the
{ACTOR_CONCEPT} given here.
"""

SUITE_OPTION_DESCRIPTION = """\
Runs the test case as if it were part of the given suite.


This overrides the default suite file "{default_suite_file}".
"""

EXECUTING_ACT_PHASE_OPTION_DESCRIPTION = """\
{phase[before_assert]:syntax} and {phase[assert]:syntax} are skipped;
and instead of "reporting" the result,
the outcome of {phase[act]:syntax} is emitted:


output on stdout/stderr from {phase[act]:syntax} becomes the output on stdout/stderr;

the exit code from {phase[act]:syntax} becomes the exit code from the program.


If an error occurs, the normal error information is emitted to stderr
(following the output from {phase[act]:syntax}).
"""

KEEPING_SANDBOX_OPTION_DESCRIPTION = """\
Runs the test case as normal, but the {sandbox} is preserved,
and it's root directory is the only output on stdout.

If execution of the test case cannot be started (due to invalid syntax, e.g.),
then nothing is output on stdout.
"""

PREPROCESSOR_OPTION_DESCRIPTION = """\
{concept_single_line_description}.


{preprocessor} {is_a_shell_cmd}
"""

TEXT_PARSER = TextParser({
    'phase': PHASE_NAME_DICTIONARY,
    'preprocessor': opt.PREPROCESSOR_OPTION_ARGUMENT,
    'sandbox': formatting.concept_(SDS_CONCEPT_INFO),
    'interpreter_program': common_opts.ACTOR_OPTION_ARGUMENT,
    'INTERPRETER_ACTOR_TERM': formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name),
    'ACTOR_CONCEPT': concepts.ACTOR_CONCEPT_INFO.singular_name,
    'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
    'is_a_shell_cmd': IS_A_SHELL_CMD,
    'concept_single_line_description': concepts.PREPROCESSOR_CONCEPT_INFO.single_line_description_str,
    'default_suite_file': file_names.DEFAULT_SUITE_FILE,
})
