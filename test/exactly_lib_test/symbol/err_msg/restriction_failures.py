import unittest

from exactly_lib.symbol.data.restrictions.reference_restrictions import FailureOfIndirectReference, \
    FailureOfDirectReference
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure
from exactly_lib.symbol.err_msg import restriction_failures as sut
from exactly_lib.symbol.restriction import InvalidTypeCategoryFailure, InvalidValueTypeFailure
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestErrorMessage),
    ])


class TestErrorMessage(unittest.TestCase):
    string_sym_def_1 = data_symbol_utils.string_symbol_definition('symbol1')
    string_sym_def_2 = data_symbol_utils.string_symbol_definition('symbol2')

    symbol_table = data_symbol_utils.symbol_table_from_symbol_definitions(
        [string_sym_def_1,
         string_sym_def_2
         ]
    )

    def test_invalid_type_category(self):
        # ACT #
        actual = sut.error_message(self.string_sym_def_1.name,
                                   self.symbol_table,
                                   InvalidTypeCategoryFailure(TypeCategory.LOGIC,
                                                              TypeCategory.DATA))
        # ASSERT #
        self.assertIsInstance(actual, str)

    def test_invalid_type(self):
        # ACT #
        actual = sut.error_message(self.string_sym_def_1.name,
                                   self.symbol_table,
                                   InvalidValueTypeFailure(ValueType.PATH,
                                                           ValueType.STRING))
        # ASSERT #
        self.assertIsInstance(actual, str)

    def test_direct_reference(self):
        # ACT #
        actual = sut.error_message(self.string_sym_def_1.name,
                                   self.symbol_table,
                                   FailureOfDirectReference(ValueRestrictionFailure('the message',
                                                                                    'the how to fix')))
        # ASSERT #
        self.assertIsInstance(actual, str)

    def test_indirect_reference(self):
        # ACT #
        actual = sut.error_message(self.string_sym_def_1.name,
                                   self.symbol_table,
                                   FailureOfIndirectReference(self.string_sym_def_1.name,
                                                              [self.string_sym_def_2.name],
                                                              ValueRestrictionFailure('the message',
                                                                                      'the how to fix')))
        # ASSERT #
        self.assertIsInstance(actual, str)
