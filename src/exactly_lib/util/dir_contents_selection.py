"""Functionality for accessing a subset of the files in a directory."""
import fnmatch
import itertools
import os
import pathlib
import types

from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util import functional


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


class Selectors(tuple):
    """
    Represents a set of restrictions, as a deep embedding,
    so that it is possible to optimize the selection computation
    (mostly for minimizing number of IO requests)
    """

    def __new__(cls,
                name_patterns: frozenset = frozenset(),
                file_types: frozenset = frozenset()):
        return tuple.__new__(cls, (name_patterns, file_types))

    @property
    def name_patterns(self) -> frozenset:
        return self[0]

    @property
    def file_types(self) -> frozenset:
        return self[1]

    @property
    def selection_descriptions(self) -> list:
        """
        A list of strings that each describe a restriction
        that must be met by a file to be included in the set.
        """
        name_selector_descriptions = [
            "name matches `{}'".format(pattern)
            for pattern in self.name_patterns
        ]

        file_type_selector_descriptions = [
            "file types is {}".format(file_properties.TYPE_INFO[file_type])
            for file_type in self.file_types
        ]

        return name_selector_descriptions + file_type_selector_descriptions


def all_files() -> Selectors:
    return Selectors()


def name_matches_pattern(pattern: str) -> Selectors:
    return Selectors(name_patterns=frozenset([pattern]))


def file_type_is(file_type: file_properties.FileType) -> Selectors:
    return Selectors(file_types=frozenset([file_type]))


def and_also(x: Selectors, y: Selectors) -> Selectors:
    return Selectors(
        name_patterns=x.name_patterns.union(y.name_patterns),
        file_types=x.file_types.union(y.file_types)
    )


def get_selection(directory: pathlib.Path,
                  selectors: Selectors) -> iter:
    return _FilesGetter(selectors, directory).get()


class _FilesGetter:
    def __init__(self,
                 selectors: Selectors,
                 directory: pathlib.Path):
        self.directory = directory
        self.selectors = selectors

    def get(self) -> iter:

        if self._file_types_are_disjoint():
            return iter([])

        all_files_iter = self._all_files()

        if not self.selectors.file_types and not self.selectors.name_patterns:
            return all_files_iter

        if not self.selectors.file_types:
            return self._names_iterator(all_files_iter)

        if not self.selectors.name_patterns:
            return self._non_disjoint_type_selections_iterator(all_files_iter)

        return self._non_disjoint_type_selections_iterator(
            self._names_iterator(
                all_files_iter)
        )

    def _all_files(self) -> iter:
        return os.listdir(str(self.directory))

    def _names_iterator(self, names: iter) -> iter:
        ret_val = names
        for name_pattern in self.selectors.name_patterns:
            ret_val = self._name_iterator(name_pattern, ret_val)
        return ret_val

    def _name_iterator(self, name_pattern: str, names: iter) -> iter:
        return iter(fnmatch.filter(names, name_pattern))

    def _non_disjoint_type_selections_iterator(self, file_names: iter) -> iter:
        file_types = list(self.selectors.file_types)
        if len(file_types) == 1:
            file_type = file_types[0]
            if file_type is FileType.SYMLINK:
                return self._is_sym_link_iterator(file_names)
            else:
                return self._is_other_than_sym_link_iterator(file_type, file_names)

        file_types.remove(FileType.SYMLINK)
        file_type_other_than_sym_link = file_types[0]

        return self._is_sym_link_iterator(
            self._is_other_than_sym_link_iterator(file_type_other_than_sym_link, file_names))

    def _is_sym_link_iterator(self, file_names: iter) -> iter:

        predicate = file_properties.TYPE_INFO[FileType.SYMLINK].stat_mode_predicate
        for file_name in file_names:
            try:
                stat_results = os.stat(str(self.directory / file_name),
                                       follow_symlinks=False)
                if predicate(stat_results.st_mode):
                    yield file_name
            except FileNotFoundError:
                pass

    def _is_other_than_sym_link_iterator(self,
                                         file_type: FileType,
                                         file_names: iter) -> iter:

        predicate = file_properties.TYPE_INFO[file_type].stat_mode_predicate
        for file_name in file_names:
            try:
                stat_results = os.stat(str(self.directory / file_name),
                                       follow_symlinks=True)
                if predicate(stat_results.st_mode):
                    yield file_name
            except FileNotFoundError:
                pass

    def _both_kind_of_restrictions(self) -> iter:
        raise NotImplementedError('todo')

    def _file_types_are_disjoint(self) -> bool:
        file_types = self.selectors.file_types
        return FileType.REGULAR in file_types and FileType.DIRECTORY in file_types

    def _file_type_predicate(self) -> types.FunctionType:
        predicates = [file_properties.TYPE_INFO[file_type].stat_mode_predicate
                      for file_type in self.selectors.file_types]

        return functional.and_predicate(predicates)


class EveryFileInDir(DirContentsSelector):
    def files(self, directory: pathlib.Path) -> iter:
        return directory.iterdir()

    @property
    def restriction_descriptions(self) -> list:
        return []


class NameFilter:
    def __init__(self, pattern: str):
        self.pattern = pattern

    def __call__(self, names):
        return fnmatch.filter(names, self.pattern)


class TypeFilter:
    def __init__(self, pattern: str):
        self.pattern = pattern

    def __call__(self, names):
        return fnmatch.filter(names, self.pattern)


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
