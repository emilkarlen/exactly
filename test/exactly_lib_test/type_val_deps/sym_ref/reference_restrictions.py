import unittest
from collections import Counter
from typing import Sequence, Optional, Callable

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol import value_type
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference, \
    ReferenceRestrictions, Failure, SymbolDependentValue
from exactly_lib.symbol.value_type import DataValueType, ValueType, LogicValueType, DATA_TYPE_2_VALUE_TYPE
from exactly_lib.type_val_deps.dep_variants.data.data_type_sdv import DataTypeSdv
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions as sut, value_restrictions as vr
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.impl.symbols_handling.symbol_validation import RestrictionThatIsAlwaysSatisfied
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext, ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.data.test_resources import data_type_reference_visitor
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    value_restriction_that_is_unconditionally_satisfied, is_failure_of_direct_reference, \
    is_failure_of_indirect_reference, value_restriction_that_is_unconditionally_unsatisfied
from exactly_lib_test.type_val_deps.data.test_resources.symbol_context import DataSymbolValueContext, \
    DataTypeSymbolContext
from exactly_lib_test.type_val_deps.logic.test_resources.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.string_transformers import \
    StringTransformerSdvConstantTestImpl
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


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
            vr.AnyDataTypeRestriction()))
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


class _ReferenceRestrictionsVisitorThatRegisterClassOfVisitMethod(
    data_type_reference_visitor.DataTypeReferenceRestrictionsVisitor):
    def __init__(self, return_value):
        self.visited_classes = []
        self.return_value = return_value

    def visit_direct_and_indirect(self, x: vr.AnyDataTypeRestriction):
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
        expected_result = is_failure_of_direct_reference(
            message=asrt_text_doc.is_string_for_test_that_equals(error_message)
        )
        restriction_on_direct = restriction_with_constant_failure(error_message)
        self._check_direct_with_satisfied_variants_for_restriction_on_every_node(restriction_on_direct,
                                                                                 expected_result)

    def test_that_only_direct_symbol_is_processed_when_restriction_on_indirect_ref_is_absent(self):
        # ARRANGE #
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )
        references = []
        level_2_symbol = TestDataSymbolContext.of('level_2_symbol', references, DataValueType.STRING)
        references1 = [reference_to(level_2_symbol, restrictions_that_should_not_be_used)]
        level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references1, DataValueType.STRING)
        references2 = []
        level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references2, DataValueType.STRING)
        references3 = [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                       reference_to(level_1b_symbol, restrictions_that_should_not_be_used)]
        level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references3, DataValueType.STRING)
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
            restriction_on_direct_node: vr.ValueRestriction,
            expected_result: Assertion[Optional[Failure]]):
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
        level_2_symbol = TestDataSymbolContext.of('level_2_symbol', references, DataValueType.STRING)
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )

        references1 = [reference_to(level_2_symbol, restrictions_that_should_not_be_used)]
        level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references1, DataValueType.STRING)
        references2 = []
        level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references2, DataValueType.STRING)
        references3 = [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                       reference_to(level_1b_symbol, restrictions_that_should_not_be_used)]
        level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references3, DataValueType.STRING)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol, level_2_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            symbol_container_2_result=unconditional_satisfaction)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_that_registers_processed_symbols,
            direct=unconditionally_satisfied_value_restriction(),
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
        level_1a_symbol = TestDataSymbolContext.of('level_1a_symbol', references, DataValueType.STRING)
        references1 = []
        level_1b_symbol = TestDataSymbolContext.of('level_1b_symbol', references1, DataValueType.STRING)
        references2 = [reference_to(level_1a_symbol, restrictions_that_should_not_be_used),
                       reference_to(level_1b_symbol, restrictions_that_should_not_be_used)]
        level_0_symbol = TestDataSymbolContext.of('level_0_symbol', references2, DataValueType.STRING)
        symbol_table_entries = [level_0_symbol, level_1a_symbol, level_1b_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        result_that_indicates_error = 'result that indicates error'
        function_that_reports_error = unconditional_dissatisfaction(result_that_indicates_error)
        restriction_that_registers_processed_symbols = RestrictionThatRegistersProcessedSymbols(
            symbol_container_2_result=function_that_reports_error)
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_that_registers_processed_symbols,
            direct=unconditionally_satisfied_value_restriction(),
            meaning_of_failure_of_indirect_reference=
            asrt_text_doc.new_single_string_text_for_test__optional('meaning of failure'),
        )
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.name,
                                                             level_0_symbol.symbol_table_container)
        # ASSERT #
        result_assertion = is_failure_of_indirect_reference(
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
                TestDataSymbolContext.of('level_2_symbol', references, DataValueType.PATH)
            ),
            (
                ValueType.FILE_MATCHER,
                TestLogicSymbolContext.of('level_2_symbol', references4, LogicValueType.FILE_MATCHER)
            ),
        ]
        for dissatisfied_value_type, dissatisfied_level_2_symbol in dissatisfied_level_2_symbol_variants:
            with self.subTest(dissatisfied_value_type=str(dissatisfied_value_type)):
                satisfied_value_type = DataValueType.STRING
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
                    direct=unconditionally_satisfied_value_restriction(),
                    meaning_of_failure_of_indirect_reference=
                    asrt_text_doc.new_single_string_text_for_test__optional('meaning of failure'),
                )
                # ACT #
                actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.name,
                                                                     level_0_symbol.symbol_table_container)
                # ASSERT #
                expected_result = is_failure_of_indirect_reference(
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
        satisfied_value_type = DataValueType.STRING
        dissatisfied_value_type = DataValueType.PATH

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
                DATA_TYPE_2_VALUE_TYPE[dissatisfied_value_type]))
        restrictions_to_test = sut.ReferenceRestrictionsOnDirectAndIndirect(
            indirect=restriction_on_every_indirect,
            direct=unconditionally_satisfied_value_restriction(),
            meaning_of_failure_of_indirect_reference=
            asrt_text_doc.new_single_string_text_for_test__optional('meaning of failure'),
        )
        # ACT #
        actual_result = restrictions_to_test.is_satisfied_by(symbol_table, level_0_symbol.name,
                                                             level_0_symbol.symbol_table_container)
        # ASSERT #
        expected_result = is_failure_of_indirect_reference(
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


class TestOrReferenceRestrictions(unittest.TestCase):
    def test_satisfied(self):
        cases = [
            NameAndValue(
                'single satisfied string-selector restriction, unconditionally satisfied part',
                sut.OrReferenceRestrictions([
                    sut.OrRestrictionPart(DataValueType.STRING,
                                          sut.ReferenceRestrictionsOnDirectAndIndirect(
                                              direct=value_restriction_that_is_unconditionally_satisfied()))
                ])
            ),
            NameAndValue(
                'multiple unconditionally satisfied restrictions',
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
        for case in cases:
            with self.subTest(msg=case.name):
                actual = case.value.is_satisfied_by(*self._symbol_setup_with_indirectly_referenced_symbol())
                self.assertIsNone(actual)

    def test_unsatisfied(self):

        def mk_err_msg(symbol_name: str,
                       value_type: ValueType) -> str:
            return symbol_name + ': ' + 'Value type of tested symbol is ' + str(value_type)

        def value_type_error_message_function(symbol_name: str,
                                              container: SymbolContainer) -> TextRenderer:
            sdv = container.sdv
            assert isinstance(sdv, SymbolDependentValue)  # Type info for IDE
            return asrt_text_doc.new_single_string_text_for_test(mk_err_msg(symbol_name, container.value_type))

        references = []
        referenced_symbol_cases = [
            NameAndValue(
                'data symbol',
                TestDataSymbolContext.of('referenced_data_symbol', references, DataValueType.STRING)
            ),
            NameAndValue(
                'logic symbol',
                StringTransformerSymbolContext.of_sdv('referenced_logic_symbol',
                                                      StringTransformerSdvConstantTestImpl(
                                                          string_transformers.arbitrary(),
                                                          references=[]))
            ),
        ]
        for referenced_symbol_case in referenced_symbol_cases:
            restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
                direct=ValueRestrictionThatRaisesErrorIfApplied(),
                indirect=ValueRestrictionThatRaisesErrorIfApplied(),
            )

            value_type_of_referencing_symbol = DataValueType.STRING
            value_type_other_than_referencing_symbol = DataValueType.PATH

            references1 = [reference_to(referenced_symbol_case.value,
                                        restrictions_that_should_not_be_used)]
            referencing_symbol = TestDataSymbolContext.of('referencing_symbol', references1,
                                                          value_type_of_referencing_symbol)
            symbol_table_entries = [referencing_symbol, referenced_symbol_case.value]

            symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)
            cases = [
                NEA('no restriction parts / default error message generator',
                    is_failure_of_direct_reference(),
                    sut.OrReferenceRestrictions([]),
                    ),
                NEA('no restriction parts / custom error message generator',
                    is_failure_of_direct_reference(
                        message=asrt_text_doc.is_string_for_test_that_equals(
                            mk_err_msg(referencing_symbol.name,
                                       DATA_TYPE_2_VALUE_TYPE[value_type_of_referencing_symbol])
                        ),
                    ),
                    sut.OrReferenceRestrictions([], value_type_error_message_function),
                    ),
                NEA('single direct: unsatisfied selector',
                    is_failure_of_direct_reference(),
                    sut.OrReferenceRestrictions([
                        sut.OrRestrictionPart(value_type_other_than_referencing_symbol,
                                              sut.ReferenceRestrictionsOnDirectAndIndirect(
                                                  direct=value_restriction_that_is_unconditionally_satisfied())),
                    ]),
                    ),
                NEA('single direct: satisfied selector, unsatisfied part-restriction',
                    is_failure_of_direct_reference(),
                    sut.OrReferenceRestrictions([
                        sut.OrRestrictionPart(value_type_of_referencing_symbol,
                                              sut.ReferenceRestrictionsOnDirectAndIndirect(
                                                  direct=value_restriction_that_is_unconditionally_unsatisfied())),
                    ]),
                    ),
                NEA('multiple direct: unconditionally unsatisfied selectors',
                    is_failure_of_direct_reference(),
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
                    ),
                NEA('multiple direct: unconditionally satisfied selectors, unconditionally satisfied restrictions',
                    is_failure_of_direct_reference(),
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
                    ),
                NEA('first: selector=satisfied, direct=satisfied, indirect=unsatisfied. second:satisfied ',
                    is_failure_of_indirect_reference(failing_symbol=asrt.equals(referenced_symbol_case.value.name),
                                                     path_to_failing_symbol=asrt.equals([])),
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
                    ),
            ]

            for case in cases:
                with self.subTest(referenced_symbol_case_name=referenced_symbol_case.name,
                                  msg=case.name):
                    actual = case.actual.is_satisfied_by(symbol_table,
                                                         referencing_symbol.name,
                                                         referencing_symbol.symbol_table_container)
                    case.expected.apply_with_message(self, actual, 'return value')

    @staticmethod
    def _symbol_setup_with_indirectly_referenced_symbol():
        references = []
        referenced_symbol = TestDataSymbolContext.of('referenced_symbol', references, DataValueType.STRING)
        restrictions_that_should_not_be_used = sut.ReferenceRestrictionsOnDirectAndIndirect(
            direct=ValueRestrictionThatRaisesErrorIfApplied(),
            indirect=ValueRestrictionThatRaisesErrorIfApplied(),
        )

        references1 = [reference_to(referenced_symbol,
                                    restrictions_that_should_not_be_used)]
        referencing_symbol = TestDataSymbolContext.of('referencing_symbol', references1, DataValueType.STRING)
        symbol_table_entries = [referencing_symbol, referenced_symbol]

        symbol_table = SymbolContext.symbol_table_of_contexts(symbol_table_entries)

        return symbol_table, referencing_symbol.name, referencing_symbol.symbol_table_container,


def unconditionally_satisfied_value_restriction() -> vr.ValueRestriction:
    return RestrictionWithConstantResult(None)


def restriction_with_constant_failure(error_message: str) -> vr.ValueRestriction:
    return RestrictionWithConstantResult(ErrorMessageWithFixTip(
        asrt_text_doc.new_single_string_text_for_test(error_message))
    )


class RestrictionWithConstantResult(vr.ValueRestriction):
    def __init__(self, result: Optional[ErrorMessageWithFixTip]):
        self.result = result

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        return self.result


class ValueRestrictionThatRaisesErrorIfApplied(vr.ValueRestriction):
    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        raise NotImplementedError('It is an error if this method is called')


class RestrictionThatRegistersProcessedSymbols(vr.ValueRestriction):
    def __init__(self, symbol_container_2_result: Callable[[sut.SymbolContainer], Optional[str]]):
        self.symbol_container_2_result = symbol_container_2_result
        self.visited = Counter()

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        value: sut.SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        self.visited.update([symbol_name])
        error_message = self.symbol_container_2_result(value)
        return (
            ErrorMessageWithFixTip(asrt_text_doc.new_single_string_text_for_test(error_message))
            if error_message
            else None)


class DataTypeSdvForTest(DataTypeSdv):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    def resolve(self, symbols: SymbolTable):
        raise NotImplementedError('It is an error if this method is called')

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references


class TestDataSymbolValueContext(DataSymbolValueContext[DataTypeSdvForTest]):
    def __init__(self,
                 sdv: DataTypeSdvForTest,
                 data_value_type: DataValueType,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)
        self._data_value_type = data_value_type
        self._value_type = value_type.DATA_TYPE_2_VALUE_TYPE[data_value_type]

    @staticmethod
    def of(references: Sequence[SymbolReference],
           data_value_type: DataValueType,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestDataSymbolValueContext':
        return TestDataSymbolValueContext(DataTypeSdvForTest(references),
                                          data_value_type,
                                          definition_source)

    @property
    def value_type(self) -> ValueType:
        return self._value_type

    @property
    def data_value_type(self) -> DataValueType:
        return self._data_value_type

    @property
    def assert_equals_sdv(self) -> Assertion[SymbolDependentValue]:
        raise NotImplementedError('unsupported')

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        raise NotImplementedError('unsupported')


class TestDataSymbolContext(DataTypeSymbolContext[DataTypeSdvForTest]):
    def __init__(self,
                 name: str,
                 value: TestDataSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of(symbol_name: str,
           references: Sequence[SymbolReference],
           value_type: DataValueType = DataValueType.STRING,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestDataSymbolContext':
        return TestDataSymbolContext(symbol_name,
                                     TestDataSymbolValueContext.of(references, value_type, definition_source))

    @property
    def value(self) -> TestDataSymbolValueContext:
        return self._value


class FullDepsSdvForTest(FullDepsSdv):
    def __init__(self, references: Sequence[SymbolReference]):
        self._references = references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FullDepsDdv:
        raise NotImplementedError('It is an error if this method is called')


class TestLogicSymbolValueContext(LogicSymbolValueContext[FullDepsSdvForTest]):
    def __init__(self,
                 sdv: FullDepsSdvForTest,
                 logic_value_type: LogicValueType,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)
        self._value_type = value_type.LOGIC_TYPE_2_VALUE_TYPE[logic_value_type]

    @staticmethod
    def of(references: Sequence[SymbolReference],
           logic_value_type: LogicValueType,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestLogicSymbolValueContext':
        return TestLogicSymbolValueContext(FullDepsSdvForTest(references),
                                           logic_value_type,
                                           definition_source)

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        raise NotImplementedError('unsupported')

    @property
    def value_type(self) -> ValueType:
        return self._value_type


class TestLogicSymbolContext(LogicTypeSymbolContext[FullDepsSdvForTest]):
    def __init__(self,
                 name: str,
                 value: TestLogicSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of(symbol_name: str,
           references: Sequence[SymbolReference],
           value_type: LogicValueType = LogicValueType.FILE_MATCHER,
           definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
           ) -> 'TestLogicSymbolContext':
        return TestLogicSymbolContext(symbol_name,
                                      TestLogicSymbolValueContext.of(references, value_type, definition_source))

    @property
    def value(self) -> TestLogicSymbolValueContext:
        return self._value

    @property
    def reference_sdv(self) -> FullDepsSdvForTest:
        raise ValueError('cannot create a reference of test impl')

    @property
    def abstract_syntax(self) -> AbstractSyntax:
        raise NotImplementedError('cannot create a reference of test impl')


class SymbolReferenceAbsStx(AbstractSyntax):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(self.symbol_name)


def reference_to(symbol: SymbolContext, restrictions: ReferenceRestrictions) -> SymbolReference:
    return SymbolReference(symbol.name, restrictions)


def unconditional_satisfaction(value: sut.SymbolContainer) -> Optional[str]:
    return None


def unconditional_dissatisfaction(result: str) -> Callable[[sut.SymbolContainer], Optional[str]]:
    def ret_val(value: sut.SymbolContainer) -> str:
        return result

    return ret_val


def dissatisfaction_if_value_type_is(value_type: ValueType) -> Callable[[sut.SymbolContainer], Optional[str]]:
    def ret_val(container: sut.SymbolContainer) -> Optional[str]:
        if container.value_type is value_type:
            return 'fail due to value type is ' + str(value_type)
        return None

    return ret_val
