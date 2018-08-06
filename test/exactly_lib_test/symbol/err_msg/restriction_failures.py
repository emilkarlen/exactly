import unittest

from exactly_lib.symbol.err_msg import restriction_failures as sut
from exactly_lib.symbol.restriction import InvalidTypeCategoryFailure, InvalidValueTypeFailure
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestErrorMessage),
    ])


class TestErrorMessage(unittest.TestCase):
    string_symbol_name = 'string_symbol_name'
    symbol_table = data_symbol_utils.symbol_table_from_symbol_definitions(
        [data_symbol_utils.string_symbol_definition(string_symbol_name)]
    )

    def test_invalid_type_category(self):
        # ACT #
        actual = sut.error_message(self.string_symbol_name,
                                   self.symbol_table,
                                   InvalidTypeCategoryFailure(TypeCategory.LOGIC,
                                                              TypeCategory.DATA))
        # ASSERT #
        self.assertIsInstance(actual, str)

    def test_invalid_type(self):
        # ACT #
        actual = sut.error_message(self.string_symbol_name,
                                   self.symbol_table,
                                   InvalidValueTypeFailure(ValueType.PATH,
                                                           ValueType.STRING))
        # ASSERT #
        self.assertIsInstance(actual, str)
