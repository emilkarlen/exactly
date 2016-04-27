import argparse
import pathlib

from shellcheck_lib import program_info
from shellcheck_lib.cli.argument_parsing_of_act_phase_setup import resolve_act_phase_setup_from_argparse_argument
from shellcheck_lib.cli.cli_environment.command_line_options import OPTION_FOR_ACTOR
from shellcheck_lib.util import argument_parsing_utils
from .settings import Settings


def parse(argv: list) -> Settings:
    """
    :raises ArgumentParsingError Invalid usage
    :param argv:
    :return:
    """
    argument_parser = _new_argument_parser()
    namespace = argument_parsing_utils.raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                   argv)
    return Settings(resolve_act_phase_setup_from_argparse_argument(namespace.actor),
                    pathlib.Path(namespace.file).resolve())


def _new_argument_parser() -> argparse.ArgumentParser:
    ret_val = argparse.ArgumentParser(description='Execute a Test Suite',
                                      prog=program_info.PROGRAM_NAME + ' suite')
    ret_val.add_argument('file',
                         metavar='FILE',
                         type=str,
                         help='The file containing the Test Suite')
    ret_val.add_argument(OPTION_FOR_ACTOR,
                         metavar="INTERPRETER",
                         nargs=1,
                         help="""\
                        Executable that executes the script of the act phase.
                        The interpreter is given a single command line argument, which is the file
                        that contains the contents of the act phase.""")
    return ret_val
