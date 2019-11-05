import unittest
from typing import Sequence, List

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.matcher.impls import parse_integer_matcher as sut
from exactly_lib.test_case_utils.matcher.impls.comparison_matcher import ComparisonMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, Matcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable, singleton_symbol_table_2
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.matcher_assertions import is_equivalent_to, ModelInfo
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseIntegerMatcher)


class EquivalenceCheck:
    def __init__(self,
                 equivalent: MatcherWTraceAndNegation[int],
                 models: List[ModelInfo[int]],
                 ):
        self.equivalent = equivalent
        self.models = models

    def assertion(self, expectation_type: ExpectationType) -> ValueAssertion[Matcher[int]]:
        return (
            is_equivalent_to(self.equivalent, self.models)
            if expectation_type is ExpectationType.POSITIVE
            else
            is_equivalent_to(self.equivalent.negation, self.models)
        )


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
        cases = [
            (
                'no arguments',
                remaining_source(''),
            ),
            (
                'no arguments, but it appears on the following line',
                remaining_source('',
                                 [comparators.EQ.name + ' 1']),
            ),
            (
                'invalid OPERATOR',
                remaining_source('- 72'),
            ),
            (
                'quoted OPERATOR',
                remaining_source('"{op}" 69'.format(op=comparators.EQ.name)),
            ),
            (
                'missing INTEGER',
                remaining_source(comparators.EQ.name),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    with from_parse_source(source) as parser:
                        sut.parse(parser, ExpectationType.POSITIVE, None)

    def test_successful_parse(self):
        # ARRANGE #
        tcds = fake_tcds()
        symbol_69 = NameAndValue('SYMBOL_69',
                                 symbol_utils.container(string_resolvers.str_constant('69')),
                                 )
        for expectation_type in ExpectationType:
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
                                             ])),
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
                         asrt_sym_ref.is_reference_to_string_made_up_of_just_plain_strings(symbol_69.name)
                     ),
                     symbols=singleton_symbol_table_2(symbol_69.name,
                                                      symbol_69.value)
                     ),
            ]
            for case in cases:
                with self.subTest(name=case.name,
                                  expectation_type=expectation_type):
                    with from_parse_source(case.source) as parser:
                        # ACT #
                        actual_resolver = sut.parse(parser, expectation_type, None)
                        # ASSERT #
                        case.references.apply_with_message(self, actual_resolver.references, 'references')

                        actual_ddv = actual_resolver.resolve(case.symbols)

                        validator = actual_ddv.validator

                        mb_validation_failure = validator.validate_pre_sds_if_applicable(tcds.hds)
                        self.assertIsNone(mb_validation_failure, 'pre sds validation')

                        mb_validation_failure = validator.validate_post_sds_if_applicable(tcds)
                        self.assertIsNone(mb_validation_failure, 'post sds validation')

                        actual = actual_resolver.resolve(case.symbols).value_of_any_dependency(tcds)

                    case.source_assertion.apply_with_message(self, case.source, 'source')
                    case.result.assertion(expectation_type).apply_with_message(self, actual, 'parsed value')

    def test_failing_validation(self):
        # ARRANGE #
        tcds = fake_tcds()
        is_text_renderer = asrt_renderer.is_renderer_of_major_blocks()
        symbol_not_an_int = NameAndValue('SYMBOL_NOT_AN_INT',
                                         symbol_utils.container(string_resolvers.str_constant('notAnInt')),
                                         )
        for expectation_type in ExpectationType:
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
                                   asrt_sym_ref.is_reference_to_string_made_up_of_just_plain_strings(
                                       symbol_not_an_int.name)
                               ),
                               symbols=singleton_symbol_table_2(symbol_not_an_int.name,
                                                                symbol_not_an_int.value)
                               ),
            ]
            for case in cases:
                with self.subTest(name=case.name,
                                  expectation_type=expectation_type):
                    with from_parse_source(case.source) as parser:
                        # ACT #
                        actual_resolver = sut.parse(parser, expectation_type, None)
                        actual_ddv = actual_resolver.resolve(case.symbols)
                        # ASSERT #
                        case.references.apply_with_message(self, actual_resolver.references, 'references')

                        mb_validation_failure = actual_ddv.validator.validate_pre_sds_if_applicable(tcds.hds)

                        self.assertIsNotNone(mb_validation_failure, 'pre sds validation')

                        is_text_renderer.apply_with_message(self, mb_validation_failure, 'error message')


def model_of(rhs: int) -> ModelInfo:
    return ModelInfo(rhs)


def matcher_of(operator: comparators.ComparisonOperator,
               constant_rhs: int,
               expectation_type: ExpectationType = ExpectationType.POSITIVE) -> MatcherWTraceAndNegation[int]:
    return ComparisonMatcher(expectation_type,
                             operator,
                             constant_rhs,
                             str,
                             )
