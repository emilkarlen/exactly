import unittest

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contents_transformation
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.line_matches.utils import \
    InstructionArgumentsVariantConstructor, TestCaseBase
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail
from exactly_lib_test.named_element.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_case_constructors = [
        _NoLineMatchesRegEx,
        _ALineMatchesRegEx,
        _AWholeLineMatchesRegEx,

        _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents,
    ]
    return unittest.TestSuite([
        test_case_constructor(configuration)
        for test_case_constructor in test_case_constructors
    ])


class _NoLineMatchesRegEx(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        regex_arg_str = '123'
        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(regex_arg_str=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.FAIL,
            any_or_every_keyword=instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            actual_file_contents=actual_contents,
        )


class _ALineMatchesRegEx(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        regex_arg_str = 'MATCH'
        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(regex_arg_str=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.PASS,
            any_or_every_keyword=instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            actual_file_contents=actual_contents,
        )


class _AWholeLineMatchesRegEx(TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        regex_arg_str = '^MATCH$'
        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(regex_arg_str=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.PASS,
            any_or_every_keyword=instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            actual_file_contents=actual_contents,
        )


class _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = NameAndValue('the_transformer',
                                         LinesTransformerConstant(
                                             contents_transformation.ToUppercaseLinesTransformer()))

        actual_original_contents = lines_content(['only',
                                                  'lowercase',
                                                  'letters'])

        reg_ex_that_matches_uppercase_character = '[A-Z]'

        symbol_table_with_transformer = SymbolTable({
            named_transformer.name: container(named_transformer.value)
        })

        expected_symbol_reference_to_transformer = is_lines_transformer_reference_to(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(
                regex_arg_str=reg_ex_that_matches_uppercase_character,
                transformer=named_transformer.name),
            expected_result_of_positive_test=PassOrFail.PASS,
            any_or_every_keyword=instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
            actual_file_contents=actual_original_contents,
            symbols=symbol_table_with_transformer,
            expected_symbol_usages=expected_symbol_usages,
        )
