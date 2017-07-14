import unittest

from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType, \
    SPECIFIC_ABSOLUTE_RELATIVITY, specific_relative_relativity
from exactly_lib_test.test_case_file_structure.test_resources import path_relativity as sut
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


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
        expected = SPECIFIC_ABSOLUTE_RELATIVITY
        actual = specific_relative_relativity(RelOptionType.REL_ACT)
        assertion = sut.equals_path_relativity(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__both_are_relative_but_with_different_relativity(self):
        # ARRANGE #
        expected = specific_relative_relativity(RelOptionType.REL_ACT)
        actual = specific_relative_relativity(RelOptionType.REL_HOME)
        assertion = sut.equals_path_relativity(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


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
        expected = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        actual = PathRelativityVariants({RelOptionType.REL_ACT}, True)
        assertion = sut.path_relativity_variants_equals(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__rel_option_types__expected_has_super_set(self):
        expected = PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME}, False)
        actual = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        assertion = sut.path_relativity_variants_equals(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__rel_option_types__single_different_value(self):
        expected = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        actual = PathRelativityVariants({RelOptionType.REL_HOME}, False)
        assertion = sut.path_relativity_variants_equals(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)
