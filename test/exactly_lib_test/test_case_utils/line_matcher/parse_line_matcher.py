import unittest
from typing import List, Sequence, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher as sut
from exactly_lib.test_case_utils.line_matcher.impl import line_number
from exactly_lib.test_case_utils.line_matcher.line_matchers import line_matcher_constant
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import Matcher
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_parser \
    import remaining_source
from exactly_lib_test.symbol.test_resources import sdv_assertions
from exactly_lib_test.symbol.test_resources.line_matcher import is_line_matcher_reference_to
from exactly_lib_test.test_case_utils.line_matcher.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.line_matcher.test_resources.ddv_assertions import ddv_matches_line_matcher
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.matcher.test_resources.int_expr_matcher import \
    ComparisonMatcherForEquivalenceChecks
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_case_utils.test_resources import matcher_parse_check
from exactly_lib_test.test_case_utils.test_resources.matcher_parse_check import Expectation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.matcher_assertions import is_equivalent_to, ModelInfo


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestLineNumberParser),
        unittest.makeSuite(TestParseLineMatcher),
    ])


class Configuration(matcher_parse_check.Configuration[LineMatcherLine]):
    def parse(self, parser: TokenParser) -> SymbolDependentValue:
        return sut.parse_line_matcher_from_token_parser(parser)

    def is_reference_to(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_line_matcher_reference_to(symbol_name)

    def sdv_of_constant_matcher(self, matcher: LineMatcher) -> SymbolDependentValue:
        return LineMatcherSdv(
            matchers.sdv_from_primitive_value(matcher)
        )

    def constant_matcher(self, result: bool) -> LineMatcher:
        return line_matcher_constant(result)

    def arbitrary_model_that_should_not_be_touched(self) -> LineMatcherLine:
        return 1, 'arbitrary line'


class TestLineNumberParser(unittest.TestCase):
    def _check(self,
               source: TokenParser,
               expectation: Expectation):
        # ACT #
        actual_sdv = line_number.parse_line_number(source)
        # ASSERT #
        expectation.sdv.apply_with_message(self, actual_sdv,
                                           'SDV')
        expectation.token_stream.apply_with_message(self,
                                                    source.token_stream,
                                                    'token stream')

    def test_failing_parse(self):
        cases = [
            (
                'no arguments',
                remaining_source(''),
            ),
            (
                'no arguments, but it appears on the following line',
                remaining_source('  ',
                                 ['= 69']),
            ),
            (
                'invalid OPERATOR',
                remaining_source('~ 69'),
            ),
            (
                'invalid INTEGER EXPRESSION',
                remaining_source('~ notAnInteger'),
            ),
        ]
        for name, source in cases:
            with self.subTest(case_name=name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    line_number.parse_line_number(source)

    def test_successful_parse(self):
        # ARRANGE #
        def model_of(rhs: int) -> ModelInfo:
            return ModelInfo((rhs, 'irrelevant line contents'))

        expected_integer_matcher = _ExpectedEquivalentLineNumMatcher(comparators.LT,
                                                                     69)
        expected_sdv = resolved_value_is_line_number_matcher(expected_integer_matcher,
                                                             [
                                                                 model_of(60),
                                                                 model_of(69),
                                                                 model_of(72),

                                                             ])

        text_on_following_line = 'text on following line'

        cases = [
            SourceCase(
                'simple comparison',

                source=
                remaining_source('< 69',
                                 following_lines=[text_on_following_line]),

                source_assertion=
                assert_token_stream(
                    remaining_source=asrt.equals('\n' + text_on_following_line)),
            ),
            SourceCase(
                'following tokens on same line',

                source=
                remaining_source('< 69 next',
                                 following_lines=[text_on_following_line]),

                source_assertion=
                assert_token_stream(
                    remaining_source=asrt.equals('next' + '\n' + text_on_following_line)),
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                self._check(case.source,
                            Expectation(expected_sdv,
                                        case.source_assertion))


class TestParseLineMatcher(matcher_parse_check.TestParseStandardExpressionsBase):
    _conf = Configuration()

    @property
    def conf(self) -> Configuration:
        return self._conf

    def test_line_number(self):
        # ARRANGE #
        def model_of(rhs: int) -> ModelInfo:
            return ModelInfo((rhs, 'irrelevant line contents'))

        comparator = comparators.LT
        rhs = 72
        expected_integer_matcher = _ExpectedEquivalentLineNumMatcher(comparator,
                                                                     rhs)

        expected_sdv = resolved_value_is_line_number_matcher(expected_integer_matcher,
                                                             [
                                                                 model_of(69),
                                                                 model_of(72),
                                                                 model_of(80),

                                                             ])

        # ACT & ASSERT #
        self._check(
            remaining_source(argument_syntax.syntax_for_line_number_matcher(comparator,
                                                                            str(rhs))),
            Expectation(
                sdv=expected_sdv),
        )


def resolved_value_is_line_number_matcher(equivalent: Matcher[LineMatcherLine],
                                          model_infos: List[ModelInfo],
                                          references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence
                                          ) -> ValueAssertion[SymbolDependentValue]:
    expected_matcher = is_equivalent_to(equivalent,
                                        model_infos)
    return sdv_assertions.matches_sdv_of_line_matcher(
        references,
        ddv_matches_line_matcher(expected_matcher)
    )


class _ExpectedEquivalentLineNumMatcher(Matcher[LineMatcherLine]):
    NAME = ' '.join((line_matcher.LINE_NUMBER_MATCHER_NAME,
                     syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name))

    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs: int):
        self._matcher = ComparisonMatcherForEquivalenceChecks(self.NAME, operator, rhs)

    @property
    def name(self) -> str:
        return self.NAME

    def matches(self, model: LineMatcherLine) -> bool:
        return self._matcher.matches(model[0])

    def matches_emr(self, model: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        return self._matcher.matches_emr(model[0])

    @property
    def option_description(self) -> str:
        raise NotImplementedError('unsupported')
