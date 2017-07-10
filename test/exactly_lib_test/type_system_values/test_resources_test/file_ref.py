import unittest

from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsNothing
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import \
    FileRefTestImpl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.type_system_values.test_resources import file_ref as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEquals(),
        unittest.makeSuite(TestNotEquals_PathSuffixAsFixedPath),
        unittest.makeSuite(TestNotEquals_DifferentTypeOfPathSuffix),
    ])


class TestEquals(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsFixedPath('file-name')),
             ),
            ('NOT Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsFixedPath('a-file-name')),
             ),
        ]
        for test_case_name, value in test_cases:
            assert isinstance(value, FileRef), 'Type info for IDE'
            with self.subTest(test_case_name):
                assertion = sut.equals_file_ref(value)
                assertion.apply_without_message(self, value)


class TestNotEquals_PathSuffixAsFixedPath(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref(expected).apply_with_message(put, actual, 'NotEquals')


class TestNotEquals_DifferentTypeOfPathSuffix(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT,
                                   PathPartAsFixedPath('name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT,
                                 PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_file_ref(expected).apply_with_message(put, actual, 'NotEquals')


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HOME
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool) -> FileRefRelativityRestriction:
    return FileRefRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))
