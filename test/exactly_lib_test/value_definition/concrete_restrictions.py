import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib.value_definition import concrete_restrictions as sut
from exactly_lib.value_definition.concrete_values import StringValue
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.value_definition.test_resources.value_definition_utils import file_ref_value


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestNoRestriction)


class TestNoRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            StringValue('string'),
            file_ref_value(),
        ]
        restriction = sut.NoRestriction()
        value_definitions = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(value_definitions, value)
                # ASSERT #
                self.assertIsNone(actual)


class TestFileRefRelativityRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = sut.FileRefRelativityRestriction(PathRelativityVariants(
            {RelOptionType.REL_ACT, RelOptionType.REL_HOME, RelOptionType.REL_RESULT},
            False))
        value_definitions = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(value_definitions, value)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__relative_paths(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = sut.FileRefRelativityRestriction(PathRelativityVariants(
            {RelOptionType.REL_RESULT},
            False))
        value_definitions = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                # ACT #
                actual = restriction.is_satisfied_by(value_definitions, value)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')
