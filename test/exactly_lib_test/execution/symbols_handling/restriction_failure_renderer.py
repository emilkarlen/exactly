import unittest

from exactly_lib.execution.symbols_handling import restriction_failure_renderer as sut
from exactly_lib.symbol.concrete_restrictions import FailureOfDirectReference, FailureOfIndirectReference
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_names


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRenderFailureOfDirectReference),
        unittest.makeSuite(TestRenderFailureOfIndirectReference),
    ])


class TestRenderFailureOfDirectReference(unittest.TestCase):
    def test(self):
        # ARRANGE #
        failure = FailureOfDirectReference('error message')
        # ACT #
        actual = sut.error_message('checked_symbol', empty_symbol_table(), failure)
        # ASSERT #
        self.assertIsInstance(actual, str)


class TestRenderFailureOfIndirectReference(unittest.TestCase):
    def test_empty_path_to_failing_symbol(self):
        # ARRANGE #
        path_to_failing_symbol = []
        failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                             path_to_failing_symbol=path_to_failing_symbol,
                                             error_message='error message')
        # ACT #
        checked_symbol = 'checked_symbol'
        symbol_table = symbol_table_from_names([checked_symbol] + path_to_failing_symbol)
        actual = sut.error_message('checked_symbol', symbol_table, failure)
        # ASSERT #
        self.assertIsInstance(actual, str)

    def test_meaning_of_failure_is_non_empty(self):
        # ARRANGE #
        path_to_failing_symbol = []
        failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                             path_to_failing_symbol=path_to_failing_symbol,
                                             error_message='error message',
                                             meaning_of_failure='meaning of failure')
        # ACT #
        checked_symbol = 'checked_symbol'
        symbol_table = symbol_table_from_names([checked_symbol] + path_to_failing_symbol)
        actual = sut.error_message('checked_symbol', symbol_table, failure)
        # ASSERT #
        self.assertIsInstance(actual, str)

    def test_non_empty_path_to_failing_symbol(self):
        # ARRANGE #
        path_to_failing_symbol = ['symbol_on_path_to_failing_symbol']
        failure = FailureOfIndirectReference(failing_symbol='name_of_failing_symbol',
                                             path_to_failing_symbol=path_to_failing_symbol,
                                             error_message='error message')
        # ACT #
        checked_symbol = 'checked_symbol'
        symbol_table = symbol_table_from_names([checked_symbol] + path_to_failing_symbol)
        actual = sut.error_message(checked_symbol, symbol_table, failure)
        # ASSERT #
        self.assertIsInstance(actual, str)
