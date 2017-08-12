import pathlib
import unittest

from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.assertions.file_checks import FileChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def path_is_file_with_contents(expected_contents: str) -> asrt.ValueAssertion:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return _PathIsFileWithContents(expected_contents)


def dir_contains_exactly(expected_contents: file_structure.DirContents) -> asrt.ValueAssertion:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return DirContainsExactly(expected_contents)


def dir_is_empty() -> asrt.ValueAssertion:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return DirContainsExactly(file_structure.empty_dir_contents())


def dir_contains_at_least(expected_contents: file_structure.DirContents) -> asrt.ValueAssertion:
    """
    Assumes that the actual value is a pathlib.Path
    """
    return _DirContainsAtLeast(expected_contents)


class PathAssertionBase(asrt.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        asrt.IsInstance(pathlib.Path).apply(put, value, message_builder)
        self._apply(put, value, message_builder)

    def _apply(self,
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

    def _apply(self,
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

    def _apply(self,
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

    def _apply(self,
               put: unittest.TestCase,
               dir_path: pathlib.Path,
               message_builder: asrt.MessageBuilder):
        checker = self._checker_for_path(put, dir_path, message_builder)
        checker.assert_dir_contains_at_least(dir_path,
                                             self.expected_contents.file_system_elements)
