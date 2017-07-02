import types
import unittest
from collections import Counter

from exactly_lib.symbol import concrete_restrictions as sut
from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.value_restriction import ReferenceRestrictions
from exactly_lib.symbol.value_restriction import ValueRestriction
from exactly_lib.symbol.value_structure import SymbolValueResolver, ValueType, ValueContainer
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import \
    value_restriction_that_is_unconditionally_satisfied, value_restriction_that_is_unconditionally_unsatisfied, \
    is_failure_of_direct_reference, is_failure_of_indirect_reference
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.symbol.test_resources.symbol_utils import file_ref_value
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNoRestriction),
        unittest.makeSuite(TestStringRestriction),
        unittest.makeSuite(TestFileRefRelativityRestriction),
        unittest.makeSuite(TestValueRestrictionVisitor),
        unittest.makeSuite(TestReferenceRestrictionVisitor),
        unittest.makeSuite(TestUsageOfDirectRestriction),
        unittest.makeSuite(TestUsageOfRestrictionOnIndirectReferencedSymbol),
        unittest.makeSuite(TestOrReferenceRestrictions),
    ])


class TestNoRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            string_constant('string'),
            file_ref_value(),
        ]
        restriction = sut.NoRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                value_container = container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value_container)
                # ASSERT #
                self.assertIsNone(actual)


class TestStringRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            string_constant('string'),
            string_constant(''),
        ]
        restriction = sut.StringRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                value_container = container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value_container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__not_a_string(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(),
        ]
        restriction = sut.StringRestriction()
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                value_container = container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value_container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestFileRefRelativityRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = sut.FileRefRelativityRestriction(PathRelativityVariants(
            {RelOptionType.REL_ACT, RelOptionType.REL_HOME, RelOptionType.REL_RESULT},
            False))
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                value_container = container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value_container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__relative_paths(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = sut.FileRefRelativityRestriction(PathRelativityVariants(
            {RelOptionType.REL_RESULT},
            False))
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                value_container = container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value_container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestEitherStringOrFileRefRelativityRestriction(unittest.TestCase):
    def test_pass(self):
        # ARRANGE #
        test_cases = [
            string_constant('string'),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]

        restriction = sut.EitherStringOrFileRefRelativityRestriction(
            sut.StringRestriction(),
            sut.FileRefRelativityRestriction(PathRelativityVariants(
                {RelOptionType.REL_ACT,
                 RelOptionType.REL_HOME,
                 RelOptionType.REL_RESULT},
                False))
        )
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                value_container = container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value_container)
                # ASSERT #
                self.assertIsNone(actual)

    def test_fail__failing_file_refs(self):
        # ARRANGE #
        test_cases = [
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_ACT)),
            file_ref_value(file_ref_test_impl(relativity=RelOptionType.REL_HOME)),
        ]
        restriction = sut.EitherStringOrFileRefRelativityRestriction(
            sut.StringRestriction(),
            sut.FileRefRelativityRestriction(PathRelativityVariants(
                {RelOptionType.REL_RESULT},
                False)))
        symbols = empty_symbol_table()
        for value in test_cases:
            with self.subTest(msg='value=' + str(value)):
                value_container = container(value)
                # ACT #
                actual = restriction.is_satisfied_by(symbols, 'symbol_name', value_container)
                # ASSERT #
                self.assertIsNotNone(actual,
                                     'Result should denote failing validation')


class TestValueRestrictionVisitor(unittest.TestCase):
    def test_none(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.NoRestriction())
        # ASSERT #
        self.assertEqual([sut.NoRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_string(self):
        # ARRANGE #
        expected_return_value = 87
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.StringRestriction())
        # ASSERT #
        self.assertEqual([sut.StringRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_file_ref(self):
        # ARRANGE #
        expected_return_value = 69
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.FileRefRelativityRestriction(
            sut.PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertEqual([sut.FileRefRelativityRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_string_or_file_ref(self):
        # ARRANGE #
        expected_return_value = 99
        visitor = _VisitorThatRegisterClassOfVisitMethod(expected_return_value)
        restriction = sut.EitherStringOrFileRefRelativityRestriction(
            sut.StringRestriction(),
            sut.FileRefRelativityRestriction(sut.PathRelativityVariants(set(), False)))
        # ACT #
        actual_return_value = visitor.visit(restriction)
        # ASSERT #
        self.assertEqual([sut.EitherStringOrFileRefRelativityRestriction],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        visitor = _VisitorThatRegisterClassOfVisitMethod("not used")
        non_concept = 'a string is not a sub class of ' + str(ValueRestriction)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            visitor.visit(non_concept)


class TestReferenceRestrictionVisitor(unittest.TestCase):
    def test_direct_and_indirect(self):
        # ARRANGE #
        expected_return_value = 72
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.ReferenceRestrictionsOnDirectAndIndirect(sut.NoRestriction()))
        # ASSERT #
        self.assertEqual([sut.ReferenceRestrictionsOnDirectAndIndirect],
                         visitor.visited_classes,
                         'visited classes')
        self.assertEqual(expected_return_value,
                         actual_return_value,
                         'return value')

    def test_path_or_string(self):
        # ARRANGE #
        expected_return_value = 87
        visitor = _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(expected_return_value)
        # ACT #
        actual_return_value = visitor.visit(sut.PathOrStringReferenceRestrictions(PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertEqual([sut.PathOrStringReferenceRestrictions],
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


class _VisitorThatRegisterClassOfVisitMethod(sut.ValueRestrictionVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_none(self, x: sut.NoRestriction):
        self.visited_classes.append(sut.NoRestriction)
        return self.return_value

    def visit_string(self, x: sut.StringRestriction):
        self.visited_classes.append(sut.StringRestriction)
        return self.return_value

    def visit_file_ref_relativity(self, x: sut.FileRefRelativityRestriction):
        self.visited_classes.append(sut.FileRefRelativityRestriction)
        return self.return_value

    def visit_string_or_file_ref_relativity(self, x: sut.EitherStringOrFileRefRelativityRestriction):
        self.visited_classes.append(sut.EitherStringOrFileRefRelativityRestriction)
        return self.return_value


class _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(sut.ReferenceRestrictionsVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_direct_and_indirect(self, x: sut.NoRestriction):
        self.visited_classes.append(sut.ReferenceRestrictionsOnDirectAndIndirect)
        return self.return_value

    def visit_path_or_string(self, x: sut.PathOrStringReferenceRestrictions):
        self.visited_classes.append(sut.PathOrStringReferenceRestrictions)
        return self.return_value

    def visit_or(self, x: sut.StringRestriction):
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
        expected_result = is_failure_of_direct_reference(error_message=asrt.equals(error_message))
        restriction_on_direct = RestrictionWithConstantResult(error_message)
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

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=unconditional_satisfaction)
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
            restriction_on_direct_node: sut.ValueRestriction,
            expected_result: asrt.ValueAssertion):
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
                restrictions = sut.ReferenceRestrictionsOnDirectAndIndirect(direct=restriction_on_direct_node,
                                                                            indirect=restriction_on_every)
                assert isinstance(symbol_to_check.value, sut.ValueContainer)
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

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=unconditional_satisfaction)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_that_registers_processed_symbols,
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

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        result_that_indicates_error = 'result that indicates error'
        function_that_reports_error = unconditional_dissatisfaction(result_that_indicates_error)
        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=function_that_reports_error)
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
        satisfied_value_type = ValueType.STRING
        dissatisfied_value_type = ValueType.PATH
        level_2_symbol = symbol_table_entry('level_2_symbol',
                                            references=[],
                                            value_type=dissatisfied_value_type)
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
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

        restriction_on_every_indirect = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=dissatisfaction_if_value_type_is(dissatisfied_value_type))
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_on_every_indirect,
            direct=unconditionally_satisfied_value_restriction(),
            meaning_of_failure_of_indirect_reference='meaning of failure')
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.key, level_0_symbol.value)
        # ASSERT #
        expected_result = is_failure_of_indirect_reference(failing_symbol=asrt.equals(level_2_symbol.key),
                                                           path_to_failing_symbol=asrt.equals([level_1a_symbol.key]),
                                                           meaning_of_failure=asrt.equals('meaning of failure'))
        expected_result.apply_with_message(self, actual_result, 'result of processing')
        actual_processed_symbols = dict(restriction_on_every_indirect.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.key: 1,
            level_2_symbol.key: 1,
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def test_long_path_to_symbol_that_fails(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())
        satisfied_value_type = ValueType.STRING
        dissatisfied_value_type = ValueType.PATH

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

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        restriction_on_every_indirect = RestrictionThatRegistersProcessedSymbols(
            value_container_2_result__fun=dissatisfaction_if_value_type_is(dissatisfied_value_type))
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
            ('single unconditionally satisfied restriction',
             sut.OrReferenceRestrictions([
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_satisfied())
             ])
             ),
            ('multiple unconditionally satisfied restrictions',
             sut.OrReferenceRestrictions([
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_satisfied()),
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_satisfied())
             ])
             ),
        ]
        for case_name, restrictions in cases:
            with self.subTest(msg=case_name):
                actual = restrictions.is_satisfied_by(*self._symbol_setup_with_indirectly_referenced_symbol())
                self.assertIsNone(actual)

    def test_unsatisfied(self):
        referenced_symbol = symbol_table_entry('referenced_symbol',
                                               references=[])
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        value_type_of_referencing_symbol = ValueType.STRING
        referencing_symbol = symbol_table_entry('referencing_symbol',
                                                value_type=value_type_of_referencing_symbol,
                                                references=[reference_to(referenced_symbol,
                                                                         restrictions_that_should_not_be_used)])
        symbol_table_entries = [referencing_symbol, referenced_symbol]

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        def value_type_error_message_function(value: ValueContainer) -> str:
            v = value.value
            assert isinstance(v, SymbolValueResolver)  # Type info for IDE
            return 'Value type of tested symbol is ' + str(v.value_type)

        cases = [
            ('no restriction parts / default error message generator',
             sut.OrReferenceRestrictions([]),
             is_failure_of_direct_reference(),
             ),
            ('no restriction parts / custom error message generator',
             sut.OrReferenceRestrictions([], value_type_error_message_function),
             is_failure_of_direct_reference(error_message=asrt.equals('Value type of tested symbol is ' +
                                                                      str(value_type_of_referencing_symbol))),
             ),
            ('single direct: unsatisfied',
             sut.OrReferenceRestrictions([
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_unsatisfied())
             ]),
             is_failure_of_direct_reference(),
             ),
            ('multiple direct: unconditionally satisfied restrictions',
             sut.OrReferenceRestrictions([
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_unsatisfied()),
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_unsatisfied())
             ]),
             is_failure_of_direct_reference(),
             ),
            ('first: direct=satisfied, indirect=unsatisfied. second:satisfied ',
             sut.OrReferenceRestrictions([
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_satisfied(),
                     indirect=value_restriction_that_is_unconditionally_unsatisfied()),
                 sut.ReferenceRestrictionsOnDirectAndIndirect(
                     direct=value_restriction_that_is_unconditionally_satisfied())
             ]),
             is_failure_of_indirect_reference(failing_symbol=asrt.equals(referenced_symbol.key),
                                              path_to_failing_symbol=asrt.equals([])),
             ),
        ]
        for case_name, restrictions, result_assertion in cases:
            with self.subTest(msg=case_name):
                actual = restrictions.is_satisfied_by(symbol_table, referencing_symbol.key, referencing_symbol.value)
                result_assertion.apply_with_message(self, actual, 'return value')

    @staticmethod
    def _symbol_setup_with_indirectly_referenced_symbol():
        referenced_symbol = symbol_table_entry('referenced_symbol',
                                               references=[])
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied())

        referencing_symbol = symbol_table_entry('referencing_symbol',
                                                references=[reference_to(referenced_symbol,
                                                                         restrictions_that_should_not_be_used)])
        symbol_table_entries = [referencing_symbol, referenced_symbol]

        symbol_table = symbol_utils.symbol_table_from_entries(symbol_table_entries)

        return symbol_table, referencing_symbol.key, referencing_symbol.value,


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
