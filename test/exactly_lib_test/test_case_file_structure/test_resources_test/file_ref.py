import unittest

from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsNothing
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_case_file_structure.test_resources import file_ref as sut
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import \
    FileRefTestImpl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEqualsCommonToBothAssertionMethods(),
        TestEqualsSpecificForAssertionMethod2WithIgnoredValueReferences(),
        unittest.makeSuite(TestNotEquals_PathSuffixAsFixedPath),
        unittest.makeSuite(TestNotEquals_DifferentTypeOfPathSuffix),
        unittest.makeSuite(Test2NotEquals),
    ])


class TestEqualsCommonToBothAssertionMethods(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsFixedPath('file-name')),
             empty_symbol_table(),
             ),
            ('NOT Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsFixedPath('a-file-name')),
             empty_symbol_table(),
             ),
        ]
        for test_case_name, value, symbol_table_for_method2 in test_cases:
            assert isinstance(value, FileRef), 'Type info for IDE'
            with self.subTest(msg='file_ref_equals::' + test_case_name):
                assertion = sut.file_ref_equals(value)
                assertion.apply_with_message(self, value, test_case_name)
            with self.subTest(msg='equals_file_ref2::' + test_case_name):
                assertion = sut.equals_file_ref2(value)
                assertion.apply_with_message(self, value, test_case_name)


class TestEqualsSpecificForAssertionMethod2WithIgnoredValueReferences(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Nothing path suffixes',
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsNothing()),
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsNothing()),
             ),
        ]
        for test_case_name, first, second in test_cases:
            assert isinstance(first, FileRef), 'Type info for IDE (first)'
            assert isinstance(second, FileRef), 'Type info for IDE (second)'
            with self.subTest(msg='1::' + test_case_name):
                assertion = sut.equals_file_ref2(first)
                assertion.apply_with_message(self, second, test_case_name)
            with self.subTest(msg='2::' + test_case_name):
                assertion = sut.equals_file_ref2(second)
                assertion.apply_with_message(self, first, test_case_name)


class TestNotEquals_PathSuffixAsFixedPath(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')


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
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')


class Test2NotEquals(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref2(expected)
            assertion.apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref2(expected)
            assertion.apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref2(expected)
            assertion.apply_with_message(put, actual, 'NotEquals')


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HOME
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool) -> FileRefRelativityRestriction:
    return FileRefRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))
