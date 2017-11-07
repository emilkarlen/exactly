import types
import unittest
from collections import Counter

from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.type_system import DATA_TYPE_2_VALUE_TYPE
from exactly_lib.symbol.data.restrictions import value_restrictions as vr, reference_restrictions as sut
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure, ValueRestriction
from exactly_lib.symbol.resolver_structure import DataValueResolver, SymbolContainer, LogicValueResolver, \
    SymbolValueResolver
from exactly_lib.symbol.restriction import ReferenceRestrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.value_type import DataValueType, ValueType, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    value_restriction_that_is_unconditionally_satisfied, is_failure_of_direct_reference, \
    is_failure_of_indirect_reference, value_restriction_that_is_unconditionally_unsatisfied
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.lines_transformer import LinesTransformerResolverConstantTestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.values import FakeLinesTransformer
from exactly_lib_test.util.test_resources import symbol_tables


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestReferenceRestrictionVisitor),
        unittest.makeSuite(TestUsageOfDirectRestriction),
        unittest.makeSuite(TestUsageOfRestrictionOnIndirectReferencedSymbol),
        unittest.makeSuite(TestOrReferenceRestrictions),
    ])


class TestReferenceRestrictionVisitor(unittest.TestCase):
    def test_direct_and_indirect(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.ReferenceRestrictionsOnDirectAndIndirect(
            vr.AnySymbolTypeRestriction()))
        # ASSERT #
        self.assertEqual([sut.ReferenceRestrictionsOnDirectAndIndirect],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_or(self):
        # ARRANGE #
        expected_return_value = 87
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.OrReferenceRestrictions([]))
        # ASSERT #
        self.assertEqual([sut.OrReferenceRestrictions],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod("not used")
        invalid_value = 'a string is not a sub class of ' + str(ValueRestriction)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            visitor.visit(invalid_value)


class _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(sut.SymbolReferenceRestrictionsVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_direct_and_indirect(self, x: vr.AnySymbolTypeRestriction):
        self.visited_classes.append(sut.ReferenceRestrictionsOnDirectAndIndirect)
        return self.return_value

    def visit_or(self, x: vr.StringRestriction):
        self.visited_classes.append(sut.OrReferenceRestrictions)
        return self.return_value


class TestUsageOfDirectRestriction(unittest.TestCase):
    def test_satisfied_restriction(self):
        expected_result = asrt.is_none
        restriction_on_direct = RestrictionWithConstantResult(None)
        self._check_direct_with_satisfied_variants_for_restriction_on_every_node(restriction_on_direct,
                                                                                 expected_result)

    def test_unsatisfied_restriction(self):
        error_message = 'error message'
        expected_result = is_failure_of_direct_reference(message=asrt.equals(error_message))
        restriction_on_direct = restriction_with_constant_failure(error_message)
        self._check_direct_with_satisfied_variants_for_restriction_on_every_node(restriction_on_direct,
                                                                                 expected_result)

    def test_that_only_direct_symbol_is_processed_when_restriction_on_indirect_ref_is_absent(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())
        level_2_symbol = symbol_table_entry('level_2_symbol', [])
        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             [reference_to(level_2_symbol, restrictions_that_should_not_be_used)])
        level_1b_symbol = symbol_table_entry('level_1b_symbol', [])
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                                             reference_to(level_1b_symbol, restrictions_that_should_not_be_used)])
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = symbol_tables.symbol_table_from_entries(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            resolver_container_2_result__fun=unconditional_satisfaction)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=restriction_that_registers_processed_symbols)
        # ACT #
        restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {level_0_symbol.key: 1}
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def _check_direct_with_satisfied_variants_for_restriction_on_every_node(
            self,
            restriction_on_direct_node: vr.ValueRestriction,
            expected_result: asrt.ValueAssertion):
        symbol_to_check = data_symbol_utils.entry('symbol_name')
        cases = [
            (
                'restriction on every is None',
                None,
                symbol_tables.symbol_table_from_entries([symbol_to_check]),
            ),
            (
                'restriction on every is unconditionally satisfied',
                None,
                symbol_tables.symbol_table_from_entries([symbol_to_check]),
            ),
        ]
        for case_name, restriction_on_every, symbol_table in cases:
            with self.subTest(msg=case_name):
                restrictions = sut.ReferenceRestrictionsOnDirectAndIndirect(direct=restriction_on_direct_node,
                                                                            indirect=restriction_on_every)
                assert isinstance(symbol_to_check.value, sut.SymbolContainer)
                actual_result = restrictions.is_satisfied_by(symbol_table,
                                                             symbol_to_check.key,
                                                             symbol_to_check.value)
                expected_result.apply_with_message(self, actual_result, 'return value')


class TestUsageOfRestrictionOnIndirectReferencedSymbol(unittest.TestCase):
    def test_that_every_referenced_symbol_is_processed_once(self):
        # ARRANGE #
        level_2_symbol = symbol_table_entry('level_2_symbol', [])
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             [reference_to(level_2_symbol, restrictions_that_should_not_be_used)])
        level_1b_symbol = symbol_table_entry('level_1b_symbol', [])
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                                             reference_to(level_1b_symbol, restrictions_that_should_not_be_used)])
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = symbol_tables.symbol_table_from_entries(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            resolver_container_2_result__fun=unconditional_satisfaction)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_that_registers_processed_symbols,
            direct=unconditionally_satisfied_value_restriction())
        # ACT #
        container = level_0_symbol.value
        assert isinstance(container, SymbolContainer), 'Expects a SymbolContainer'
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, container)
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

    def test_unconditionally_failing_restriction_on_indirect_referenced_symbol(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             [])
        level_1b_symbol = symbol_table_entry('level_1b_symbol', [])
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                                             reference_to(level_1b_symbol, restrictions_that_should_not_be_used)])
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol]

        symbol_table = symbol_tables.symbol_table_from_entries(symbol_table_entries)

        result_that_indicates_error = 'result that indicates error'
        function_that_reports_error = unconditional_dissatisfaction(result_that_indicates_error)
        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            resolver_container_2_result__fun=function_that_reports_error)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_that_registers_processed_symbols,
            direct=unconditionally_satisfied_value_restriction(),
            meaning_of_failure_of_indirect_reference='meaning of failure')
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        result_assertion = is_failure_of_indirect_reference(failing_symbol=asrt.equals(level_1a_symbol.key),
                                                            path_to_failing_symbol=asrt.equals([]),
                                                            error_message=asrt.equals(result_that_indicates_error),
                                                            meaning_of_failure=asrt.equals('meaning of failure'))
        result_assertion.apply_with_message(self, actual_result, 'result of processing')
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.key: 1,
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def test_combination_of_satisfied_and_dissatisfied_symbols(self):
        # ARRANGE #
        dissatisfied_level_2_symbol_variants = [
            (
                ValueType.PATH,
                symbol_table_entry('level_2_symbol',
                                   references=[],
                                   value_type=DataValueType.PATH)
            ),
            (
                ValueType.FILE_MATCHER,
                logic_symbol_table_entry('level_2_symbol',
                                         references=[],
                                         value_type=LogicValueType.FILE_MATCHER)
            ),
        ]
        for dissatisfied_value_type, dissatisfied_level_2_symbol in dissatisfied_level_2_symbol_variants:
            with self.subTest(dissatisfied_value_type=str(dissatisfied_value_type)):
                satisfied_value_type = DataValueType.STRING
                restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
                    direct=ValueRestrictionThatRaisesErrorIfApplied(),
                    indirect=ValueRestrictionThatRaisesErrorIfApplied())

                level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                                     references=[reference_to(dissatisfied_level_2_symbol,
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
                symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, dissatisfied_level_2_symbol]

                symbol_table = symbol_tables.symbol_table_from_entries(symbol_table_entries)

                restriction_on_every_indirect = RestrictionThatRegistersProcessedSymbols(
                    resolver_container_2_result__fun=dissatisfaction_if_value_type_is(dissatisfied_value_type))
                restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
                    indirect=restriction_on_every_indirect,
                    direct=unconditionally_satisfied_value_restriction(),
                    meaning_of_failure_of_indirect_reference='meaning of failure')
                # ACT #
                actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key,
                                                                     level_0_symbol.value)
                # ASSERT #
                expected_result = is_failure_of_indirect_reference(
                    failing_symbol=asrt.equals(dissatisfied_level_2_symbol.key),
                    path_to_failing_symbol=asrt.equals(
                        [level_1a_symbol.key]),
                    meaning_of_failure=asrt.equals('meaning of failure'))
                expected_result.apply_with_message(self, actual_result, 'result of processing')
                actual_processed_symbols = dict(restriction_on_every_indirect.visited.items())
                expected_processed_symbol = {
                    level_1a_symbol.key: 1,
                    dissatisfied_level_2_symbol.key: 1,
                }
                self.assertEqual(expected_processed_symbol,
                                 actual_processed_symbols)

    def test_long_path_to_symbol_that_fails(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())
        satisfied_value_type = DataValueType.STRING
        dissatisfied_value_type = DataValueType.PATH

        level_3_symbol = symbol_table_entry('level_3_symbol',
                                            references=[],
                                            value_type=dissatisfied_value_type)
        level_2_symbol = symbol_table_entry('level_2_symbol',
                                            references=[reference_to(level_3_symbol,
                                                                     restrictions_that_should_not_be_used)],
                                            value_type=satisfied_value_type)
        level_1a_symbol = symbol_table_entry('level_1a_symbol',
                                             references=[],
                                             value_type=satisfied_value_type)
        level_1b_symbol = symbol_table_entry('level_1b_symbol',
                                             references=[reference_to(level_2_symbol,
                                                                      restrictions_that_should_not_be_used)],
                                             value_type=satisfied_value_type)
        level_0_symbol = symbol_table_entry('level_0_symbol',
                                            references=[reference_to(level_1a_symbol,
                                                                     restrictions_that_should_not_be_used),
                                                        reference_to(level_1b_symbol,
                                                                     restrictions_that_should_not_be_used)],
                                            value_type=satisfied_value_type)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol, level_3_symbol]

        symbol_table = symbol_tables.symbol_table_from_entries(symbol_table_entries)

        restriction_on_every_indirect = RestrictionThatRegistersProcessedSymbols(
            resolver_container_2_result__fun=dissatisfaction_if_value_type_is(
                DATA_TYPE_2_VALUE_TYPE[dissatisfied_value_type]))
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_on_every_indirect,
            direct=unconditionally_satisfied_value_restriction(),
            meaning_of_failure_of_indirect_reference='meaning of failure')
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        expected_result = is_failure_of_indirect_reference(failing_symbol=asrt.equals(level_3_symbol.key),
                                                           path_to_failing_symbol=asrt.equals([level_1b_symbol.key,
                                                                                               level_2_symbol.key]),
                                                           meaning_of_failure=asrt.equals('meaning of failure'))
        expected_result.apply_with_message(self, actual_result, 'result of processing')
        actual_processed_symbols = dict(restriction_on_every_indirect.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.key: 1,
            level_1b_symbol.key: 1,
            level_2_symbol.key: 1,
            level_3_symbol.key: 1,
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)


class TestOrReferenceRestrictions(unittest.TestCase):
    def test_satisfied(self):
        cases = [
            ('single satisfied string-selector restriction, unconditionally satisfied part',
             sut.OrReferenceRestrictions([
                 sut.OrRestrictionPart(DataValueType.STRING,
                                       sut.ReferenceRestrictionsOnDirectAndIndirect(
                                           direct=value_restriction_that_is_unconditionally_satisfied()))
             ])
             ),
            ('multiple unconditionally satisfied restrictions',
             sut.OrReferenceRestrictions([
                 sut.OrRestrictionPart(DataValueType.STRING,
                                       sut.ReferenceRestrictionsOnDirectAndIndirect(
                                           direct=value_restriction_that_is_unconditionally_satisfied())),
                 sut.OrRestrictionPart(DataValueType.STRING,
                                       sut.ReferenceRestrictionsOnDirectAndIndirect(
                                           direct=value_restriction_that_is_unconditionally_satisfied()))
             ])
             ),
        ]
        for case_name, restrictions in cases:
            with self.subTest(msg=case_name):
                actual = restrictions.is_satisfied_by(*self._symbol_setup_with_indirectly_referenced_symbol())
                self.assertIsNone(actual)

    def test_unsatisfied(self):

        def mk_err_msg(symbol_name: str,
                       value_type: ValueType) -> str:
            return symbol_name + ': ' + 'Value type of tested symbol is ' + str(value_type)

        def value_type_error_message_function(symbol_name: str,
                                              container: SymbolContainer) -> str:
            v = container.resolver
            assert isinstance(v, SymbolValueResolver)  # Type info for IDE
            return mk_err_msg(symbol_name, v.value_type)

        referenced_symbol_cases = [
            ('data symbol',
             symbol_table_entry('referenced_data_symbol',
                                references=[])
             ),
            ('logic symbol',
             Entry('referenced_logic_symbol',
                   symbol_utils.container(
                       LinesTransformerResolverConstantTestImpl(FakeLinesTransformer(),
                                                                references=[])))
             ),
        ]
        for referenced_symbol_case_name, referenced_symbol in referenced_symbol_cases:
            restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
                direct=ValueRestrictionThatRaisesErrorIfApplied(),
                indirect=ValueRestrictionThatRaisesErrorIfApplied())

            value_type_of_referencing_symbol = DataValueType.STRING
            value_type_other_than_referencing_symbol = DataValueType.PATH

            referencing_symbol = symbol_table_entry('referencing_symbol',
                                                    value_type=value_type_of_referencing_symbol,
                                                    references=[reference_to(referenced_symbol,
                                                                             restrictions_that_should_not_be_used)])
            symbol_table_entries = [referencing_symbol, referenced_symbol]

            symbol_table = symbol_tables.symbol_table_from_entries(symbol_table_entries)

            cases = [
                ('no restriction parts / default error message generator',
                 sut.OrReferenceRestrictions([]),
                 is_failure_of_direct_reference(),
                 ),
                ('no restriction parts / custom error message generator',
                 sut.OrReferenceRestrictions([], value_type_error_message_function),
                 is_failure_of_direct_reference(
                     message=asrt.equals(mk_err_msg(referencing_symbol.key,
                                                    DATA_TYPE_2_VALUE_TYPE[value_type_of_referencing_symbol])),
                 )
                 ),
                ('single direct: unsatisfied selector',
                 sut.OrReferenceRestrictions([
                     sut.OrRestrictionPart(value_type_other_than_referencing_symbol,
                                           sut.ReferenceRestrictionsOnDirectAndIndirect(
                                               direct=value_restriction_that_is_unconditionally_satisfied())),
                 ]),
                 is_failure_of_direct_reference(),
                 ),
                ('single direct: satisfied selector, unsatisfied part-restriction',
                 sut.OrReferenceRestrictions([
                     sut.OrRestrictionPart(value_type_of_referencing_symbol,
                                           sut.ReferenceRestrictionsOnDirectAndIndirect(
                                               direct=value_restriction_that_is_unconditionally_unsatisfied())),
                 ]),
                 is_failure_of_direct_reference(),
                 ),
                ('multiple direct: unconditionally unsatisfied selectors',
                 sut.OrReferenceRestrictions([
                     sut.OrRestrictionPart(
                         value_type_other_than_referencing_symbol,
                         sut.ReferenceRestrictionsOnDirectAndIndirect(
                             direct=value_restriction_that_is_unconditionally_unsatisfied())),
                     sut.OrRestrictionPart(
                         value_type_other_than_referencing_symbol,
                         sut.ReferenceRestrictionsOnDirectAndIndirect(
                             direct=value_restriction_that_is_unconditionally_unsatisfied()))
                 ]),
                 is_failure_of_direct_reference(),
                 ),
                ('multiple direct: unconditionally satisfied selectors, unconditionally satisfied restrictions',
                 sut.OrReferenceRestrictions([
                     sut.OrRestrictionPart(
                         value_type_of_referencing_symbol,
                         sut.ReferenceRestrictionsOnDirectAndIndirect(
                             direct=value_restriction_that_is_unconditionally_unsatisfied())),
                     sut.OrRestrictionPart(
                         value_type_of_referencing_symbol,
                         sut.ReferenceRestrictionsOnDirectAndIndirect(
                             direct=value_restriction_that_is_unconditionally_unsatisfied()))
                 ]),
                 is_failure_of_direct_reference(),
                 ),
                ('first: selector=satisfied, direct=satisfied, indirect=unsatisfied. second:satisfied ',
                 sut.OrReferenceRestrictions([
                     sut.OrRestrictionPart(
                         value_type_of_referencing_symbol,
                         sut.ReferenceRestrictionsOnDirectAndIndirect(
                             direct=value_restriction_that_is_unconditionally_satisfied(),
                             indirect=value_restriction_that_is_unconditionally_unsatisfied())),
                     sut.OrRestrictionPart(
                         value_type_of_referencing_symbol,
                         sut.ReferenceRestrictionsOnDirectAndIndirect(
                             direct=value_restriction_that_is_unconditionally_satisfied())),
                 ]),
                 is_failure_of_indirect_reference(failing_symbol=asrt.equals(referenced_symbol.key),
                                                  path_to_failing_symbol=asrt.equals([])),
                 ),
            ]
            for case_name, restrictions, result_assertion in cases:
                with self.subTest(referenced_symbol_case_name=referenced_symbol_case_name,
                                  msg=case_name):
                    actual = restrictions.is_satisfied_by(symbol_table,
                                                          referencing_symbol.key,
                                                          referencing_symbol.value)
                    result_assertion.apply_with_message(self, actual, 'return value')

    @staticmethod
    def _symbol_setup_with_indirectly_referenced_symbol():
        referenced_symbol = symbol_table_entry('referenced_symbol',
                                               references=[])
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        referencing_symbol = symbol_table_entry('referencing_symbol',
                                                value_type=DataValueType.STRING,
                                                references=[reference_to(referenced_symbol,
                                                                         restrictions_that_should_not_be_used)])
        symbol_table_entries = [referencing_symbol, referenced_symbol]

        symbol_table = symbol_tables.symbol_table_from_entries(symbol_table_entries)

        return symbol_table, referencing_symbol.key, referencing_symbol.value,


def unconditionally_satisfied_value_restriction() -> vr.ValueRestriction:
    return RestrictionWithConstantResult(None)


def restriction_with_constant_failure(error_message: str) -> vr.ValueRestriction:
    return RestrictionWithConstantResult(ValueRestrictionFailure(error_message))


class RestrictionWithConstantResult(vr.ValueRestriction):
    def __init__(self, result):
        self.result = result

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.SymbolContainer) -> str:
        return self.result


class ValueRestrictionThatRaisesErrorIfApplied(vr.ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.SymbolContainer) -> str:
        raise NotImplementedError('It is an error if this method is called')


class RestrictionThatRegistersProcessedSymbols(vr.ValueRestriction):
    def __init__(self, resolver_container_2_result__fun: types.FunctionType):
        self.resolver_container_2_result__fun = resolver_container_2_result__fun
        self.visited = Counter()

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.SymbolContainer) -> ValueRestrictionFailure:
        self.visited.update([symbol_name])
        error_message = self.resolver_container_2_result__fun(value)
        return ValueRestrictionFailure(error_message) if error_message else None


class DataValueResolverForTest(DataValueResolver):
    def __init__(self,
                 references: list,
                 data_value_type: DataValueType):
        self._data_value_type = data_value_type
        self._references = references

    @property
    def data_value_type(self) -> DataValueType:
        return self._data_value_type

    @property
    def value_type(self) -> ValueType:
        return type_system.DATA_TYPE_2_VALUE_TYPE[self._data_value_type]

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('It is an error if this method is called')

    @property
    def references(self) -> list:
        return self._references


class LogicValueResolverForTest(LogicValueResolver):
    def __init__(self,
                 references: list,
                 logic_value_type: LogicValueType):
        self._logic_value_type = logic_value_type
        self._references = references

    @property
    def logic_value_type(self) -> LogicValueType:
        return self._logic_value_type

    @property
    def value_type(self) -> ValueType:
        return type_system.LOGIC_TYPE_2_VALUE_TYPE[self._logic_value_type]

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('It is an error if this method is called')

    @property
    def references(self) -> list:
        return self._references


def symbol_table_entry(symbol_name: str,
                       references,
                       value_type: DataValueType = DataValueType.STRING) -> Entry:
    return Entry(symbol_name,
                 symbol_utils.container(DataValueResolverForTest(references,
                                                                 data_value_type=value_type)))


def logic_symbol_table_entry(symbol_name: str,
                             references,
                             value_type: LogicValueType = LogicValueType.FILE_MATCHER) -> Entry:
    return Entry(symbol_name,
                 symbol_utils.container(LogicValueResolverForTest(references,
                                                                  logic_value_type=value_type)))


def reference_to(entry: Entry, restrictions: ReferenceRestrictions) -> SymbolReference:
    return SymbolReference(entry.key, restrictions)


def unconditional_satisfaction(value: sut.SymbolContainer) -> str:
    return None


def unconditional_dissatisfaction(result: str) -> types.FunctionType:
    def ret_val(value: sut.SymbolContainer) -> str:
        return result

    return ret_val


def dissatisfaction_if_value_type_is(value_type: ValueType) -> types.FunctionType:
    def ret_val(container: sut.SymbolContainer) -> str:
        resolver = container.resolver
        assert isinstance(resolver, SymbolValueResolver), 'Expects a NamedElementResolver'
        if resolver.value_type is value_type:
            return 'fail due to value type is ' + str(value_type)
        return None

    return ret_val
