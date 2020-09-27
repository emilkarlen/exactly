import unittest
from typing import Sequence, List

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher as sut
from exactly_lib.test_case_utils.matcher.impls.comparison_matcher import ComparisonMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.util.description_tree import details
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.logic.test_resources.resolving_helper import resolving_helper
from exactly_lib_test.symbol.test_resources.string import StringSymbolContext
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.matcher_assertions import is_equivalent_to, ModelInfo
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseIntegerMatcher)


class EquivalenceCheck:
    def __init__(self,
                 equivalent: MatcherWTrace[int],
                 models: List[ModelInfo[int]],
                 ):
        self.equivalent = equivalent
        self.models = models

    def assertion(self) -> ValueAssertion[MatcherWTrace[int]]:
        return is_equivalent_to(self.equivalent, self.models)


class Case:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 source_assertion: ValueAssertion[ParseSource],
                 result: EquivalenceCheck,
                 references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                 symbols: SymbolTable = empty_symbol_table(),
                 ):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
        self.result = result
        self.references = references
        self.symbols = symbols


class ValidationCase:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 source_assertion: ValueAssertion[ParseSource],
                 references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                 symbols: SymbolTable = empty_symbol_table(),
                 ):
        self.name = name
        self.source = source
        self.references = references
        self.symbols = symbols


class TestParseIntegerMatcher(unittest.TestCase):
    def test_failing_parse(self):
        parser = sut.IntegerMatcherParser(None)
        cases = [
            NameAndValue(
                'no arguments',
                remaining_source(''),
            ),
            NameAndValue(
                'invalid OPERATOR',
                remaining_source('- 72'),
            ),
            NameAndValue(
                'quoted OPERATOR',
                remaining_source('"{op}" 69'.format(op=comparators.EQ.name)),
            ),
            NameAndValue(
                'missing INTEGER',
                remaining_source(comparators.EQ.name),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    with from_parse_source(case.value) as token_parser:
                        parser.parse(token_parser)

    def test_successful_parse(self):
        # ARRANGE #
        parser = sut.IntegerMatcherParser(None)
        tcds = fake_tcds()
        symbol_69 = StringSymbolContext.of_constant('SYMBOL_69', '69')
        cases = [
            Case(comparators.EQ.name + ' plain integer',
                 remaining_source(comparators.EQ.name + ' 1'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])
                 ),
            Case(comparators.EQ.name + ' plain integer, expr on new line',
                 remaining_source('\n' + comparators.EQ.name + ' 1'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])
                 ),
            Case(comparators.EQ.name + ' plain integer, integer on new line',
                 remaining_source(comparators.EQ.name + '\n' + ' 1'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])
                 ),
            Case(comparators.NE.name,
                 remaining_source(comparators.NE.name + ' 1'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.NE, 1),
                                         [
                                             model_of(-1),
                                             model_of(1),
                                             model_of(2),
                                         ])),
            Case(comparators.LT.name,
                 remaining_source(comparators.LT.name + ' 69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.LT, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.LTE.name,
                 remaining_source(comparators.LTE.name + '  69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.LTE, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.GT.name,
                 remaining_source(comparators.GT.name + ' 69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.GT, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.GTE.name,
                 remaining_source(comparators.GTE.name + ' 69'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.GTE, 69),
                                         [
                                             model_of(60),
                                             model_of(69),
                                             model_of(72),
                                         ])),
            Case(comparators.GTE.name + ' following content on line',
                 remaining_source(comparators.GTE.name + ' 72 next'),
                 source_assertion=
                 assert_source(remaining_part_of_current_line=asrt.equals('next')),
                 result=EquivalenceCheck(matcher_of(comparators.GTE, 72),
                                         [
                                             model_of(69),
                                             model_of(72),
                                             model_of(80),
                                         ])),
            Case(comparators.EQ.name + ' integer expression',
                 remaining_source('== "69+72"'),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
                 result=EquivalenceCheck(matcher_of(comparators.EQ, 69 + 72),
                                         [
                                             model_of(69 + 72 - 1),
                                             model_of(69 + 72),
                                             model_of(69 + 72 + 1),
                                         ])),
            Case(comparators.EQ.name + ' with symbol references',
                 remaining_source('== "{}+72"'.format(symbol_reference_syntax_for_name(symbol_69.name))),
                 source_assertion=
                 assert_source(is_at_eol=asrt.is_true),
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
            with self.subTest(name=case.name):
                with from_parse_source(case.source) as token_parser:
                    # ACT #
                    actual_sdv = parser.parse(token_parser)
                    # ASSERT #
                    case.references.apply_with_message(self, actual_sdv.references, 'references')

                    actual_ddv = actual_sdv.resolve(case.symbols)

                    validator = actual_ddv.validator

                    mb_validation_failure = validator.validate_pre_sds_if_applicable(tcds.hds)
                    self.assertIsNone(mb_validation_failure, 'pre sds validation')

                    mb_validation_failure = validator.validate_post_sds_if_applicable(tcds)
                    self.assertIsNone(mb_validation_failure, 'post sds validation')

                    actual = resolving_helper(case.symbols).resolve_matcher(actual_sdv)

                case.source_assertion.apply_with_message(self, case.source, 'source')
                case.result.assertion().apply_with_message(self, actual, 'parsed value')

    def test_failing_validation(self):
        # ARRANGE #
        parser = sut.IntegerMatcherParser(None)
        tcds = fake_tcds()
        is_text_renderer = asrt_renderer.is_renderer_of_major_blocks()
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
            with self.subTest(name=case.name):
                with from_parse_source(case.source) as token_parser:
                    # ACT #
                    actual_sdv = parser.parse(token_parser)
                    actual_ddv = actual_sdv.resolve(case.symbols)
                    # ASSERT #
                    case.references.apply_with_message(self, actual_sdv.references, 'references')

                    mb_validation_failure = actual_ddv.validator.validate_pre_sds_if_applicable(tcds.hds)

                    self.assertIsNotNone(mb_validation_failure, 'pre sds validation')

                    is_text_renderer.apply_with_message(self, mb_validation_failure, 'error message')


def model_of(rhs: int) -> ModelInfo:
    return ModelInfo(rhs)


def matcher_of(operator: comparators.ComparisonOperator,
               constant_rhs: int) -> MatcherWTrace[int]:
    return ComparisonMatcher(operator,
                             constant_rhs,
                             details.String,
                             )
