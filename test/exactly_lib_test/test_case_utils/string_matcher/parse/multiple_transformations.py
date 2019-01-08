import unittest

from typing import Iterable, Optional

from exactly_lib.test_case_utils.string_matcher.parse import parse_string_matcher as sut
from exactly_lib.type_system.error_message import ErrorMessageResolver, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherResolverConstantTestImpl, \
    is_reference_to_string_matcher
from exactly_lib_test.symbol.test_resources.string_transformer import StringTransformerResolverConstantTestImpl, \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import test_configuration as tc
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as str_trans_syntax
from exactly_lib_test.test_case_utils.test_resources.matcher_assertions import Expectation
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


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

        initial_model = model_construction.model_of(initial_model_contents)

        equals_expected_matcher = NameAndValue('EQUALS_EXPECTED',
                                               StringMatcherResolverConstantTestImpl(
                                                   EqualsMatcher(model_after_2_transformations)
                                               ))

        prepend_transformer_symbol = NameAndValue('PREPEND_TRANSFORMER',
                                                  StringTransformerResolverConstantTestImpl(
                                                      PrependStringToLinesTransformer(string_to_prepend))
                                                  )

        prepend_trans_arg = str_trans_syntax.syntax_for_transformer_option(prepend_transformer_symbol.name)

        trans_and_eq_expected_matcher_source = remaining_source('{prepend_trans_arg} {equals_expected_matcher}'.format(
            prepend_trans_arg=prepend_trans_arg,
            equals_expected_matcher=equals_expected_matcher.name,
        ))

        # ACT & ASSERT #

        parser = sut.string_matcher_parser()
        prepend_and_equals_expected_matcher_resolver = parser.parse(trans_and_eq_expected_matcher_source)

        prepend_and_equals_expected_matcher = NameAndValue('PREPEND_AND_EQUALS_EXPECTED',
                                                           prepend_and_equals_expected_matcher_resolver)

        symbols = SymbolTable({
            equals_expected_matcher.name: container(equals_expected_matcher.value),
            prepend_transformer_symbol.name: container(prepend_transformer_symbol.value),
            prepend_and_equals_expected_matcher.name: container(prepend_and_equals_expected_matcher.value),
        })
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(prepend_transformer_symbol.name),
            is_reference_to_string_matcher(prepend_and_equals_expected_matcher.name),
        ])

        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{prepend_trans_arg} {maybe_not} {prepend_and_equals_expected_matcher}',
                     prepend_trans_arg=prepend_trans_arg,
                     maybe_not=maybe_not.nothing__if_positive__not_option__if_negative,
                     prepend_and_equals_expected_matcher=prepend_and_equals_expected_matcher.name)),
            initial_model,
            self.configuration.arrangement_for_contents(
                symbols=symbols),
            Expectation(
                main_result=maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_references),
        )


class PrependStringToLinesTransformer(StringTransformer):
    def __init__(self, string_to_prepend: str):
        self.string_to_prepend = string_to_prepend

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(self._prepend, lines)

    def _prepend(self, to: str) -> str:
        return self.string_to_prepend + to


class EqualsMatcher(StringMatcher):
    def __init__(self, expected: str):
        self.expected = expected

    @property
    def option_description(self) -> str:
        return 'equals ' + self.expected

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        actual = self._as_single_string(model)
        if self.expected == actual:
            return None
        else:
            err_msg = 'not eq to "{}": "{}"'.format(self.expected, actual)
            return ConstantErrorMessageResolver(err_msg)

    @staticmethod
    def _as_single_string(model: FileToCheck) -> str:
        with model.lines() as lines:
            return ''.join(list(lines))
