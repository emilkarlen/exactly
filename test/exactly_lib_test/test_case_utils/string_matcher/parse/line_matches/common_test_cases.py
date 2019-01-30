import unittest

from typing import Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import ConstantPreOrPostSdsValueValidator, \
    PreOrPostSdsValueValidator
from exactly_lib.test_case_utils.line_matcher.line_matcher_values import LineMatcherValueFromPrimitiveValue
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.line_matcher import is_line_matcher_reference_to, \
    LineMatcherResolverConstantValueTestImpl
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.line_matcher.test_resources.arguments_building import NOT_A_LINE_MATCHER
from exactly_lib_test.test_case_utils.string_matcher.parse.line_matches import test_resources as tr
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import \
    CommonArgumentsConstructor
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.test_configuration import \
    TestConfigurationForMatcher, TestCaseBase
from exactly_lib_test.test_case_utils.string_matcher.test_resources import model_construction
from exactly_lib_test.test_case_utils.test_resources import matcher_assertions
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _ParseWithMissingLineMatcherArgument(),
        _ParseWithInvalidLineMatcher(),

        _TestLineMatcherValidatorIsApplied(),

        _TestSymbolReferenceForStringTransformerIsReported(),
        _TestSymbolReferenceForLineMatcherIsReported(),
    ])


class _TestCaseBase(unittest.TestCase):
    def __init__(self):
        super().__init__()
        self.configuration = TestConfigurationForMatcher()

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
                        self.configuration.new_parser().parse(self.configuration.source_for(args_variant))


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
        assert_failing_validation = asrt_validation.matches_validation_failure(asrt.equals(failure_message))
        line_matcher_symbol_name = 'line_matcher_with_failing_validation'

        asserted_symbol_references = asrt.matches_sequence([
            is_line_matcher_reference_to(line_matcher_symbol_name)
        ])

        validation_cases = [
            NEA('failure pre sds',
                expected=
                matcher_assertions.Expectation(
                    validation_pre_sds=assert_failing_validation,
                    symbol_usages=asserted_symbol_references
                ),
                actual=ConstantPreOrPostSdsValueValidator(pre_sds_result=failure_message)
                ),
            NEA('failure post sds',
                expected=
                matcher_assertions.Expectation(
                    validation_post_sds=assert_failing_validation,
                    symbol_usages=asserted_symbol_references
                ),
                actual=ConstantPreOrPostSdsValueValidator(post_sds_result=failure_message)
                ),
        ]
        for case in validation_cases:

            symbols = SymbolTable({
                line_matcher_symbol_name: symbol_utils.container(
                    _successful_matcher_with_validation(case.actual)
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
                    source = self.configuration.arguments_for(arguments).as_remaining_source
                    with self.subTest(case=case.name,
                                      expectation_type=expectation_type,
                                      quantifier=quantifier):
                        self._check(
                            source=source,
                            model=model_construction.arbitrary_model(),
                            arrangement=ArrangementPostAct(
                                symbols=symbols
                            ),
                            expectation=case.expected
                        )


class _TestSymbolReferencesBase(_TestCaseBase):
    def _check_expectation_variants(self,
                                    common_arguments: CommonArgumentsConstructor,
                                    line_matcher: str,
                                    expected_symbols: ValueAssertion[Sequence[SymbolReference]]):
        parser = self.configuration.new_parser()

        for expectation_type in ExpectationType:
            for quantifier in Quantifier:
                with self.subTest(expectation_type=expectation_type,
                                  quantifier=quantifier.name):
                    arguments_for_implicit_file = arguments_building.ImplicitActualFileArgumentsConstructor(
                        common_arguments,
                        arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier,
                                                                                    line_matcher)
                    ).apply(expectation_type)
                    source = self.configuration.arguments_for(arguments_for_implicit_file).as_remaining_source
                    resolver = parser.parse(source)
                    assert isinstance(resolver, StringMatcherResolver)  # Sanity check
                    expected_symbols.apply_without_message(self, resolver.references)


class _TestSymbolReferenceForStringTransformerIsReported(_TestSymbolReferencesBase):
    def runTest(self):
        # ARRANGE #
        lines_transformer_name = 'the_transformer'

        common_arguments = arguments_building.CommonArgumentsConstructor(lines_transformer_name)
        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(lines_transformer_name)

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


def _successful_matcher_with_validation(validator: PreOrPostSdsValueValidator):
    return LineMatcherResolverConstantValueTestImpl(
        LineMatcherValueFromPrimitiveValue(
            LineMatcherConstant(True),
            validator
        )
    )
