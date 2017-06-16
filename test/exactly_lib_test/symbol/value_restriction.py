import unittest
from collections import Counter

from exactly_lib.symbol import value_restriction as sut
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestUsageOfDirectRestriction)
    ])


class TestUsageOfDirectRestriction(unittest.TestCase):
    def test_satisfied_restriction(self):
        expected_result = None
        restriction_on_direct = RestrictionWithConstantResult(expected_result)
        self._check_direct_with_satisfied_variants_for_restriction_on_every_node(restriction_on_direct,
                                                                                 expected_result)

    def test_unsatisfied_restriction(self):
        expected_result = 'error message'
        restriction_on_direct = RestrictionWithConstantResult(expected_result)
        self._check_direct_with_satisfied_variants_for_restriction_on_every_node(restriction_on_direct,
                                                                                 expected_result)


    def test_test(self):
        def f():
            self.fail('f fail')

        for i in range(1,4):
            with self.subTest(i=i):
                f()


    def test_test2(self):
        f = faila(self)

        for i in range(1,4):
            with self.subTest(i=i):
                f()


    def test_that_only_direct_symbol_is_processed(self):
        entry_with_no_refs = symbol_table_entry('entry_with_no_refs', [])
        self.fail('not impl')

    def _check_direct_with_satisfied_variants_for_restriction_on_every_node(
            self,
            restriction_on_direct_node: sut.ValueRestriction,
            expected_result):
        symbol_to_check = symbol_utils.entry('symbol_name')
        cases = [
            (
                'restriction on every is None',
                None,
                symbol_utils.symbol_table_from_entries([symbol_to_check]),
            ),
            (
                'restriction on every is unconditionally satisfied',
                None,
                symbol_utils.symbol_table_from_entries([symbol_to_check]),
            ),
        ]
        for case_name, restriction_on_every, symbol_table in cases:
            with self.subTest(msg=case_name):
                restrictions = sut.ReferenceRestrictions(direct=restriction_on_direct_node,
                                                         every=restriction_on_every)
                assert isinstance(symbol_to_check.value, sut.ValueContainer)
                actual_result = restrictions.is_satisfied_by(symbol_table,
                                                             symbol_to_check.key,
                                                             symbol_to_check.value)
                self.assertEqual(expected_result, actual_result)


class RestrictionWithConstantResult(sut.ValueRestriction):
    def __init__(self, result):
        self.result = result

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.ValueContainer) -> str:
        return self.result



class RestrictionThatRegistersProcessedSymbols(sut.ValueRestriction):
    def __init__(self, result):
        self.result = result
        self.visited = Counter()

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.ValueContainer) -> str:
        self.visited.update([symbol_name])
        return self.result

def faila(tc: unittest.TestCase):
    def r():
        tc.fail("r")

    return r


def symbol_table_entry(symbol_name: str, referred_symbols):
    raise NotImplementedError()