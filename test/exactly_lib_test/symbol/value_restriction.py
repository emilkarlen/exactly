import types
import unittest
from collections import Counter

from exactly_lib.symbol import value_restriction as sut
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.value_restriction import ReferenceRestrictions
from exactly_lib.symbol.value_structure import SymbolValueResolver, ValueType
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.symbol.test_resources import symbol_utils


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestUsageOfDirectRestriction),
        unittest.makeSuite(TestUsageOfRestrictionOnIndirectReferencedSymbol),
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

    def test_that_only_direct_symbol_is_processed(self):
        # ARRANGE #
        level_2_symbol = symbol_table_entry('level_2_symbol', [])
        restrictions_that_should_not_be_used = ReferenceRestrictions(direct=ValueRestrictionThatRaisesErrorIfApplied(),
                                                                     indirect=ValueRestrictionThatRaisesErrorIfApplied())

        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             [reference_to(level_2_symbol, restrictions_that_should_not_be_used)])
        level_1b_symbol = symbol_table_entry('level_1b_symbol', [])
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                                             reference_to(level_1b_symbol, restrictions_that_should_not_be_used)])
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=unconditional_satisfaction)
        restrictions_to_test = ReferenceRestrictions(direct=restriction_that_registers_processed_symbols)
        # ACT #
        restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {level_0_symbol.key: 1}
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

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
                                                         indirect=restriction_on_every)
                assert isinstance(symbol_to_check.value, sut.ValueContainer)
                actual_result = restrictions.is_satisfied_by(symbol_table,
                                                             symbol_to_check.key,
                                                             symbol_to_check.value)
                self.assertEqual(expected_result, actual_result)


class TestUsageOfRestrictionOnIndirectReferencedSymbol(unittest.TestCase):
    def test_that_every_referenced_symbol_is_processed_once(self):
        # ARRANGE #
        level_2_symbol = symbol_table_entry('level_2_symbol', [])
        restrictions_that_should_not_be_used = ReferenceRestrictions(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             [reference_to(level_2_symbol, restrictions_that_should_not_be_used)])
        level_1b_symbol = symbol_table_entry('level_1b_symbol', [])
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                                             reference_to(level_1b_symbol, restrictions_that_should_not_be_used)])
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=unconditional_satisfaction)
        restrictions_to_test = ReferenceRestrictions(indirect=restriction_that_registers_processed_symbols,
                                                     direct=unconditionally_satisfied_value_restriction())
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        result_that_indicates_success = None
        self.assertEqual(result_that_indicates_success,
                         actual_result,
                         'result of processing')
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.key: 1,
            level_1b_symbol.key: 1,
            level_2_symbol.key: 1
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def test_unconditionally_failing_value_restriction(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = ReferenceRestrictions(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             [])
        level_1b_symbol = symbol_table_entry('level_1b_symbol', [])
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                                             reference_to(level_1b_symbol, restrictions_that_should_not_be_used)])
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol]

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        result_that_indicates_error = 'result that indicates error'
        function_that_reports_error = unconditional_dissatisfaction(result_that_indicates_error)
        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=function_that_reports_error)
        restrictions_to_test = ReferenceRestrictions(indirect=restriction_that_registers_processed_symbols,
                                                     direct=unconditionally_satisfied_value_restriction())
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        self.assertEqual(result_that_indicates_error,
                         actual_result,
                         'result of processing')
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.key: 1,
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def test_combination_of_satisfied_and_dissatisified_symbols(self):
        # ARRANGE #
        satisfied_value_type = ValueType.STRING
        disSatisfied_value_type = ValueType.PATH
        level_2_symbol = symbol_table_entry('level_2_symbol',
                                            references=[],
                                            value_type=disSatisfied_value_type)
        restrictions_that_should_not_be_used = ReferenceRestrictions(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             references=[reference_to(level_2_symbol,
                                                                      restrictions_that_should_not_be_used)],
                                             value_type=satisfied_value_type)
        level_1b_symbol = symbol_table_entry('level_1b_symbol',
                                             references=[],
                                             value_type=satisfied_value_type)
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            references=[reference_to(level_1a_symbol,
                                                                     restrictions_that_should_not_be_used),
                                                        reference_to(level_1b_symbol,
                                                                     restrictions_that_should_not_be_used)],
                                            value_type=satisfied_value_type)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        restriction_on_every = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=dissatisfaction_if_value_type_is(disSatisfied_value_type))
        restrictions_to_test = ReferenceRestrictions(
            indirect=restriction_on_every,
            direct=RestrictionWithConstantResult(None))
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        self.assertIsNotNone(actual_result,
                             'result of processing')
        actual_processed_symbols = dict(restriction_on_every.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.key: 1,
            level_2_symbol.key: 1,
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)


def unconditionally_satisfied_value_restriction() -> sut.ValueRestriction:
    return RestrictionWithConstantResult(None)


class RestrictionWithConstantResult(sut.ValueRestriction):
    def __init__(self, result):
        self.result = result

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.ValueContainer) -> str:
        return self.result


class ValueRestrictionThatRaisesErrorIfApplied(sut.ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.ValueContainer) -> str:
        raise NotImplementedError('It is an error if this method is called')


class RestrictionThatRegistersProcessedSymbols(sut.ValueRestriction):
    def __init__(self, value_container_2_result__fun: types.FunctionType):
        self.value_container_2_result__fun = value_container_2_result__fun
        self.visited = Counter()

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.ValueContainer) -> str:
        self.visited.update([symbol_name])
        return self.value_container_2_result__fun(value)


class SymbolValueResolverForTest(SymbolValueResolver):
    def __init__(self,
                 references: list,
                 value_type: ValueType):
        self._value_type = value_type
        self._references = references

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('It is an error if this method is called')

    @property
    def references(self) -> list:
        return self._references


def symbol_table_entry(symbol_name: str,
                       references,
                       value_type: ValueType = ValueType.STRING) -> Entry:
    return Entry(symbol_name,
                 symbol_utils.container(SymbolValueResolverForTest(references,
                                                                   value_type=value_type)))


def reference_to(entry: Entry, restrictions: ReferenceRestrictions) -> SymbolReference:
    return SymbolReference(entry.key, restrictions)


def unconditional_satisfaction(value: sut.ValueContainer) -> str:
    return None


def unconditional_dissatisfaction(result: str) -> types.FunctionType:
    def ret_val(value: sut.ValueContainer) -> str:
        return result

    return ret_val


def dissatisfaction_if_value_type_is(value_type: ValueType) -> types.FunctionType:
    def ret_val(value: sut.ValueContainer) -> str:
        if value.value.value_type is value_type:
            return 'fail due to value type is ' + str(value_type)
        return None

    return ret_val
