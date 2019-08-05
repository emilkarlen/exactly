import unittest
from typing import Optional

from exactly_lib.symbol.data.restrictions.reference_restrictions import FailureOfIndirectReference, \
    FailureOfDirectReference
from exactly_lib.symbol.data.value_restriction import ErrorMessageWithFixTip
from exactly_lib.symbol.err_msg import restriction_failures as sut
from exactly_lib.symbol.restriction import InvalidTypeCategoryFailure, InvalidValueTypeFailure
from exactly_lib.type_system.value_type import TypeCategory, ValueType
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestErrorMessage)


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
        actual = sut.ErrorMessage(self.string_sym_def_1.name,
                                  self.symbol_table,
                                  InvalidTypeCategoryFailure(TypeCategory.LOGIC,
                                                             TypeCategory.DATA))
        # ASSERT #
        asrt_text_doc.assert_is_valid_text_renderer(self, actual)

    def test_invalid_type(self):
        # ACT #
        actual = sut.ErrorMessage(self.string_sym_def_1.name,
                                  self.symbol_table,
                                  InvalidValueTypeFailure(ValueType.PATH,
                                                          ValueType.STRING))
        # ASSERT #
        asrt_text_doc.assert_is_valid_text_renderer(self, actual)

    def test_direct_reference(self):
        # ACT #
        actual = sut.ErrorMessage(self.string_sym_def_1.name,
                                  self.symbol_table,
                                  FailureOfDirectReference(_new_em('the message',
                                                                    'the how to fix')))
        # ASSERT #
        asrt_text_doc.assert_is_valid_text_renderer(self, actual)

    def test_indirect_reference(self):
        # ACT #
        actual = sut.ErrorMessage(self.string_sym_def_1.name,
                                  self.symbol_table,
                                  FailureOfIndirectReference(self.string_sym_def_1.name,
                                                             [self.string_sym_def_2.name],
                                                             _new_em('the message',
                                                                      'the how to fix')))
        # ASSERT #
        asrt_text_doc.assert_is_valid_text_renderer(self, actual)


def _new_em(message: str,
            how_to_fix: Optional[str] = None) -> ErrorMessageWithFixTip:
    return ErrorMessageWithFixTip(
        asrt_text_doc.new_single_string_text_for_test(message),
        (
            None
            if how_to_fix is None
            else asrt_text_doc.new_single_string_text_for_test(how_to_fix)
        )
    )
