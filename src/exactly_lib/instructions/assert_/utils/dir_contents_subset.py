"""Functionality for accessing a subset of the files in a directory."""
import pathlib

from exactly_lib.section_document.parser_implementations.token_stream import TokenStream


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


def parse(token_stream: TokenStream) -> DirContentsSubset:
    return EveryFileInDir()
