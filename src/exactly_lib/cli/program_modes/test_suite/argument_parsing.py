import argparse
import pathlib

from exactly_lib import program_info
from exactly_lib.cli.argument_parsing_of_act_phase_setup import resolve_act_phase_setup_from_argparse_argument
from exactly_lib.cli.cli_environment import common_cli_options as common_opts
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as case_opts
from exactly_lib.cli.cli_environment.program_modes.test_suite import command_line_options as opts
from exactly_lib.cli.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.util import argument_parsing_utils
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from .settings import Settings


def parse(default: TestCaseHandlingSetup,
          argv: list) -> Settings:
    """
    :raises ArgumentParsingError Invalid usage
    """
    argument_parser = _new_argument_parser()
    namespace = argument_parsing_utils.raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                   argv)
    return Settings(resolve_act_phase_setup_from_argparse_argument(default.act_phase_setup,
                                                                   namespace.actor),
                    pathlib.Path(namespace.file).resolve())


def _new_argument_parser() -> argparse.ArgumentParser:
    ret_val = argparse.ArgumentParser(description='Runs a test suite',
                                      prog=program_info.PROGRAM_NAME + ' ' + common_opts.SUITE_COMMAND)
    ret_val.add_argument('file',
                         metavar=opts.TEST_SUITE_FILE_ARGUMENT,
                         type=str,
                         help='The test suite file.')
    ret_val.add_argument(long_option_syntax(opts.OPTION_FOR_ACTOR__LONG),
                         metavar=case_opts.ACTOR_OPTION_ARGUMENT,
                         nargs=1,
                         help=_ACTOR_OPTION_DESCRIPTION.format(
                             INTERPRETER_ACTOR_TERM=case_opts.INTERPRETER_ACTOR_TERM
                         ))
    return ret_val


_ACTOR_OPTION_DESCRIPTION = """\
An {INTERPRETER_ACTOR_TERM} to use for every test case in the suite."""
