import unittest
from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.symbol.err_msg import restriction_failures as sut
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext, \
    StringSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRenderFailureOfDirectReference),
        unittest.makeSuite(TestRenderFailureOfIndirectReference),
    ])


class TestRenderFailureOfDirectReference(unittest.TestCase):
    def test(self):
        cases = [
            FailureOfDirectReference(_new_em('error message')),
            FailureOfDirectReference(_new_em('error message',
                                             'how to fix')),
        ]
        for failure in cases:
            with self.subTest(msg=failure.error):
                actual = sut.ErrorMessage('checked_symbol', empty_symbol_table(), failure)
                asrt_text_doc.assert_is_valid_text_renderer(self, actual)


class TestRenderFailureOfIndirectReference(unittest.TestCase):
    def test_all_referenced_symbols_have_definition_source(self):
        for path_to_failing_symbol in [[], ['symbol_on_path_to_failing_symbol']]:
            for how_to_fix in ['', 'how_to_fix']:
                with self.subTest(path_to_failing_symbol=path_to_failing_symbol,
                                  how_to_fix=how_to_fix):
                    error = _new_em('error message',
                                    how_to_fix=how_to_fix)
                    failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                                         path_to_failing_symbol=path_to_failing_symbol,
                                                         error=error)
                    # ACT #
                    checked_symbol = StringConstantSymbolContext('checked_symbol')
                    symbol_table = SymbolContext.symbol_table_of_contexts(
                        [checked_symbol] +
                        [StringConstantSymbolContext(failing_symbol)
                         for failing_symbol in path_to_failing_symbol]
                    )
                    actual = sut.ErrorMessage(checked_symbol.name, symbol_table, failure)
                    # ASSERT #
                    asrt_text_doc.assert_is_valid_text_renderer(self, actual)

    def test_directly_referenced_symbol_is_builtin(self):
        referenced_symbol = StringConstantSymbolContext('referenced symbol',
                                                        'referenced symbol value',
                                                        definition_source=None)
        for how_to_fix in ['', 'how_to_fix']:
            with self.subTest(how_to_fix=how_to_fix):
                error = _new_em('error message',
                                how_to_fix=how_to_fix)
                failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                                     path_to_failing_symbol=[referenced_symbol.name],
                                                     error=error)
                # ACT #
                checked_symbol = StringConstantSymbolContext('checked symbol name',
                                                             'checked symbol value')
                symbol_table = SymbolContext.symbol_table_of_contexts([
                    checked_symbol,
                    referenced_symbol,
                ])
                actual = sut.ErrorMessage(checked_symbol.name, symbol_table, failure)
                # ASSERT #
                asrt_text_doc.assert_is_valid_text_renderer(self, actual)

    def test_symbol_is_builtin(self):
        for how_to_fix in ['', 'how_to_fix']:
            with self.subTest(how_to_fix=how_to_fix):
                error = _new_em('error message',
                                how_to_fix=how_to_fix)
                failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                                     path_to_failing_symbol=[],
                                                     error=error)
                # ACT #
                checked_symbol = StringSymbolContext.of_constant('checked_symbol',
                                                                 'checked symbol value',
                                                                 definition_source=None)
                symbol_table = checked_symbol.symbol_table
                actual = sut.ErrorMessage(checked_symbol.name, symbol_table, failure)
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
