import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.file_contents import contents_transformation
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, \
    TestWithConfigurationAndNegationArgumentBase, suite_for__conf__not_argument, args
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducer
from exactly_lib_test.named_element.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        _ParseWithMissingRegExArgument,
        _ParseWithSuperfluousArgument,

        _ParseWithInvalidRegEx,
        _NoLineMatchesRegEx,
        _ALineMatchesRegEx,
        _AWholeLineMatchesRegEx,

        _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


class ActResultProducerFromHomeAndSds2Str(ActResultProducer):
    def __init__(self, home_and_sds_2_str):
        self.home_and_sds_2_str = home_and_sds_2_str


class _ParseWithMissingRegExArgument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().parse(
                self.configuration.source_for(
                    args('{maybe_not} {any} {line_matches}',
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)))


class _ParseWithSuperfluousArgument(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().parse(
                self.configuration.source_for(
                    args('{maybe_not} {any} {line_matches} abc superfluous',
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)))


class _ParseWithInvalidRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().parse(
                self.configuration.source_for(
                    args('{maybe_not} {any} {line_matches} **',
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)))


class _NoLineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        reg_ex = '123'
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{maybe_not} {any} {line_matches} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(main_result=self.maybe_not.fail__if_positive__pass_if_negative),
        )


class _ALineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = 'ATC'
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{maybe_not} {any} {line_matches} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative),
        )


class _AWholeLineMatchesRegEx(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        reg_ex = '^MATCH$'
        self._check_single_instruction_line_with_source_variants(
            self.configuration.first_line_argument(
                args("{maybe_not} {any} {line_matches} '{reg_ex}'",
                     reg_ex=reg_ex,
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)),
            self.configuration.arrangement_for_contents(
                actual_contents,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
            Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative),
        )


class _WhenLinesTransformerIsGivenThenComparisonShouldBeAppliedToTransformedContents(
    TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = NameAndValue('the_transformer',
                                         LinesTransformerConstant(
                                             contents_transformation.ToUppercaseLinesTransformer()))

        contents_generator = contents_transformation.TransformedContentsSetup(
            original='some\ntext',
            transformed='SOME\nTEXT',
        )

        symbols = SymbolTable({
            named_transformer.name: container(named_transformer.value)
        })

        expected_symbol_reference_to_transformer = is_lines_transformer_reference_to(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence([
            expected_symbol_reference_to_transformer
        ])

        reg_ex_that_matches_uppercase_character = '[A-Z]'

        self._check_single_instruction_line_with_source_variants(
            instruction_argument=
            self.configuration.first_line_argument(
                args("{transform_option} {transformer} {maybe_not} {any} {line_matches} '{reg_ex}'",
                     transformer=named_transformer.name,
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                     reg_ex=reg_ex_that_matches_uppercase_character,
                     )),
            arrangement=
            self.configuration.arrangement_for_contents_from_fun(
                contents_generator.contents_before_replacement,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols,
            ),
            expectation=
            Expectation(
                main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_usages,
            ),
        )
