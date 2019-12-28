import unittest
from typing import Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import ConstantDdvValidator
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher as sut
from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.line_matcher import is_line_matcher_reference_to, \
    successful_matcher_with_validation, sdv_of_unconditionally_matching_matcher
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer__ref
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_name_and_containers
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.line_matcher.test_resources.arguments_building import NOT_A_LINE_MATCHER
from exactly_lib_test.test_case_utils.string_matcher.parse.line_matches import test_resources as tr
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building, test_configuration
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import \
    CommonArgumentsConstructor
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.test_configuration import \
    TestCaseBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _ParseWithMissingLineMatcherArgument(),
        _ParseWithInvalidLineMatcher(),

        _TestLineMatcherValidatorIsApplied(),
        _TestStringTransformerValidatorIsApplied(),

        _TestSymbolReferenceForStringTransformerIsReported(),
        _TestSymbolReferenceForLineMatcherIsReported(),
    ])


class _TestCaseBase(unittest.TestCase):
    def _check_variants_with_expectation_type_and_any_or_every(
            self,
            args_variant_constructor: tr.InstructionArgumentsConstructorForExpTypeAndQuantifier):
        for expectation_type in ExpectationType:
            for quantifier in Quantifier:
                with self.subTest(expectation_type=expectation_type,
                                  any_or_every_keyword=quantifier):
                    args_variant = args_variant_constructor.construct(expectation_type,
                                                                      quantifier)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.string_matcher_parser().parse(test_configuration.source_for(args_variant))


class _ParseWithMissingLineMatcherArgument(_TestCaseBase):
    def runTest(self):
        self._check_variants_with_expectation_type_and_any_or_every(
            tr.args_constructor_for(line_matcher=''))


class _ParseWithInvalidLineMatcher(_TestCaseBase):
    def runTest(self):
        self._check_variants_with_expectation_type_and_any_or_every(
            tr.args_constructor_for(line_matcher=NOT_A_LINE_MATCHER))


class _TestLineMatcherValidatorIsApplied(TestCaseBase):
    def runTest(self):
        failure_message = 'failure'
        failing_validation_result = asrt_validation.new_single_string_text_for_test(failure_message)
        assert_failing_validation = asrt_validation.post_sds_validation_fails(asrt.equals(failure_message))
        line_matcher_symbol_name = 'line_matcher_with_failing_validation'

        asserted_symbol_references = asrt.matches_sequence([
            is_line_matcher_reference_to(line_matcher_symbol_name)
        ])

        validation_cases = [
            NEA('failure pre sds',
                expected=
                integration_check.Expectation(
                    validation=asrt_validation.pre_sds_validation_fails(asrt.equals(failure_message)),
                    symbol_references=asserted_symbol_references
                ),
                actual=ConstantDdvValidator(
                    pre_sds_result=failing_validation_result
                )
                ),
            NEA('failure post sds',
                expected=
                integration_check.Expectation(
                    validation=asrt_validation.post_sds_validation_fails__w_any_msg(),
                    symbol_references=asserted_symbol_references
                ),
                actual=ConstantDdvValidator(
                    post_sds_result=failing_validation_result
                )
                ),
        ]
        for case in validation_cases:

            symbols = SymbolTable({
                line_matcher_symbol_name: symbol_utils.container(
                    successful_matcher_with_validation(case.actual)
                )
            })
            for quantifier in Quantifier:

                arguments_constructor = arguments_building.ImplicitActualFileArgumentsConstructor(
                    CommonArgumentsConstructor(),
                    arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier,
                                                                                line_matcher_symbol_name)
                )
                for expectation_type in ExpectationType:
                    arguments = arguments_constructor.apply(expectation_type)
                    source = test_configuration.arguments_for(arguments).as_remaining_source
                    with self.subTest(case=case.name,
                                      expectation_type=expectation_type,
                                      quantifier=quantifier):
                        self._check(
                            source=source,
                            model=integration_check.ARBITRARY_MODEL,
                            arrangement=integration_check.Arrangement(
                                symbols=symbols
                            ),
                            expectation=case.expected
                        )


class _TestStringTransformerValidatorIsApplied(TestCaseBase):
    def runTest(self):
        line_matcher_symbol = NameAndValue(
            'valid_line_matcher',
            symbol_utils.container(
                sdv_of_unconditionally_matching_matcher()
            )
        )

        for case in failing_validation_cases():
            symbol_context = case.value.symbol_context

            symbols = symbol_table_from_name_and_containers([
                line_matcher_symbol,
                symbol_context.name_and_container,
            ])

            expected_symbol_references = asrt.matches_sequence([
                symbol_context.reference_assertion,
                is_line_matcher_reference_to(line_matcher_symbol.name)
            ])

            for quantifier in Quantifier:

                arguments_constructor = arguments_building.ImplicitActualFileArgumentsConstructor(
                    CommonArgumentsConstructor(symbol_context.name),
                    arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier,
                                                                                line_matcher_symbol.name)
                )
                for expectation_type in ExpectationType:
                    arguments = arguments_constructor.apply(expectation_type)
                    source = test_configuration.arguments_for(arguments).as_remaining_source
                    with self.subTest(case=case.name,
                                      expectation_type=expectation_type,
                                      quantifier=quantifier):
                        self._check(
                            source=source,
                            model=integration_check.ARBITRARY_MODEL,
                            arrangement=integration_check.Arrangement(
                                symbols=symbols
                            ),
                            expectation=integration_check.Expectation(
                                validation=case.value.expectation,
                                symbol_references=expected_symbol_references,
                            )
                        )


class _TestSymbolReferencesBase(_TestCaseBase):
    def _check_expectation_variants(self,
                                    common_arguments: CommonArgumentsConstructor,
                                    line_matcher: str,
                                    expected_symbols: ValueAssertion[Sequence[SymbolReference]]):
        parser = sut.string_matcher_parser()

        for expectation_type in ExpectationType:
            for quantifier in Quantifier:
                with self.subTest(expectation_type=expectation_type,
                                  quantifier=quantifier.name):
                    arguments_for_implicit_file = arguments_building.ImplicitActualFileArgumentsConstructor(
                        common_arguments,
                        arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier,
                                                                                    line_matcher)
                    ).apply(expectation_type)
                    source = test_configuration.arguments_for(arguments_for_implicit_file).as_remaining_source
                    sdv = parser.parse(source)
                    assert isinstance(sdv, StringMatcherSdv)  # Sanity check
                    expected_symbols.apply_without_message(self, sdv.references)


class _TestSymbolReferenceForStringTransformerIsReported(_TestSymbolReferencesBase):
    def runTest(self):
        # ARRANGE #
        lines_transformer_name = 'the_transformer'

        common_arguments = arguments_building.CommonArgumentsConstructor(lines_transformer_name)
        expected_symbol_reference_to_transformer = is_reference_to_string_transformer__ref(lines_transformer_name)

        expected_symbol_references = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        line_matcher = syntax_for_regex_matcher('regex')

        # ACT & ASSERT #

        self._check_expectation_variants(common_arguments, line_matcher, expected_symbol_references)


class _TestSymbolReferenceForLineMatcherIsReported(_TestSymbolReferencesBase):
    def runTest(self):
        # ARRANGE #
        line_matcher = 'the_line_matcher'

        common_arguments = arguments_building.CommonArgumentsConstructor()
        expected_symbol_reference_to_transformer = is_line_matcher_reference_to(line_matcher)

        expected_symbol_references = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        # ACT & ASSERT #

        self._check_expectation_variants(common_arguments, line_matcher, expected_symbol_references)
