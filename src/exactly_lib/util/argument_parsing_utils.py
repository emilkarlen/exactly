import argparse
import pathlib
from typing import List, Callable, TypeVar, Tuple


class ArgumentParsingError(Exception):
    """
    Indicates an invalid command line - a command line that the
    ArgumentParser cannot parse.
    """

    def __init__(self, error_message: str):
        self.error_message = error_message


def resolve_existing_path(path_to_resolve: pathlib.Path) -> pathlib.Path:
    """
    raises ArgumentParsingError: path_to_resolve is not an existing file
    """
    try:
        resolved = path_to_resolve.resolve()
        if not resolved.exists():
            raise ArgumentParsingError('File does not exist: ' + str(resolved))
        return resolved
    except FileNotFoundError as ex:
        raise ArgumentParsingError(str(ex))


def parse_args__raise_exception_instead_of_exiting_on_error(parser: argparse.ArgumentParser,
                                                            arguments: List[str]) -> argparse.Namespace:
    """
    Corresponds to argparse.ArgumentParser.parse_args.

    But instead of exiting on error, a ArgumentParsingException is raised.
    """

    def do_parse() -> argparse.Namespace:
        return parser.parse_args(arguments)

    return _raise_exception_instead_of_exiting_on_error(do_parse)


def parse_known_args__raise_exception_instead_of_exiting_on_error(
        parser: argparse.ArgumentParser,
        arguments: List[str]
) -> Tuple[argparse.Namespace, List[str]]:
    """
    Corresponds to argparse.ArgumentParser.parse_known_args.

    But instead of exiting on error, a ArgumentParsingException is raised.
    """

    def do_parse() -> Tuple[argparse.Namespace, List[str]]:
        return parser.parse_known_args(arguments)

    return _raise_exception_instead_of_exiting_on_error(do_parse)


PARSE_RESULT = TypeVar('PARSE_RESULT')


def _raise_exception_instead_of_exiting_on_error(parse_action: Callable[[], PARSE_RESULT]) -> PARSE_RESULT:
    """
    Corresponds to argparse.ArgumentParser.parse_args.

    But instead of exiting on error, a ArgumentParsingException is raised.
    """
    original_error_handler = argparse.ArgumentParser.error

    def error_handler(the_parser: argparse.ArgumentParser, the_message: str):
        raise ArgumentParsingError(the_message)

    try:
        argparse.ArgumentParser.error = error_handler
        return parse_action()
    finally:
        argparse.ArgumentParser.error = original_error_handler
