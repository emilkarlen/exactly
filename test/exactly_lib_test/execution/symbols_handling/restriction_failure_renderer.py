import unittest

from exactly_lib.execution.symbols_handling import restriction_failure_renderer as sut
from exactly_lib.symbol.concrete_restrictions import FailureOfDirectReference, FailureOfIndirectReference
from exactly_lib.symbol.value_restriction import ValueRestrictionFailure
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_names


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestRenderFailureOfDirectReference(),
        TestRenderFailureOfIndirectReference(),
    ])


class TestRenderFailureOfDirectReference(unittest.TestCase):
    def runTest(self):
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
    def runTest(self):
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
