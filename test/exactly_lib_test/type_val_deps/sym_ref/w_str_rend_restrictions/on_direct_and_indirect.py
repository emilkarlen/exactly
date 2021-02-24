import unittest
from collections import Counter
from typing import Optional, Callable

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.symbol.sdv_structure import SymbolContainer, Failure
from exactly_lib.symbol.value_type import WithStrRenderingType, ValueType, W_STR_RENDERING_TYPE_2_VALUE_TYPE
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions as sut
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.impl.symbols_handling.symbol_validation import RestrictionThatIsAlwaysSatisfied
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.sym_ref.w_str_rend_restrictions.test_resources import TestDataSymbolContext, \
    TestLogicSymbolContext, \
    reference_to, unconditional_satisfaction, unconditional_dissatisfaction, dissatisfaction_if_value_type_is
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.data_restrictions_assertions import \
    is_failure__of_direct_reference, \
    is_failure__of_indirect_reference
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.value_restrictions import \
    ValueRestrictionWithConstantResult, \
    ValueRestrictionThatRaisesErrorIfApplied
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestUsageOfDirectRestriction),
        unittest.makeSuite(TestUsageOfRestrictionOnIndirectReferencedSymbol),
    ])


class TestUsageOfDirectRestriction(unittest.TestCase):
    def test_satisfied_restriction(self):
        expected_result = asrt.is_none
        restriction_on_direct = ValueRestrictionWithConstantResult.of_unconditionally_satisfied()
        self._check_direct_with_satisfied_variants_for_restriction_on_every_node(restriction_on_direct,
                                                                                 expected_result)

    def test_unsatisfied_restriction(self):
        error_message = 'error message'
        expected_result = is_failure__of_direct_reference(
            message=asrt_text_doc.is_string_for_test_that_equals(error_message)
        )
        restriction_on_direct = ValueRestrictionWithConstantResult.of_err_msg_for_test(error_message)
        self._check_direct_with_satisfied_variants_for_restriction_on_every_node(restriction_on_direct,
                                                                                 expected_result)

    def test_that_only_direct_symbol_is_processed_when_restriction_on_indirect_ref_is_absent(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )
        references = []
        level_2_symbol = TestDataSymbolContext.of('level_2_symbol', references, WithStrRenderingType.STRING)
        references1 = [reference_to(level_2_symbol, restrictions_that_should_not_be_used)]
        level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references1, WithStrRenderingType.STRING)
        references2 = []
        level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references2, WithStrRenderingType.STRING)
        references3 = [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                       reference_to(level_1b_symbol, restrictions_that_should_not_be_used)]
        level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references3, WithStrRenderingType.STRING)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            symbol_container_2_result=unconditional_satisfaction)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=restriction_that_registers_processed_symbols,
        )
        # ACT #
        restrictions_to_test.is_satisfied_by(symbol_table,
                                             level_0_symbol.name,
                                             level_0_symbol.symbol_table_container)
        # ASSERT #
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {level_0_symbol.name: 1}
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def _check_direct_with_satisfied_variants_for_restriction_on_every_node(
            self,
            restriction_on_direct_node: ValueRestriction,
            expected_result: Assertion[Optional[Failure]],
    ):
        symbol_to_check = StringConstantSymbolContext('symbol_name')
        restriction_on_every_cases = [
            NameAndValue(
                'restriction on every is None',
                None,
            ),
            NameAndValue(
                'restriction on every is unconditionally satisfied',
                RestrictionThatIsAlwaysSatisfied(),
            ),
        ]
        for restriction_on_every_case in restriction_on_every_cases:
            with self.subTest(restriction_on_every_case.name):
                restrictions = sut.ReferenceRestrictionsOnDirectAndIndirect(
                    direct=restriction_on_direct_node,
                    indirect=restriction_on_every_case.value
                )
                actual_result = restrictions.is_satisfied_by(symbol_to_check.symbol_table,
                                                             symbol_to_check.name,
                                                             symbol_to_check.symbol_table_container)
                expected_result.apply_with_message(self, actual_result, 'return value')


class TestUsageOfRestrictionOnIndirectReferencedSymbol(unittest.TestCase):
    def test_that_every_referenced_symbol_is_processed_once(self):
        # ARRANGE #
        references = []
        level_2_symbol = TestDataSymbolContext.of('level_2_symbol', references, WithStrRenderingType.STRING)
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )

        references1 = [reference_to(level_2_symbol, restrictions_that_should_not_be_used)]
        level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references1, WithStrRenderingType.STRING)
        references2 = []
        level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references2, WithStrRenderingType.STRING)
        references3 = [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                       reference_to(level_1b_symbol, restrictions_that_should_not_be_used)]
        level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references3, WithStrRenderingType.STRING)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            symbol_container_2_result=unconditional_satisfaction)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_that_registers_processed_symbols,
            direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied(),
        )
        # ACT #
        container = level_0_symbol.symbol_table_container
        assert isinstance(container, SymbolContainer), 'Expects a SymbolContainer'
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.name, container)
        # ASSERT #
        result_that_indicates_success = None
        self.assertEqual(result_that_indicates_success,
                         actual_result,
                         'result of processing')
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.name: 1,
            level_1b_symbol.name: 1,
            level_2_symbol.name: 1
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def test_unconditionally_failing_restriction_on_indirect_referenced_symbol(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )

        references = []
        level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references, WithStrRenderingType.STRING)
        references1 = []
        level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references1, WithStrRenderingType.STRING)
        references2 = [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                       reference_to(level_1b_symbol, restrictions_that_should_not_be_used)]
        level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references2, WithStrRenderingType.STRING)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        result_that_indicates_error = 'result that indicates error'
        function_that_reports_error = unconditional_dissatisfaction(result_that_indicates_error)
        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            symbol_container_2_result=function_that_reports_error)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_that_registers_processed_symbols,
            direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied(),
            meaning_of_failure_of_indirect_reference=
            asrt_text_doc.new_single_string_text_for_test__optional('meaning of failure'),
        )
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.name,
                                                             level_0_symbol.symbol_table_container)
        # ASSERT #
        result_assertion = is_failure__of_indirect_reference(
            failing_symbol=asrt.equals(level_1a_symbol.name),
            path_to_failing_symbol=asrt.equals([]),
            error_message=asrt_text_doc.is_string_for_test_that_equals(result_that_indicates_error),
            meaning_of_failure=asrt_text_doc.is_string_for_test_that_equals('meaning of failure')
        )
        result_assertion.apply_with_message(self, actual_result, 'result of processing')
        actual_processed_symbols = dict(restriction_that_registers_processed_symbols.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.name: 1,
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)

    def test_combination_of_satisfied_and_dissatisfied_symbols(self):
        # ARRANGE #
        references = []
        references4 = []
        dissatisfied_level_2_symbol_variants = [
            (
                ValueType.PATH,
                TestDataSymbolContext.of('level_2_symbol', references, WithStrRenderingType.PATH)
            ),
            (
                ValueType.FILE_MATCHER,
                TestLogicSymbolContext.of('level_2_symbol', references4, ValueType.FILE_MATCHER)
            ),
        ]
        for dissatisfied_value_type, dissatisfied_level_2_symbol in dissatisfied_level_2_symbol_variants:
            with self.subTest(dissatisfied_value_type=str(dissatisfied_value_type)):
                satisfied_value_type = WithStrRenderingType.STRING
                restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
                    direct=ValueRestrictionThatRaisesErrorIfApplied(),
                    indirect=ValueRestrictionThatRaisesErrorIfApplied(),
                )

                references1 = [reference_to(dissatisfied_level_2_symbol,
                                            restrictions_that_should_not_be_used)]
                level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references1, satisfied_value_type)
                references2 = []
                level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references2, satisfied_value_type)
                references3 = [reference_to(level_1a_symbol,
                                            restrictions_that_should_not_be_used),
                               reference_to(level_1b_symbol,
                                            restrictions_that_should_not_be_used)]
                level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references3, satisfied_value_type)
                symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, dissatisfied_level_2_symbol]

                symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

                restriction_on_every_indirect = RestrictionThatRegistersProcessedSymbols(
                    symbol_container_2_result=dissatisfaction_if_value_type_is(dissatisfied_value_type))
                restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
                    indirect=restriction_on_every_indirect,
                    direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied(),
                    meaning_of_failure_of_indirect_reference=
                    asrt_text_doc.new_single_string_text_for_test__optional('meaning of failure'),
                )
                # ACT #
                actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.name,
                                                                     level_0_symbol.symbol_table_container)
                # ASSERT #
                expected_result = is_failure__of_indirect_reference(
                    failing_symbol=asrt.equals(dissatisfied_level_2_symbol.name),
                    path_to_failing_symbol=asrt.equals(
                        [level_1a_symbol.name]),
                    meaning_of_failure=asrt_text_doc.is_string_for_test_that_equals('meaning of failure')
                )
                expected_result.apply_with_message(self, actual_result, 'result of processing')
                actual_processed_symbols = dict(restriction_on_every_indirect.visited.items())
                expected_processed_symbol = {
                    level_1a_symbol.name: 1,
                    dissatisfied_level_2_symbol.name: 1,
                }
                self.assertEqual(expected_processed_symbol,
                                 actual_processed_symbols)

    def test_long_path_to_symbol_that_fails(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )
        satisfied_value_type = WithStrRenderingType.STRING
        dissatisfied_value_type = WithStrRenderingType.PATH

        references = []
        level_3_symbol = TestDataSymbolContext.of('level_3_symbol', references, dissatisfied_value_type)
        references1 = [reference_to(level_3_symbol,
                                    restrictions_that_should_not_be_used)]
        level_2_symbol = TestDataSymbolContext.of('level_2_symbol', references1, satisfied_value_type)
        references2 = []
        level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references2, satisfied_value_type)
        references3 = [reference_to(level_2_symbol,
                                    restrictions_that_should_not_be_used)]
        level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references3, satisfied_value_type)
        references4 = [reference_to(level_1a_symbol,
                                    restrictions_that_should_not_be_used),
                       reference_to(level_1b_symbol,
                                    restrictions_that_should_not_be_used)]
        level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references4, satisfied_value_type)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol, level_3_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        restriction_on_every_indirect = RestrictionThatRegistersProcessedSymbols(
            symbol_container_2_result=dissatisfaction_if_value_type_is(
                W_STR_RENDERING_TYPE_2_VALUE_TYPE[dissatisfied_value_type]))
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_on_every_indirect,
            direct=ValueRestrictionWithConstantResult.of_unconditionally_satisfied(),
            meaning_of_failure_of_indirect_reference=
            asrt_text_doc.new_single_string_text_for_test__optional('meaning of failure'),
        )
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.name,
                                                             level_0_symbol.symbol_table_container)
        # ASSERT #
        expected_result = is_failure__of_indirect_reference(
            failing_symbol=asrt.equals(level_3_symbol.name),
            path_to_failing_symbol=asrt.equals([level_1b_symbol.name,
                                                level_2_symbol.name]),
            meaning_of_failure=asrt_text_doc.is_string_for_test_that_equals('meaning of failure'),
        )
        expected_result.apply_with_message(self, actual_result, 'result of processing')
        actual_processed_symbols = dict(restriction_on_every_indirect.visited.items())
        expected_processed_symbol = {
            level_1a_symbol.name: 1,
            level_1b_symbol.name: 1,
            level_2_symbol.name: 1,
            level_3_symbol.name: 1,
        }
        self.assertEqual(expected_processed_symbol,
                         actual_processed_symbols)


class RestrictionThatRegistersProcessedSymbols(ValueRestriction):
    def __init__(self, symbol_container_2_result: Callable[[SymbolContainer], Optional[str]]):
        self.symbol_container_2_result = symbol_container_2_result
        self.visited = Counter()

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        self.visited.update([symbol_name])
        error_message = self.symbol_container_2_result(value)
        return (
            ErrorMessageWithFixTip(asrt_text_doc.new_single_string_text_for_test(error_message))
            if error_message
            else None)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
