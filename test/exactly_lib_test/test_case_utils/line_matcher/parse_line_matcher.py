import unittest
from typing import List, Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.test_case_utils.line_matcher.impl import line_number
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MODEL, MatchingResult
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_parser \
    import remaining_source
from exactly_lib_test.test_case_utils.matcher.test_resources import assertions as asrt_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.source_case import SourceCase
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.matcher_assertions import is_equivalent_to, ModelInfo


class Expectation:
    def __init__(self,
                 sdv: ValueAssertion[LogicSdv],
                 token_stream: ValueAssertion[TokenParser] = asrt.anything_goes()):
        self.sdv = sdv
        self.token_stream = token_stream


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestLineNumberParser),
    ])


class TestLineNumberParser(unittest.TestCase):
    def _check(self,
               source: TokenParser,
               expectation: Expectation):
        # ACT #
        actual_sdv = line_number.parse_line_number__generic(source)
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
                    line_number.parse_line_number__generic(source)

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


def resolved_value_is_line_number_matcher(equivalent: MatcherWTrace[LineMatcherLine],
                                          model_infos: List[ModelInfo],
                                          references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence
                                          ) -> ValueAssertion[LogicSdv]:
    expected_matcher = is_equivalent_to(equivalent,
                                        model_infos)
    return asrt_matcher.matches_matcher_sdv(
        references=references,
        primitive_value=expected_matcher
    )


class _ExpectedEquivalentLineNumMatcher(MatcherWTrace[LineMatcherLine]):
    NAME = ' '.join((line_matcher.LINE_NUMBER_MATCHER_NAME,
                     syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))

    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 rhs: int):
        self._matcher = _ComparisonMatcherForEquivalenceChecks(operator, rhs)

    @property
    def name(self) -> str:
        return self.NAME

    def structure(self) -> StructureRenderer:
        return renderers.Constant(
            tree.Node(self.NAME,
                      None,
                      (),
                      ())
        )

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        value = self._matches(model)
        return MatchingResult(
            value,
            renderers.Constant(tree.Node(self.NAME, value, (), ())),
        )

    def _matches(self, model: LineMatcherLine) -> bool:
        return self._matcher.matches(model[0])


class _ComparisonMatcherForEquivalenceChecks:
    def __init__(self,
                 operator: comparators.ComparisonOperator,
                 constant_rhs: int,
                 ):
        self._constant_rhs = constant_rhs
        self._operator = operator

    def matches(self, model: int) -> bool:
        return self._operator.operator_fun(model, self._constant_rhs)
