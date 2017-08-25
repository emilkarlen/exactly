"""Functionality for accessing a subset of the files in a directory."""
import fnmatch
import functools
import os
import pathlib
import types

from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util import functional


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
            "name matches glob pattern `{}'".format(pattern)
            for pattern in self.name_patterns
        ]

        file_type_selector_descriptions = [
            "types is {}".format(file_properties.TYPE_INFO[file_type].type_argument)
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


def and_all(selectors: iter) -> Selectors:
    return functools.reduce(and_also, selectors, all_files())


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
