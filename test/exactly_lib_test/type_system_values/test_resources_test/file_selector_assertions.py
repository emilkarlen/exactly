import unittest

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.type_system_values.test_resources import file_selector_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsFileSelector),
    ])


class TestEqualsFileSelector(unittest.TestCase):
    def test_equals_empty(self):
        # ARRANGE #
        expected = FileSelector(Selectors())
        actual = FileSelector(Selectors())
        assertion = sut.equals_file_selector(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_equals_empty(self):
        # ARRANGE #
        cases = [
            NameAndValue('name pattern mismatch',
                         FileSelector(Selectors(name_patterns=frozenset(['pattern'])))
                         ),
            NameAndValue('file type mismatch',
                         FileSelector(Selectors(file_types=frozenset([FileType.REGULAR])))
                         ),
        ]
        assertion_to_check = sut.equals_file_selector(FileSelector(Selectors()))
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_equals_name_patterns(self):
        # ARRANGE #
        expected = FileSelector(Selectors(name_patterns=frozenset(['pattern 1',
                                                                   'pattern 2'])))
        actual = FileSelector(Selectors(name_patterns=frozenset(['pattern 1',
                                                                 'pattern 2'])))
        assertion = sut.equals_file_selector(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_equals_name_patterns(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_selector(FileSelector(Selectors(
            name_patterns=frozenset(['expected pattern'])
        )))
        cases = [
            NameAndValue('name pattern mismatch',
                         FileSelector(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('one additional pattern',
                         FileSelector(Selectors(name_patterns=frozenset(['expected pattern',
                                                                         'actual pattern'])))
                         ),
            NameAndValue('file type mismatch',
                         FileSelector(Selectors(file_types=frozenset([FileType.REGULAR])))
                         ),
            NameAndValue('empty selection',
                         FileSelector(Selectors())
                         ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_equals_file_types(self):
        # ARRANGE #
        expected = FileSelector(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                FileType.SYMLINK])))
        actual = FileSelector(Selectors(file_types=frozenset([FileType.REGULAR,
                                                              FileType.SYMLINK])))
        assertion = sut.equals_file_selector(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_equals_file_types(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_selector(FileSelector(Selectors(
            file_types=frozenset([FileType.SYMLINK,
                                  FileType.DIRECTORY])
        )))
        cases = [
            NameAndValue('name pattern mismatch',
                         FileSelector(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('one additional pattern',
                         FileSelector(Selectors(name_patterns=frozenset(['expected pattern',
                                                                         'actual pattern'])))
                         ),
            NameAndValue('missing file type',
                         FileSelector(Selectors(file_types=frozenset([FileType.DIRECTORY])))
                         ),
            NameAndValue('different file types',
                         FileSelector(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                      FileType.DIRECTORY])))
                         ),
            NameAndValue('name pattern mismatch',
                         FileSelector(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('empty selection',
                         FileSelector(Selectors())
                         ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_equals_name_patterns_and_file_types(self):
        # ARRANGE #
        expected = FileSelector(Selectors(name_patterns=frozenset(['p']),
                                          file_types=frozenset([FileType.REGULAR])))
        actual = FileSelector(Selectors(name_patterns=frozenset(['p']),
                                        file_types=frozenset([FileType.REGULAR])))
        assertion = sut.equals_file_selector(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
