import pathlib
import unittest

from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_checks import FileChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class PathAssertionBase(va.ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        va.IsInstance(pathlib.Path).apply(put, value, message_builder)
        self._apply(put, value, message_builder)

    def _apply(self,
               put: unittest.TestCase,
               value: pathlib.Path,
               message_builder: va.MessageBuilder):
        raise NotImplementedError()

    @staticmethod
    def _checker_for_path(put: unittest.TestCase,
                          dir_path: pathlib.Path,
                          message_builder: va.MessageBuilder) -> FileChecker:
        header = va.sub_component_header('Contents of {}'.format(dir_path), message_builder)
        return FileChecker(put, header)


class PathIsFileWithContents(PathAssertionBase):
    def __init__(self, expected_contents: str):
        self.expected_contents = expected_contents

    def _apply(self,
               put: unittest.TestCase,
               value: pathlib.Path,
               message_builder: va.MessageBuilder):
        file_checker = FileChecker(put)
        file_checker.assert_exists_plain_file(value)
        file_checker.assert_file_contents(value, self.expected_contents)


class DirContainsExactly__Va(PathAssertionBase):
    def __init__(self,
                 expected_contents: file_structure.DirContents):
        self.expected_contents = expected_contents

    def _apply(self,
               put: unittest.TestCase,
               dir_path: pathlib.Path,
               message_builder: va.MessageBuilder):
        checker = self._checker_for_path(put, dir_path, message_builder)
        checker.assert_dir_contents_matches_exactly(dir_path,
                                                    self.expected_contents)


class DirContainsAtLeast__Va(PathAssertionBase):
    def __init__(self,
                 expected_contents: file_structure.DirContents):
        self.expected_contents = expected_contents

    def _apply(self,
               put: unittest.TestCase,
               dir_path: pathlib.Path,
               message_builder: va.MessageBuilder):
        checker = self._checker_for_path(put, dir_path, message_builder)
        checker.assert_dir_contains_at_least(dir_path,
                                             self.expected_contents.file_system_element_contents)
