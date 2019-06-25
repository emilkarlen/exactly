import argparse
import pathlib
import stat
from typing import List, Tuple

from exactly_lib import program_info
from exactly_lib.cli.definitions import common_cli_options as common_opts
from exactly_lib.cli.definitions.program_modes.help import arguments_for as help_args
from exactly_lib.cli.definitions.program_modes.test_suite import command_line_options as opts
from exactly_lib.cli.program_modes.common.argument_parsing_of_actor import \
    resolve_actor_from_argparse_argument
from exactly_lib.definitions import formatting
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import actors
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import suite_reporters as reporters
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.util.argument_parsing_utils import ArgumentParsingError, \
    parse_args__raise_exception_instead_of_exiting_on_error, \
    parse_known_args__raise_exception_instead_of_exiting_on_error
from exactly_lib.util.cli_syntax import short_and_long_option_syntax
from .settings import TestSuiteExecutionSettings


def parse(default: TestCaseHandlingSetup,
          argv: List[str]) -> TestSuiteExecutionSettings:
    """
    :raises ArgumentParsingError Invalid usage
    """
    return _Parser(default).parse(argv)


def parse_known_args(default: TestCaseHandlingSetup,
                     argv: List[str]) -> Tuple[TestSuiteExecutionSettings, List[str]]:
    """
    :raises ArgumentParsingError Invalid usage
    """
    return _Parser(default).parse_known_args(argv)


class _Parser:
    def __init__(self, default: TestCaseHandlingSetup):
        self.default = default
        from exactly_lib.test_suite.reporters.junit import JUnitRootSuiteProcessingReporter
        from exactly_lib.test_suite.reporters.simple_progress_reporter import SimpleProgressRootSuiteProcessingReporter
        self.reporter_name_2_reporter = {
            reporters.JUNIT_REPORTER.singular_name: JUnitRootSuiteProcessingReporter,
            reporters.PROGRESS_REPORTER.singular_name: SimpleProgressRootSuiteProcessingReporter,
        }
        self.reporter_names = sorted(list(self.reporter_name_2_reporter.keys()))
        self.default_reporter_name = reporters.DEFAULT_REPORTER.singular_name

    def parse(self, argv: List[str]) -> TestSuiteExecutionSettings:
        argument_parser = self._new_argument_parser()
        namespace = parse_args__raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                            argv)
        return self._execution_settings(namespace)

    def parse_known_args(self, argv: List[str]) -> Tuple[TestSuiteExecutionSettings, List[str]]:
        argument_parser = self._new_argument_parser()
        namespace, remaining_args = parse_known_args__raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                                  argv)
        execution_settings = self._execution_settings(namespace)
        return execution_settings, remaining_args

    def _execution_settings(self, namespace: argparse.Namespace) -> TestSuiteExecutionSettings:
        actor = resolve_actor_from_argparse_argument(self.default.actor,
                                                     namespace.actor)
        suite_file_path = self._resolve_file_path(namespace.file)
        return TestSuiteExecutionSettings(self._resolve_reporter(vars(namespace)),
                                          TestCaseHandlingSetup(ActPhaseSetup(actor),
                                                                self.default.preprocessor),
                                          suite_file_path,
                                          )

    def _resolve_file_path(self, file_argument: str) -> pathlib.Path:
        suite_file_path = pathlib.Path(file_argument)
        try:
            stat_mode = suite_file_path.stat().st_mode
        except FileNotFoundError as ex:
            raise ArgumentParsingError('Files does not exist: ' + file_argument)

        if stat.S_ISREG(stat_mode):
            return suite_file_path
        elif stat.S_ISDIR(stat_mode):
            suite_file_path = suite_file_path / file_names.DEFAULT_SUITE_FILE
            if suite_file_path.is_file():
                return suite_file_path
            else:
                raise ArgumentParsingError('{} is a directory, but do not contain the default suite file {}'.format(
                    file_argument,
                    file_names.DEFAULT_SUITE_FILE,
                ))
        else:
            raise ArgumentParsingError('Neither a file nor a directory: ' + file_argument)

    def _resolve_reporter(self, namespace: dict):
        reporter_name = self.default_reporter_name
        if opts.OPTION_FOR_REPORTER__LONG in namespace:
            reporter_list = namespace[opts.OPTION_FOR_REPORTER__LONG]
            if reporter_list is not None and len(reporter_list) == 1:
                reporter_name = reporter_list[0]
        return self.reporter_name_2_reporter[reporter_name]()

    def _new_argument_parser(self) -> argparse.ArgumentParser:
        ret_val = argparse.ArgumentParser(description=misc_texts.SUITE_COMMAND_SINGLE_LINE_DESCRIPTION,
                                          prog=program_info.PROGRAM_NAME + ' ' + common_opts.SUITE_COMMAND)
        ret_val.add_argument('file',
                             metavar=opts.TEST_SUITE_FILE_ARGUMENT,
                             type=str,
                             help='The test suite file.')
        ret_val.add_argument(short_and_long_option_syntax.long_syntax(opts.OPTION_FOR_REPORTER__LONG),
                             metavar=opts.REPORTER_OPTION_ARGUMENT,
                             nargs=1,
                             choices=self.reporter_names,
                             help=self._reporter_option_description())
        ret_val.add_argument(short_and_long_option_syntax.long_syntax(common_opts.OPTION_FOR_ACTOR__LONG),
                             metavar=common_opts.ACTOR_OPTION_ARGUMENT,
                             nargs=1,
                             help=_ACTOR_OPTION_DESCRIPTION.format(
                                 ARGUMENT=common_opts.ACTOR_OPTION_ARGUMENT,
                                 INTERPRETER_ACTOR_TERM=formatting.entity(
                                     actors.SOURCE_INTERPRETER_ACTOR.singular_name),
                                 ACTOR_CONCEPT=formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
                                 shell_syntax_concept=formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
                             ))
        return ret_val

    def _reporter_option_description(self) -> str:
        formatted_names = [formatting.cli_argument_option_string(name)
                           for name in self.reporter_names]
        formatted_default_name = formatting.cli_argument_option_string(self.default_reporter_name)
        help_option = ' '.join(
            help_args.complete_help_for(help_args.concept_single(concepts.SUITE_REPORTER_CONCEPT_INFO.singular_name)))
        return _REPORTER_OPTION_DESCRIPTION_TEMPLATE.format(reporter_names=','.join(formatted_names),
                                                            default_reporter_name=formatted_default_name,
                                                            help_option=help_option)


_REPORTER_OPTION_DESCRIPTION_TEMPLATE = """\
How to report the result of the suite. Options: {reporter_names} (default {default_reporter_name}).
Use "{help_option}" for more info.
"""

_ACTOR_OPTION_DESCRIPTION = """\
Specifies the {INTERPRETER_ACTOR_TERM} {ACTOR_CONCEPT}, by giving the program that serves as the interpreter.

{ARGUMENT} is an absolute path followed by optional arguments (using {shell_syntax_concept}).

Note that an {ACTOR_CONCEPT} specified in the test suite or individual test cases
has precedence over the {ACTOR_CONCEPT} given here.
"""
