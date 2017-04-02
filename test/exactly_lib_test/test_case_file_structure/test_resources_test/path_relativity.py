import unittest

from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType, \
    SPECIFIC_ABSOLUTE_RELATIVITY, specific_relative_relativity
from exactly_lib_test.test_case_file_structure.test_resources import path_relativity as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsPathRelativity),
        unittest.makeSuite(TestNotEqualsPathRelativity),
        TestEqualsPathRelativityVariants(),
        unittest.makeSuite(TestNotEqualsPathRelativityVariants),
    ])


class TestEqualsPathRelativity(unittest.TestCase):
    def test_absolute(self):
        # ARRANGE #
        expected = SPECIFIC_ABSOLUTE_RELATIVITY
        actual = SPECIFIC_ABSOLUTE_RELATIVITY
        assertion = sut.equals_path_relativity(expected)
        # ACT & ASSERT #
        assertion.apply_with_message(self, actual, 'Equals')

    def test_relative(self):
        for rel_option in RelOptionType:
            # ARRANGE #
            relativity = specific_relative_relativity(RelOptionType.REL_HOME)
            with self.subTest(msg='RelOptionType=' + str(rel_option)):
                assertion = sut.equals_path_relativity(relativity)
                # ACT & ASSERT #
                assertion.apply_with_message(self, relativity, 'Equals')


class TestNotEqualsPathRelativity(unittest.TestCase):
    def test_differs__because_on_is_absolute(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = SPECIFIC_ABSOLUTE_RELATIVITY
        actual = specific_relative_relativity(RelOptionType.REL_ACT)
        assertion = sut.equals_path_relativity(expected)
        # ASSERT #
        with put.assertRaises(TestException):
            # ACT #
            assertion.apply_with_message(put, actual, 'NotEquals')

    def test_differs__both_are_relative_but_with_different_relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = specific_relative_relativity(RelOptionType.REL_ACT)
        actual = specific_relative_relativity(RelOptionType.REL_HOME)
        assertion = sut.equals_path_relativity(expected)
        # ASSERT #
        with put.assertRaises(TestException):
            # ACT #
            assertion.apply_with_message(put, actual, 'NotEquals')


class TestEqualsPathRelativityVariants(unittest.TestCase):
    def runTest(self):
        test_cases = [
            PathRelativityVariants({rel_option_type}, accept_absolute)
            for accept_absolute in [False, True]
            for rel_option_type in RelOptionType
            ]

        for value in test_cases:
            with self.subTest(msg='RelOptionTypes={}, absolute={}'.format(value.rel_option_types, value.absolute)):
                sut.path_relativity_variants_equals(value).apply_with_message(self, value, 'Equals')


class TestNotEqualsPathRelativityVariants(unittest.TestCase):
    def test_differs__absolute(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        actual = PathRelativityVariants({RelOptionType.REL_ACT}, True)
        with put.assertRaises(TestException):
            sut.path_relativity_variants_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__rel_option_types__expected_has_super_set(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME}, False)
        actual = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        with put.assertRaises(TestException):
            sut.path_relativity_variants_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__rel_option_types__single_different_value(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        actual = PathRelativityVariants({RelOptionType.REL_HOME}, False)
        with put.assertRaises(TestException):
            sut.path_relativity_variants_equals(expected).apply_with_message(put, actual, 'NotEquals')
