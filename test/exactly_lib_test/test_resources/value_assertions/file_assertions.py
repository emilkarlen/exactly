import pathlib
import unittest

from exactly_lib_test.test_resources.files import file_structure
from exactly_lib_test.test_resources.files.file_checks import FileChecker
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase


def name_matches(name: Assertion[str]) -> Assertion[pathlib.Path]:
    return asrt.sub_component(
        'name',
        _get_name,
        name,
    )


def name_equals(name: str) -> Assertion[pathlib.Path]:
    return asrt.sub_component(
        'name',
        _get_name,
        asrt.equals(name),
    )


def str_as_path(path: Assertion[pathlib.Path]) -> Assertion[str]:
    return asrt.on_transformed(
        pathlib.Path,
        path,
    )


def path_as_str(path: Assertion[str]) -> Assertion[pathlib.Path]:
    return asrt.on_transformed(
        str,
        path,
    )


def path_is_file_with_contents(expected_contents: str) -> Assertion[pathlib.Path]:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return _PathIsFileWithContents(expected_contents)


def dir_contains_exactly(expected_contents: file_structure.DirContents) -> Assertion[pathlib.Path]:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return DirContainsExactly(expected_contents)


def dir_contains_exactly_2(expected_contents: FileSystemElements) -> Assertion[pathlib.Path]:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return DirContainsExactly(file_structure.DirContents(list(expected_contents)))


def dir_is_empty() -> Assertion[pathlib.Path]:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return DirContainsExactly(file_structure.empty_dir_contents())


def dir_contains_at_least(expected_contents: file_structure.DirContents) -> Assertion[pathlib.Path]:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return _DirContainsAtLeast(expected_contents)


class PathAssertionBase(AssertionBase[pathlib.Path]):
    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        asrt.IsInstance(pathlib.Path).apply(put, value, message_builder)
        self._check_path(put, value, message_builder)

    def _check_path(self,
                    put: unittest.TestCase,
                    value: pathlib.Path,
                    message_builder: asrt.MessageBuilder):
        raise NotImplementedError()

    @staticmethod
    def _checker_for_path(put: unittest.TestCase,
                          dir_path: pathlib.Path,
                          message_builder: asrt.MessageBuilder) -> FileChecker:
        header = asrt.sub_component_header('Contents of {}'.format(dir_path), message_builder)
        return FileChecker(put, header)


class _PathIsFileWithContents(PathAssertionBase):
    def __init__(self, expected_contents: str):
        self.expected_contents = expected_contents

    def _check_path(self,
                    put: unittest.TestCase,
                    value: pathlib.Path,
                    message_builder: asrt.MessageBuilder):
        file_checker = FileChecker(put)
        file_checker.assert_exists_plain_file(value)
        file_checker.assert_file_contents(value, self.expected_contents)


class DirContainsExactly(PathAssertionBase):
    def __init__(self,
                 expected_contents: file_structure.DirContents):
        self.expected_contents = expected_contents

    def _check_path(self,
                    put: unittest.TestCase,
                    dir_path: pathlib.Path,
                    message_builder: asrt.MessageBuilder):
        checker = self._checker_for_path(put, dir_path, message_builder)
        checker.assert_dir_contents_matches_exactly(dir_path,
                                                    self.expected_contents)


class _DirContainsAtLeast(PathAssertionBase):
    def __init__(self,
                 expected_contents: file_structure.DirContents):
        self.expected_contents = expected_contents

    def _check_path(self,
                    put: unittest.TestCase,
                    dir_path: pathlib.Path,
                    message_builder: asrt.MessageBuilder):
        checker = self._checker_for_path(put, dir_path, message_builder)
        checker.assert_dir_contains_at_least(dir_path,
                                             self.expected_contents.file_system_elements)


def _get_name(path: pathlib.PurePath) -> str:
    return path.name
