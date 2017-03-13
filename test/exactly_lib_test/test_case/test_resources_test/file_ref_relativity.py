import unittest

from exactly_lib.test_case.file_ref_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.test_case.test_resources import file_ref_relativity as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEquals(),
        unittest.makeSuite(TestNotEquals),
    ])


class TestEquals(unittest.TestCase):
    def runTest(self):
        test_cases = [
            PathRelativityVariants({rel_option_type}, accept_absolute)
            for accept_absolute in [False, True]
            for rel_option_type in RelOptionType
            ]

        for value in test_cases:
            with self.subTest(msg='RelOptionTypes={}, absolute={}'.format(value.rel_option_types, value.absolute)):
                sut.file_ref_relativity_equals(value).apply_with_message(self, value, 'Equals')


class TestNotEquals(unittest.TestCase):
    def test_differs__absolute(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        actual = PathRelativityVariants({RelOptionType.REL_ACT}, True)
        with put.assertRaises(TestException):
            sut.file_ref_relativity_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__rel_option_types__expected_has_super_set(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME}, False)
        actual = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        with put.assertRaises(TestException):
            sut.file_ref_relativity_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__rel_option_types__single_different_value(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        actual = PathRelativityVariants({RelOptionType.REL_HOME}, False)
        with put.assertRaises(TestException):
            sut.file_ref_relativity_equals(expected).apply_with_message(put, actual, 'NotEquals')
