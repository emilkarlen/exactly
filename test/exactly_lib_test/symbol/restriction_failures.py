import unittest
from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.symbol.err_msg import restriction_failures as sut
from exactly_lib.symbol.value_type import TypeCategory, ValueType
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference
from exactly_lib.type_val_deps.sym_ref.restrictions import InvalidTypeCategoryFailure, InvalidValueTypeFailure
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestErrorMessage)


class TestErrorMessage(unittest.TestCase):
    string_sym_def_1 = StringConstantSymbolContext('symbol1')
    string_sym_def_2 = StringConstantSymbolContext('symbol2')

    symbol_table = SymbolContext.symbol_table_of_contexts([
        string_sym_def_1,
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
                                  InvalidValueTypeFailure([ValueType.PATH]))
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
