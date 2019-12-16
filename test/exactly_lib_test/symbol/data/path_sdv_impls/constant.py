import unittest

from exactly_lib.symbol.data.path_sdv_impls import constant as sut
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.value_type import DataValueType, ValueType, TypeCategory
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.simple_path import PathDdvTestImpl
from exactly_lib_test.type_system.data.test_resources.path_assertions import equals_path


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPathConstant)


class TestPathConstant(unittest.TestCase):
    def test_value_type(self):
        # ARRANGE #
        path = PathDdvTestImpl(RelOptionType.REL_TMP, paths.empty_path_part())
        sdv = sut.PathConstantSdv(path)
        # ACT #
        actual_element_type = sdv.type_category
        actual_data_value_type = sdv.data_value_type
        actual_value_type = sdv.value_type
        # ASSERT #
        self.assertIs(TypeCategory.DATA,
                      actual_element_type)
        self.assertIs(DataValueType.PATH,
                      actual_data_value_type)
        self.assertIs(ValueType.PATH,
                      actual_value_type)

    def test_resolved_value(self):
        # ARRANGE #
        path = PathDdvTestImpl(RelOptionType.REL_TMP, paths.empty_path_part())
        sdv = sut.PathConstantSdv(path)
        # ACT #
        actual = sdv.resolve(empty_symbol_table())
        # ASSERT #
        assertion = equals_path(path)
        assertion.apply_without_message(self, actual)