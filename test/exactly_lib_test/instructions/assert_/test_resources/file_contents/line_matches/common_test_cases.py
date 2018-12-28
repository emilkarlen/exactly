import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.util.logic_types import ExpectationType, Quantifier
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources.line_matcher import is_line_matcher_reference_to
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import syntax_for_regex_matcher
from exactly_lib_test.test_case_utils.string_matcher.parse.line_matches import test_resources as tr
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    pfh_expectation_type_config
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
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
                        self.configuration.new_parser().parse(
                            ARBITRARY_FS_LOCATION_INFO,
                            self.configuration.source_for(args_variant))


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


class _TestSymbolReferenceForStringTransformerIsReported(_TestCaseBase):
    def runTest(self):
        # ARRANGE #
        parser = self.configuration.new_parser()

        lines_transformer_name = 'the_transformer'

        common_arguments = arguments_building.CommonArgumentsConstructor(lines_transformer_name)
        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(lines_transformer_name)

        expected_symbol_usages = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        for expectation_type in ExpectationType:
            etc = pfh_expectation_type_config(expectation_type)
            for quantifier in Quantifier:
                with self.subTest(expectation_type=expectation_type,
                                  quantifier=quantifier.name):
                    arguments_for_implicit_file = arguments_building.ImplicitActualFileArgumentsConstructor(
                        common_arguments,
                        arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier,
                                                                                    syntax_for_regex_matcher(
                                                                                        'regex'))
                    ).apply(etc)
                    source = self.configuration.arguments_for(arguments_for_implicit_file).as_remaining_source
                    instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                    assert isinstance(instruction, AssertPhaseInstruction)  # Sanity check
                    expected_symbol_usages.apply_without_message(self, instruction.symbol_usages())


class _TestSymbolReferenceForLineMatcherIsReported(_TestCaseBase):
    def runTest(self):
        # ARRANGE #
        parser = self.configuration.new_parser()

        line_matcher_name = 'the_line_matcher'

        common_arguments = arguments_building.CommonArgumentsConstructor()
        expected_symbol_reference_to_transformer = is_line_matcher_reference_to(line_matcher_name)

        expected_symbol_usages = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        for expectation_type in ExpectationType:
            etc = pfh_expectation_type_config(expectation_type)
            for quantifier in Quantifier:
                with self.subTest(expectation_type=expectation_type,
                                  quantifier=quantifier.name):
                    arguments_for_implicit_file = arguments_building.ImplicitActualFileArgumentsConstructor(
                        common_arguments,
                        arguments_building.LineMatchesAssertionArgumentsConstructor(quantifier,
                                                                                    line_matcher_name)
                    ).apply(etc)
                    source = self.configuration.arguments_for(arguments_for_implicit_file).as_remaining_source
                    instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                    assert isinstance(instruction, AssertPhaseInstruction)  # Sanity check
                    expected_symbol_usages.apply_without_message(self, instruction.symbol_usages())
