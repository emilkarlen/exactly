"""Functionality for accessing a subset of the files in a directory."""
import pathlib

from exactly_lib.instructions.utils.parse.token_stream_parse import TokenParser
from exactly_lib.util.cli_syntax.elements import argument as a

NAME_SELECTOR_OPTION = a.option(long_name='name',
                                argument='PATTERN')


class DirContentsSubset:
    def files(self, directory: pathlib.Path) -> iter:
        """
        :param directory: A path that is an existing directory
        :return: Iterable of all files in the directory that is in the
        subset that the object represents.
        """
        raise NotImplementedError('abstract method')

    @property
    def restriction_descriptions(self) -> list:
        """
        A list of strings that each describe a restriction
        that must be met by a file to be included in the set.
        """
        raise NotImplementedError('abstract method')


class EveryFileInDir(DirContentsSubset):
    def files(self, directory: pathlib.Path) -> iter:
        return directory.iterdir()

    @property
    def restriction_descriptions(self) -> list:
        return []


class NameMatches(DirContentsSubset):
    def __init__(self, glob_pattern: str):
        self.glob_pattern = glob_pattern

    def files(self, directory: pathlib.Path) -> iter:
        return directory.glob(self.glob_pattern)

    @property
    def restriction_descriptions(self) -> list:
        return ['name matches glob pattern ' + self.glob_pattern]


def parse(parser: TokenParser) -> DirContentsSubset:
    glob_pattern = parser.consume_optional_option_with_mandatory_argument(NAME_SELECTOR_OPTION)
    if glob_pattern is not None:
        return NameMatches(glob_pattern.string)
    return EveryFileInDir()
