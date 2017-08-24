import unittest

from exactly_lib.execution.symbols_handling import restriction_failure_renderer as sut
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference
from exactly_lib.named_element.symbol.string_resolver import string_constant
from exactly_lib.named_element.symbol.value_restriction import ValueRestrictionFailure
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.symbol.test_resources.symbol_utils import symbol_table_from_names
from exactly_lib_test.named_element.test_resources import named_elem_utils
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRenderFailureOfDirectReference),
        unittest.makeSuite(TestRenderFailureOfIndirectReference),
    ])


class TestRenderFailureOfDirectReference(unittest.TestCase):
    def test(self):
        cases = [
            FailureOfDirectReference(ValueRestrictionFailure('error message')),
            FailureOfDirectReference(ValueRestrictionFailure('error message',
                                                             'how to fix')),
        ]
        for failure in cases:
            with self.subTest(msg=failure.error):
                actual = sut.error_message('checked_symbol', empty_symbol_table(), failure)
                self.assertIsInstance(actual, str)


class TestRenderFailureOfIndirectReference(unittest.TestCase):
    def test_all_referenced_symbols_have_definition_source(self):
        for path_to_failing_symbol in [[], ['symbol_on_path_to_failing_symbol']]:
            for how_to_fix in ['', 'how_to_fix']:
                with self.subTest(path_to_failing_symbol=path_to_failing_symbol,
                                  how_to_fix=how_to_fix):
                    error = ValueRestrictionFailure('error message',
                                                    how_to_fix=how_to_fix)
                    failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                                         path_to_failing_symbol=path_to_failing_symbol,
                                                         error=error)
                    # ACT #
                    checked_symbol = 'checked_symbol'
                    symbol_table = symbol_table_from_names([checked_symbol] + path_to_failing_symbol)
                    actual = sut.error_message(checked_symbol, symbol_table, failure)
                    # ASSERT #
                    self.assertIsInstance(actual, str)

    def test_directly_referenced_symbol_is_builtin(self):
        referenced_symbol = NameAndValue('referenced symbol',
                                         named_elem_utils.container_of_builtin(
                                             string_constant('referenced symbol value')))
        for how_to_fix in ['', 'how_to_fix']:
            with self.subTest(how_to_fix=how_to_fix):
                error = ValueRestrictionFailure('error message',
                                                how_to_fix=how_to_fix)
                failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                                     path_to_failing_symbol=[referenced_symbol.name],
                                                     error=error)
                # ACT #
                checked_symbol = NameAndValue('checked symbol name',
                                              symbol_utils.string_constant_container('checked symbol value'))
                symbol_table = SymbolTable({
                    checked_symbol.name: checked_symbol.value,
                    referenced_symbol.name: referenced_symbol.value,
                })
                actual = sut.error_message(checked_symbol.name, symbol_table, failure)
                # ASSERT #
                self.assertIsInstance(actual, str)

    def test_symbol_is_builtin(self):
        for how_to_fix in ['', 'how_to_fix']:
            with self.subTest(how_to_fix=how_to_fix):
                error = ValueRestrictionFailure('error message',
                                                how_to_fix=how_to_fix)
                failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                                     path_to_failing_symbol=[],
                                                     error=error)
                # ACT #
                checked_symbol = NameAndValue('checked_symbol',
                                              named_elem_utils.container_of_builtin(
                                                  string_constant('checked symbol value')))
                symbol_table = SymbolTable({
                    checked_symbol.name: checked_symbol.value
                })
                actual = sut.error_message(checked_symbol.name, symbol_table, failure)
                # ASSERT #
                self.assertIsInstance(actual, str)
