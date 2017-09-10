import unittest

from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contents_transformation
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals
from exactly_lib_test.instructions.assert_.test_resources.file_contents.line_matches.utils import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    PassOrFail, ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
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


class _TestCaseBase(unittest.TestCase):
    def __init__(self, configuration: InstructionTestConfigurationForContentsOrEquals):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self.configuration))

    def _check_variants_with_expectation_type(
            self,
            args_variant_constructor: InstructionArgumentsVariantConstructor,
            expected_result_of_positive_test: PassOrFail,
            actual_file_contents: str,
            symbols: SymbolTable = None,
            expected_symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        for expectation_type in ExpectationType:
            etc = ExpectationTypeConfig(expectation_type)
            with self.subTest(expectation_type=expectation_type,
                              any_or_every_keyword=instruction_options.ANY_LINE_ARGUMENT):

                args_variant = args_variant_constructor.construct(expectation_type,
                                                                  instruction_options.ANY_LINE_ARGUMENT)
                complete_instruction_arguments = self.configuration.first_line_argument(args_variant)

                for source in equivalent_source_variants__with_source_check(self, complete_instruction_arguments):
                    instruction_check.check(
                        self,
                        self.configuration.new_parser(),
                        source,
                        arrangement=
                        self.configuration.arrangement_for_contents(
                            actual_file_contents,
                            post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                            symbols=symbols),
                        expectation=
                        Expectation(
                            main_result=etc.main_result(expected_result_of_positive_test),
                            symbol_usages=expected_symbol_usages)
                    )


class _NoLineMatchesRegEx(_TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        regex_arg_str = '123'
        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(regex_arg_str=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.FAIL,
            actual_file_contents=actual_contents,
        )


class _ALineMatchesRegEx(_TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        regex_arg_str = 'MATCH'
        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(regex_arg_str=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_contents,
        )


class _AWholeLineMatchesRegEx(_TestCaseBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        regex_arg_str = '^MATCH$'
        self._check_variants_with_expectation_type(
            InstructionArgumentsVariantConstructor(regex_arg_str=regex_arg_str),
            expected_result_of_positive_test=PassOrFail.PASS,
            actual_file_contents=actual_contents,
        )


class _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(_TestCaseBase):
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
            actual_file_contents=actual_original_contents,
            symbols=symbol_table_with_transformer,
            expected_symbol_usages=expected_symbol_usages,
        )
