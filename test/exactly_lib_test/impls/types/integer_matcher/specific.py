import unittest
from typing import Sequence, List

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.matcher.impls import comparison_matcher
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.util.description_tree import details
from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.impls.test_resources.validation import validation
from exactly_lib_test.impls.types.integer_matcher.test_resources import parse_check, integration_check
from exactly_lib_test.impls.types.interval.test_resources import with_interval as asrt_w_interval
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation, prim_asrt__constant
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, ParseExpectation, \
    ExecutionExpectation
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.data.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext
from exactly_lib_test.type_val_prims.matcher.test_resources.matcher_assertions import is_equivalent_to, ModelInfo
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree, \
    rendering_assertions as asrt_trace_rendering
from exactly_lib_test.util.interval.test_resources.interval_assertion import PosNeg, is_interval_for_eq, \
    is_interval_for_ne, is_interval_for_lt, is_interval_for_lte, is_interval_for_gt, is_interval_for_gte


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseIntegerMatcher)


class EquivalenceCheck:
    def __init__(self,
                 equivalent: MatcherWTrace[int],
                 models: List[ModelInfo[int]],
                 ):
        self.equivalent = equivalent
        self.models = models

    def assertion(self) -> Assertion[MatcherWTrace[int]]:
        return is_equivalent_to(self.equivalent, self.models)


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 result: EquivalenceCheck,
                 interval: PosNeg[Assertion[IntIntervalWInversion]],
                 references: Assertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                 symbols: SymbolTable = empty_symbol_table(),
                 ):
        self.name = name
        self.source = source
        self.result = result
        self.interval = interval
        self.references = references
        self.symbols = symbols


class ValidationCase:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 source_assertion: Assertion[ParseSource],
                 references: Assertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                 symbols: SymbolTable = empty_symbol_table(),
                 ):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
        self.references = references
        self.symbols = symbols


class TestParseIntegerMatcher(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'no arguments',
                '',
            ),
            NameAndValue(
                'invalid OPERATOR',
                '- 72',
            ),
            NameAndValue(
                'quoted OPERATOR',
                '"{op}" 69'.format(op=comparators.EQ.name),
            ),
            NameAndValue(
                'missing INTEGER',
                comparators.EQ.name,
            ),
        ]
        for case in cases:
            for parser_case in parse_check.PARSE_CHECKERS:
                with self.subTest(sourc_case=case.name,
                                  parser=parser_case.name):
                    parser_case.value.check_invalid_arguments(self,
                                                              remaining_source(case.value))

    def test_successful_parse(self):
        # ARRANGE #
        symbol_69 = StringSymbolContext.of_constant('SYMBOL_69', '69')
        cases = [
            Case(comparators.EQ.name + ' plain integer',
                 comparators.EQ.name + ' 1',
                 interval=is_interval_for_eq(1),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])
                 ),
            Case(comparators.EQ.name + ' plain integer, expr on new line',
                 '\n' + comparators.EQ.name + ' 1',
                 interval=is_interval_for_eq(1),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])
                 ),
            Case(comparators.EQ.name + ' plain integer, integer on new line',
                 comparators.EQ.name + '\n' + ' 1',
                 interval=is_interval_for_eq(1),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])
                 ),
            Case(comparators.NE.name,
                 comparators.NE.name + ' 1',
                 interval=is_interval_for_ne(1),
                 result=EquivalenceCheck(matcher_of(comparators.NE, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])),
            Case(comparators.LT.name,
                 comparators.LT.name + ' 69',
                 interval=is_interval_for_lt(69),
                 result=EquivalenceCheck(matcher_of(comparators.LT, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.LTE.name,
                 comparators.LTE.name + '  69',
                 interval=is_interval_for_lte(69),
                 result=EquivalenceCheck(matcher_of(comparators.LTE, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.GT.name,
                 comparators.GT.name + ' 69',
                 interval=is_interval_for_gt(69),
                 result=EquivalenceCheck(matcher_of(comparators.GT, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.GTE.name,
                 comparators.GTE.name + ' 69',
                 interval=is_interval_for_gte(69),
                 result=EquivalenceCheck(matcher_of(comparators.GTE, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.EQ.name + ' integer expression',
                 '== "69+72"',
                 interval=is_interval_for_eq(69 + 72),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 69 + 72),
                                         [
                                             model_of(69 + 72 - 1),
                                             model_of(69 + 72),
                                             model_of(69 + 72 + 1),
                                         ])),
            Case(comparators.EQ.name + ' with symbol references',
                 '== "{}+72"'.format(symbol_reference_syntax_for_name(symbol_69.name)),
                 interval=is_interval_for_eq(69 + 72),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 69 + 72),
                                         [
                                             model_of(69 + 72 - 1),
                                             model_of(69 + 72),
                                             model_of(69 + 72 + 1),
                                         ]),
                 references=asrt.matches_singleton_sequence(
                     asrt_sym_ref.is_reference_to_string_made_up_of_just_strings(symbol_69.name)
                 ),
                 symbols=symbol_69.symbol_table
                 ),
        ]
        for case in cases:
            for model_info in case.result.models:
                expected_result = case.result.equivalent.matches_w_trace(model_info.model)
                with self.subTest(case=case.name,
                                  model=model_info.description_of_model):
                    integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                        self,
                        Arguments.of_preformatted(case.source),
                        input_=integration_check.constant(model_info.model),
                        arrangement=arrangement_wo_tcds(
                            symbols=case.symbols,
                        ),
                        expectation=Expectation(
                            ParseExpectation(
                                symbol_references=case.references,
                            ),
                            ExecutionExpectation(
                                main_result=asrt_matching_result.matches(
                                    value=asrt.equals(expected_result.value),
                                    trace=asrt_trace_rendering.matches_node_renderer(
                                        asrt_d_tree.equals_node(expected_result.trace.render()),
                                    )
                                )
                            ),
                            prim_asrt__constant(
                                asrt_w_interval.is_with_interval(
                                    case.interval.pos,
                                    case.interval.neg,
                                )
                            ),
                        )
                    )

    def test_failing_validation(self):
        # ARRANGE #
        symbol_not_an_int = StringSymbolContext.of_constant('SYMBOL_NOT_AN_INT', 'notAnInt')
        cases = [
            ValidationCase(comparators.EQ.name + ' not a number',
                           remaining_source(comparators.EQ.name + ' notANumber'),
                           source_assertion=
                           assert_source(is_at_eol=asrt.is_true),
                           ),
            ValidationCase(comparators.EQ.name + ' not an int',
                           remaining_source(comparators.EQ.name + ' 0.5'),
                           source_assertion=
                           assert_source(is_at_eol=asrt.is_true),
                           ),
            ValidationCase(comparators.EQ.name + ' invalid expression syntax',
                           remaining_source(comparators.EQ.name + ' (1'),
                           source_assertion=
                           assert_source(is_at_eol=asrt.is_true),
                           ),
            ValidationCase(comparators.EQ.name + ' with symbol references',
                           remaining_source(
                               '== {}'.format(symbol_reference_syntax_for_name(symbol_not_an_int.name))
                           ),
                           source_assertion=
                           assert_source(is_at_eol=asrt.is_true),
                           references=asrt.matches_singleton_sequence(
                               symbol_not_an_int.reference_assertion__string_made_up_of_just_strings),
                           symbols=symbol_not_an_int.symbol_table
                           ),
        ]
        for case in cases:
            with self.subTest(case.name):
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    case.source,
                    input_=integration_check.ARBITRARY_MODEL,
                    arrangement=arrangement_wo_tcds(
                        symbols=case.symbols,
                    ),
                    expectation=Expectation(
                        ParseExpectation(
                            source=case.source_assertion,
                            symbol_references=case.references,
                        ),
                        ExecutionExpectation(
                            validation=validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
                        ),
                    )
                )


def model_of(rhs: int) -> ModelInfo:
    return ModelInfo(rhs)


def matcher_of(operator: comparators.ComparisonOperator,
               constant_rhs: int) -> MatcherWTrace[int]:
    return comparison_matcher.ComparisonMatcher(_comparison_matcher_config(operator),
                                                constant_rhs,
                                                )


def _comparison_matcher_config(operator: comparators.ComparisonOperator) -> comparison_matcher.Config:
    return comparison_matcher.Config(
        syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
        operator,
        details.String,
    )
