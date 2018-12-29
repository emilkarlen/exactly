import unittest

from typing import Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib_test.symbol.test_resources.line_matcher import is_line_matcher_reference_to
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.string_matcher.parse.line_matches import test_resources as tr
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import \
    CommonArgumentsConstructor
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.instruction_test_configuration import \
    TestConfigurationForMatcher
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    expectation_type_config__non_is_success
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    configuration = TestConfigurationForMatcher()

    test_case_constructors = [
        _ParseWithMissingLineMatcherArgument,
        _ParseWithSuperfluousArgument,
        _ParseWithInvalidLineMatcher,

        _TestSymbolReferenceForStringTransformerIsReported,
        _TestSymbolReferenceForLineMatcherIsReported,
    ]
    return unittest.TestSuite([
        test_case_constructor(configuration)
        for test_case_constructor in test_case_constructors
    ])


class _TestCaseBase(unittest.TestCase):
    def __init__(self,
                 configuration: InstructionTestConfigurationForContentsOrEquals):
        super().__init__()
        self.configuration = configuration

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


class _ParseWithSuperfluousArgument(_TestCaseBase):
    def runTest(self):
        self._check_variants_with_expectation_type_and_any_or_every(
            tr.ArgumentsConstructorForPossiblyInvalidSyntax(line_matcher=syntax_for_regex_matcher('regex'),
                                                            superfluous_args_str='superfluous'))


class _ParseWithInvalidLineMatcher(_TestCaseBase):
    def runTest(self):
        self._check_variants_with_expectation_type_and_any_or_every(
            tr.args_constructor_for(line_matcher=syntax_for_regex_matcher('**')))


class _TestSymbolReferencesBase(_TestCaseBase):
    def _check_expectation_variants(self,
                                    common_arguments: CommonArgumentsConstructor,
                                    line_matcher: str,
                                    expected_symbols: ValueAssertion[Sequence[SymbolReference]]):
        parser = self.configuration.new_parser()

        for expectation_type in ExpectationType:
            etc = expectation_type_config__non_is_success(expectation_type)
            for quantifier in Quantifier:
                with self.subTest(expectation_type=expectation_type,
                                  quantifier=quantifier.name):
                    arguments_for_implicit_file = arguments_building.ImplicitActualFileArgumentsConstructor(
                        common_arguments,
                        arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier,
                                                                                    line_matcher)
                    ).apply(etc)
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
