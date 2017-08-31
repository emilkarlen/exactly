import argparse
import pathlib

from exactly_lib import program_info
from exactly_lib.cli.argument_parsing_of_act_phase_setup import resolve_act_phase_setup_from_argparse_argument
from exactly_lib.cli.cli_environment import common_cli_options as common_opts
from exactly_lib.cli.cli_environment.program_modes.help import arguments_for as help_args
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as case_opts
from exactly_lib.cli.cli_environment.program_modes.test_suite import command_line_options as opts
from exactly_lib.help.actors.names_and_cross_references import SOURCE_INTERPRETER_ACTOR
from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
from exactly_lib.help.concepts.plain_concepts.shell_syntax import SHELL_SYNTAX_CONCEPT
from exactly_lib.help.concepts.plain_concepts.suite_reporter import SUITE_REPORTER_CONCEPT
from exactly_lib.help.suite_reporters import names_and_cross_references as reporters
from exactly_lib.help_texts.names import formatting
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from .settings import TestSuiteExecutionSettings


def parse(default: TestCaseHandlingSetup,
          argv: list) -> TestSuiteExecutionSettings:
    """
    :raises ArgumentParsingError Invalid usage
    """
    return _Parser(default).parse(argv)


class _Parser:
    def __init__(self, default: TestCaseHandlingSetup):
        self.default = default
        from exactly_lib.test_suite.reporters.junit import JUnitRootSuiteReporterFactory
        from exactly_lib.test_suite.reporters.simple_progress_reporter import SimpleProgressRootSuiteReporterFactory
        self.reporter_name_2_factory = {
            reporters.JUNIT_REPORTER.singular_name: JUnitRootSuiteReporterFactory,
            reporters.PROGRESS_REPORTER.singular_name: SimpleProgressRootSuiteReporterFactory,
        }
        self.reporter_names = sorted(list(self.reporter_name_2_factory.keys()))
        self.default_reporter_name = reporters.DEFAULT_REPORTER.singular_name

    def parse(self, argv: list) -> TestSuiteExecutionSettings:
        argument_parser = self._new_argument_parser()
        namespace = argument_parsing_utils.raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                       argv)
        act_phase_setup = resolve_act_phase_setup_from_argparse_argument(self.default.default_act_phase_setup,
                                                                         namespace.actor)
        return TestSuiteExecutionSettings(self._resolve_reporter_factory(vars(namespace)),
                                          TestCaseHandlingSetup(act_phase_setup,
                                                                self.default.preprocessor),
                                          argument_parsing_utils.resolve_path(pathlib.Path(namespace.file)),
                                          )

    def _resolve_reporter_factory(self,
                                  namespace: dict):
        reporter_name = self.default_reporter_name
        if opts.OPTION_FOR_REPORTER__LONG in namespace:
            reporter_list = namespace[opts.OPTION_FOR_REPORTER__LONG]
            if reporter_list is not None and len(reporter_list) == 1:
                reporter_name = reporter_list[0]
        return self.reporter_name_2_factory[reporter_name]()

    def _new_argument_parser(self) -> argparse.ArgumentParser:
        ret_val = argparse.ArgumentParser(description='Runs a test suite',
                                          prog=program_info.PROGRAM_NAME + ' ' + common_opts.SUITE_COMMAND)
        ret_val.add_argument('file',
                             metavar=opts.TEST_SUITE_FILE_ARGUMENT,
                             type=str,
                             help='The test suite file.')
        ret_val.add_argument(long_option_syntax(opts.OPTION_FOR_REPORTER__LONG),
                             metavar=opts.REPORTER_OPTION_ARGUMENT,
                             nargs=1,
                             choices=self.reporter_names,
                             help=self._reporter_option_description())
        ret_val.add_argument(long_option_syntax(opts.OPTION_FOR_ACTOR__LONG),
                             metavar=case_opts.ACTOR_OPTION_ARGUMENT,
                             nargs=1,
                             help=_ACTOR_OPTION_DESCRIPTION.format(
                                 ARGUMENT=case_opts.ACTOR_OPTION_ARGUMENT,
                                 INTERPRETER_ACTOR_TERM=formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name),
                                 ACTOR_CONCEPT=formatting.concept(ACTOR_CONCEPT.singular_name()),
                                 shell_syntax_concept=formatting.concept(SHELL_SYNTAX_CONCEPT.singular_name()),
                             ))
        return ret_val

    def _reporter_option_description(self) -> str:
        formatted_names = [formatting.cli_argument_option_string(name)
                           for name in self.reporter_names]
        formatted_default_name = formatting.cli_argument_option_string(self.default_reporter_name)
        help_option = ' '.join(
            help_args.complete_help_for(help_args.concept_single(SUITE_REPORTER_CONCEPT.singular_name())))
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
