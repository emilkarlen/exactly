import unittest
from typing import Iterable

from exactly_lib.test_case_utils.string_matcher import matcher_options, parse_string_matcher as sut
from exactly_lib.test_case_utils.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.string_matcher import StringMatcherModel
from exactly_lib.util.description_tree import details
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.string_matcher import is_reference_to_string_matcher, \
    StringMatcherSymbolContext
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer, \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Expectation, ParseExpectation, \
    ExecutionExpectation
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check, test_configuration
from exactly_lib_test.test_case_utils.string_matcher.test_resources import test_configuration as tc
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as str_trans_syntax
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import StringTransformerTestImplBase


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        ActualFileIsEmpty(),
    ])


class ActualFileIsEmpty(tc.TestWithNegationArgumentBase):
    def _doTest(self, maybe_not: ExpectationTypeConfigForNoneIsSuccess):
        # ARRANGE #
        string_to_prepend = '.'

        initial_model_contents = '\n'

        model_after_2_transformations = ''.join([string_to_prepend,
                                                 string_to_prepend,
                                                 initial_model_contents])

        initial_model = integration_check.model_of(initial_model_contents)

        equals_expected_matcher = StringMatcherSymbolContext.of_primitive(
            'EQUALS_EXPECTED',
            EqualsMatcherTestImpl(model_after_2_transformations)
        )

        prepend_transformer_symbol = StringTransformerSymbolContext.of_primitive(
            'PREPEND_TRANSFORMER',
            PrependStringToLinesTransformer(string_to_prepend)
        )

        prepend_trans_arg = str_trans_syntax.syntax_for_transformer_option(prepend_transformer_symbol.name)

        trans_and_eq_expected_matcher_source = remaining_source('{prepend_trans_arg} {equals_expected_matcher}'.format(
            prepend_trans_arg=prepend_trans_arg,
            equals_expected_matcher=equals_expected_matcher.name,
        ))

        # ACT & ASSERT #

        parser = sut.string_matcher_parser()
        prepend_and_equals_expected_matcher_sdv = parser.parse(trans_and_eq_expected_matcher_source)

        prepend_and_equals_expected_matcher = StringMatcherSymbolContext.of_sdv(
            'PREPEND_AND_EQUALS_EXPECTED',
            prepend_and_equals_expected_matcher_sdv
        )

        symbols = SymbolContext.symbol_table_of_contexts([
            equals_expected_matcher,
            prepend_transformer_symbol,
            prepend_and_equals_expected_matcher,
        ])
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(prepend_transformer_symbol.name),
            is_reference_to_string_matcher(prepend_and_equals_expected_matcher.name),
        ])

        self._check_with_source_variants(
            test_configuration.arguments_for(
                args('{prepend_trans_arg} {maybe_not} {prepend_and_equals_expected_matcher}',
                     prepend_trans_arg=prepend_trans_arg,
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative,
                     prepend_and_equals_expected_matcher=prepend_and_equals_expected_matcher.name)),
            initial_model,
            arrangement_w_tcds(
                symbols=symbols),
            Expectation(
                ParseExpectation(
                    symbol_references=expected_symbol_references,
                ),
                ExecutionExpectation(
                    main_result=maybe_not.pass__if_positive__fail__if_negative,
                ),
            )
        )


class PrependStringToLinesTransformer(StringTransformerTestImplBase):
    def __init__(self, string_to_prepend: str):
        self.string_to_prepend = string_to_prepend

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(self._prepend, lines)

    def _prepend(self, to: str) -> str:
        return self.string_to_prepend + to


class EqualsMatcherTestImpl(StringMatcherImplBase):
    def __init__(self, expected: str):
        super().__init__()
        self.expected = expected

    @property
    def name(self) -> str:
        return matcher_options.EQUALS_ARGUMENT

    def matches_w_trace(self, model: StringMatcherModel) -> MatchingResult:
        actual = self._as_single_string(model)
        if self.expected == actual:
            return self._new_tb().build_result(True)
        else:
            err_msg = 'not eq to "{}": "{}"'.format(self.expected, actual)
            return (
                self._new_tb()
                    .append_details(details.String(err_msg))
                    .build_result(False)
            )

    @staticmethod
    def _as_single_string(model: StringMatcherModel) -> str:
        with model.lines() as lines:
            return ''.join(list(lines))
