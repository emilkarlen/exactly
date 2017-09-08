import argparse
import pathlib


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


def raise_exception_instead_of_exiting_on_error(parser: argparse.ArgumentParser,
                                                arguments: list):
    """
    Corresponds to argparse.ArgumentParser.parse_args.

    But instead of exiting on error, a ArgumentParsingException is raised.
    """
    original_error_handler = argparse.ArgumentParser.error

    def error_handler(the_parser: argparse.ArgumentParser, the_message: str):
        raise ArgumentParsingError(the_message)

    try:
        argparse.ArgumentParser.error = error_handler
        return parser.parse_args(arguments)
    finally:
        argparse.ArgumentParser.error = original_error_handler
