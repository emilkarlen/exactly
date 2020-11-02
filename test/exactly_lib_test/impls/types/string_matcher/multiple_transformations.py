import unittest

from exactly_lib.impls.types.string_matcher import matcher_options, parse_string_matcher as sut
from exactly_lib.impls.types.string_matcher.impl.base_class import StringMatcherImplBase
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.description_tree import details
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation
from exactly_lib_test.impls.types.string_matcher.test_resources import test_configuration
from exactly_lib_test.impls.types.string_matcher.test_resources import test_configuration as tc
from exactly_lib_test.impls.types.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.impls.types.string_models.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_syntax as str_trans_syntax
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    ExpectationTypeConfigForNoneIsSuccess
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import is_reference_to_string_matcher, \
    StringMatcherSymbolContext
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


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

        initial_model = model_constructor.of_str(self, initial_model_contents)

        equals_expected_matcher = StringMatcherSymbolContext.of_primitive(
            'EQUALS_EXPECTED',
            EqualsMatcherTestImpl(model_after_2_transformations)
        )

        prepend_transformer_symbol = StringTransformerSymbolContext.of_primitive(
            'PREPEND_TRANSFORMER',
            string_transformers.of_line_transformer__w_preserved_line_ending(
                'prepend to each line',
                lambda line: (line + string_to_prepend)
            )
        )

        prepend_trans_arg = str_trans_syntax.syntax_for_transformer_option(prepend_transformer_symbol.name)

        trans_and_eq_expected_matcher_source = remaining_source('{prepend_trans_arg} {equals_expected_matcher}'.format(
            prepend_trans_arg=prepend_trans_arg,
            equals_expected_matcher=equals_expected_matcher.name,
        ))

        # ACT & ASSERT #

        parser = sut.parsers().full
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


class EqualsMatcherTestImpl(StringMatcherImplBase):
    def __init__(self, expected: str):
        super().__init__()
        self.expected = expected

    @property
    def name(self) -> str:
        return matcher_options.EQUALS_ARGUMENT

    def matches_w_trace(self, model: StringModel) -> MatchingResult:
        actual = model.as_str
        if self.expected == actual:
            return self._new_tb().build_result(True)
        else:
            err_msg = 'not eq to "{}": "{}"'.format(self.expected, actual)
            return (
                self._new_tb()
                    .append_details(details.String(err_msg))
                    .build_result(False)
            )
