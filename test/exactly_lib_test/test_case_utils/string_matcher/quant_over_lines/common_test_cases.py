import unittest
from typing import Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import ConstantDdvValidator
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher as sut
from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.line_matcher import is_reference_to_line_matcher__usage, \
    successful_matcher_with_validation, LineMatcherSymbolContext, is_reference_to_line_matcher, \
    LineMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as lm_args
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.line_matcher.test_resources.arguments_building import NOT_A_LINE_MATCHER
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    ExecutionExpectation, Expectation, arrangement_w_tcds
from exactly_lib_test.test_case_utils.string_matcher.quant_over_lines import test_resources as tr
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as args2
from exactly_lib_test.test_case_utils.string_matcher.test_resources import integration_check, arguments_building, \
    test_configuration
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import \
    CommonArgumentsConstructor
from exactly_lib_test.test_case_utils.string_matcher.test_resources.test_configuration import \
    TestCaseBase
from exactly_lib_test.test_case_utils.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.test_case_utils.test_resources import validation as asrt_validation
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        _ParseWithMissingLineMatcherArgument(),
        _ParseWithInvalidLineMatcher(),
        _TestFilesMatcherShouldBeParsedAsSimpleExpression(),

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
                        sut.parsers().full.parse(test_configuration.source_for(args_variant))


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
        line_matcher_symbol_name = 'line_matcher_with_failing_validation'

        asserted_symbol_references = asrt.matches_sequence([
            is_reference_to_line_matcher(line_matcher_symbol_name)
        ])

        validation_cases = [
            NEA('failure pre sds',
                expected=
                Expectation(
                    ParseExpectation(
                        symbol_references=asserted_symbol_references,
                    ),
                    ExecutionExpectation(
                        validation=asrt_validation.pre_sds_validation_fails(asrt.equals(failure_message)),
                    ),
                ),
                actual=ConstantDdvValidator(
                    pre_sds_result=failing_validation_result
                )
                ),
            NEA('failure post sds',
                expected=
                Expectation(
                    ParseExpectation(
                        symbol_references=asserted_symbol_references,
                    ),
                    ExecutionExpectation(
                        validation=asrt_validation.post_sds_validation_fails__w_any_msg(),
                    ),
                ),
                actual=ConstantDdvValidator(
                    post_sds_result=failing_validation_result
                )
                ),
        ]
        for case in validation_cases:

            symbols = LineMatcherSymbolContext.of_sdv(
                line_matcher_symbol_name,
                successful_matcher_with_validation(case.actual)
            ).symbol_table
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
                            model=integration_check.arbitrary_model(),
                            arrangement=Arrangement(
                                symbols=symbols
                            ),
                            expectation=case.expected
                        )


class _TestFilesMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model = integration_check.model_of('string with at least one line')

        line_matcher = LineMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER',
            True,
        )
        after_bin_op = 'after bin op'
        lm_argument = lm_args.And([
            lm_args.SymbolReference(line_matcher.name),
            lm_args.Custom(after_bin_op),
        ])
        for quantifier in Quantifier:
            arguments = args2.Quantification(quantifier, lm_argument.as_str)
            with self.subTest(quantifier):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    source=arguments.as_remaining_source,
                    input_=model,
                    arrangement=arrangement_w_tcds(
                        symbols=line_matcher.symbol_table,
                    ),
                    expectation=Expectation(
                        ParseExpectation(
                            source=asrt_source.is_at_line(
                                current_line_number=1,
                                remaining_part_of_current_line=lm_argument.operator_name + ' ' + after_bin_op),
                            symbol_references=line_matcher.references_assertion
                        ),
                        ExecutionExpectation(
                            main_result=asrt_matching_result.matches_value(line_matcher.result_value)
                        )
                    ),
                )


class _TestStringTransformerValidatorIsApplied(TestCaseBase):
    def runTest(self):
        line_matcher_symbol = LineMatcherSymbolContext.of_primitive_constant(
            'valid_line_matcher',
            True)

        for case in failing_validation_cases():
            symbol_context = case.value.symbol_context

            symbols = SymbolContext.symbol_table_of_contexts([
                line_matcher_symbol,
                symbol_context,
            ])

            expected_symbol_references = asrt.matches_sequence([
                symbol_context.reference_assertion,
                is_reference_to_line_matcher__usage(line_matcher_symbol.name)
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
                            model=integration_check.arbitrary_model(),
                            arrangement=Arrangement(
                                symbols=symbols
                            ),
                            expectation=Expectation(
                                ParseExpectation(
                                    symbol_references=expected_symbol_references,
                                ),
                                ExecutionExpectation(
                                    validation=case.value.expectation,
                                ),
                            )
                        )


class _TestSymbolReferencesBase(_TestCaseBase):
    def _check_expectation_variants(self,
                                    common_arguments: CommonArgumentsConstructor,
                                    line_matcher: str,
                                    expected_symbols: ValueAssertion[Sequence[SymbolReference]]):
        parser = sut.parsers().full

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
                    assert isinstance(sdv, MatcherSdv)  # Sanity check
                    expected_symbols.apply_without_message(self, sdv.references)


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
        expected_symbol_reference_to_transformer = is_reference_to_line_matcher(line_matcher)

        expected_symbol_references = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        # ACT & ASSERT #

        self._check_expectation_variants(common_arguments, line_matcher, expected_symbol_references)
