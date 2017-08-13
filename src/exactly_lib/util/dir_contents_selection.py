"""Functionality for accessing a subset of the files in a directory."""
import itertools
import pathlib

from exactly_lib.test_case_utils import file_properties


class DirContentsSelector:
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


class EveryFileInDir(DirContentsSelector):
    def files(self, directory: pathlib.Path) -> iter:
        return directory.iterdir()

    @property
    def restriction_descriptions(self) -> list:
        return []


class NamePatternSelector(DirContentsSelector):
    def __init__(self, glob_pattern: str):
        self.glob_pattern = glob_pattern

    def files(self, directory: pathlib.Path) -> iter:
        return directory.glob(self.glob_pattern)

    @property
    def restriction_descriptions(self) -> list:
        return ['name matches glob pattern ' + self.glob_pattern]


class FileTypeSelector(DirContentsSelector):
    def __init__(self, included_file_type: file_properties.FileType):
        self.included_file_type = included_file_type

    def files(self, directory: pathlib.Path) -> iter:
        predicate = file_properties.TYPE_INFO[self.included_file_type].pathlib_path_predicate
        return filter(predicate, directory.iterdir())

    @property
    def restriction_descriptions(self) -> list:
        return ['file is a ' + file_properties.TYPE_INFO[self.included_file_type].description]


class AndSelector(DirContentsSelector):
    def __init__(self, selectors: list):
        self.selectors = selectors

    def files(self, directory: pathlib.Path) -> iter:
        raise NotImplementedError('todo')

    @property
    def restriction_descriptions(self) -> list:
        return list(itertools.chain(map(lambda s: s.restriction_descriptions, self.selectors)))
