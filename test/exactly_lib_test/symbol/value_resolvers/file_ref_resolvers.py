import unittest

from exactly_lib.symbol.concrete_values import ValueType
from exactly_lib.symbol.value_resolvers import file_ref_resolvers as sut
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsNothing
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.file_ref import equals_file_ref
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import FileRefTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileRefConstant)


class TestFileRefConstant(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        file_ref = FileRefTestImpl(RelOptionType.REL_TMP, PathPartAsNothing())
        resolver = sut.FileRefConstant(file_ref)
        # ACT #
        actual = resolver.value_type
        # ASSERT #
        self.assertIs(ValueType.PATH,
                      actual)

    def test_resolved_value(self):
        # ARRANGE #
        file_ref = FileRefTestImpl(RelOptionType.REL_TMP, PathPartAsNothing())
        resolver = sut.FileRefConstant(file_ref)
        # ACT #
        actual = resolver.resolve(empty_symbol_table())
        # ASSERT #
        assertion = equals_file_ref(file_ref)
        assertion.apply_without_message(self, actual)
