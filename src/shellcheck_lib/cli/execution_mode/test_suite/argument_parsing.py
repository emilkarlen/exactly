import argparse
import pathlib

from shellcheck_lib.cli.argument_parsing_of_act_phase_setup import resolve_act_phase_setup_from_argparse_argument
from shellcheck_lib.general import argument_parsing_utils
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
    return Settings(resolve_act_phase_setup_from_argparse_argument(namespace.interpreter),
                    pathlib.Path(namespace.file).resolve())


def _new_argument_parser() -> argparse.ArgumentParser:
    ret_val = argparse.ArgumentParser(description='Execute a shellcheck Test Suite',
                                      prog='shellcheck suite')
    ret_val.add_argument('file',
                         metavar='FILE',
                         type=str,
                         help='The file containing the Test Suite')
    ret_val.add_argument('--interpreter',
                         metavar="INTERPRETER",
                         nargs=1,
                         help="""\
                        Executable that executes the script of the act phase.
                        The interpreter is given a single argument, which is the file
                        that contains the contents of the act phase.""")
    return ret_val
