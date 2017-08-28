import unittest

from exactly_lib.named_element.symbol.value_resolvers import file_ref_resolvers as sut
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsNothing
from exactly_lib.type_system_values.value_type import SymbolValueType, ValueType, ElementType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import FileRefTestImpl
from exactly_lib_test.type_system_values.test_resources.file_ref_assertions import equals_file_ref


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestFileRefConstant)


class TestFileRefConstant(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        file_ref = FileRefTestImpl(RelOptionType.REL_TMP, PathPartAsNothing())
        resolver = sut.FileRefConstant(file_ref)
        # ACT #
        actual_element_type = resolver.element_type
        actual_data_value_type = resolver.data_value_type
        actual_value_type = resolver.value_type
        # ASSERT #
        self.assertIs(ElementType.SYMBOL,
                      actual_element_type)
        self.assertIs(SymbolValueType.PATH,
                      actual_data_value_type)
        self.assertIs(ValueType.PATH,
                      actual_value_type)

    def test_resolved_value(self):
        # ARRANGE #
        file_ref = FileRefTestImpl(RelOptionType.REL_TMP, PathPartAsNothing())
        resolver = sut.FileRefConstant(file_ref)
        # ACT #
        actual = resolver.resolve(empty_symbol_table())
        # ASSERT #
        assertion = equals_file_ref(file_ref)
        assertion.apply_without_message(self, actual)
