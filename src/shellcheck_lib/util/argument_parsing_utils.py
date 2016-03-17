import argparse


class ArgumentParsingError(Exception):
    """
    Indicates an invalid command line - a command line that the
    ArgumentParser cannot parse.
    """

    def __init__(self,
                 argument_parser: argparse.ArgumentParser,
                 error_message: str):
        self.argument_parser = argument_parser
        self.error_message = error_message


def raise_exception_instead_of_exiting_on_error(parser: argparse.ArgumentParser,
                                                arguments: list):
    """
    Corresponds to argparse.ArgumentParser.parse_args.

    But instead of exiting on error, a ArgumentParsingException is raised.
    """
    original_error_handler = argparse.ArgumentParser.error

    def error_handler(the_parser: argparse.ArgumentParser, the_message: str):
        raise ArgumentParsingError(the_parser, the_message)

    try:
        argparse.ArgumentParser.error = error_handler
        return parser.parse_args(arguments)
    finally:
        argparse.ArgumentParser.error = original_error_handler
