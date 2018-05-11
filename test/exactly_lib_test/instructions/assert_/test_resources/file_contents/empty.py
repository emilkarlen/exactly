import unittest
from typing import Iterable

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerConstant
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.contents_of_file.test_resources.arguments_building import args
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.instructions.assert_.test_resources.file_contents.util.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        ParseShouldFailWhenThereAreSuperfluousArguments,
        ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument,
        ActualFileIsEmpty,
        ActualFileIsNonEmpty,

        ActualFileIsEmptyAfterTransformation,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


class ParseShouldFailWhenThereAreSuperfluousArguments(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {empty} superfluous-argument',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(
    TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {empty} <<MARKER',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative),
                    ['single line',
                     'MARKER'])
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class ActualFileIsEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {empty}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)),
                    self.configuration.arrangement_for_contents(
                        '',
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(main_result=self.maybe_not.pass__if_positive__fail__if_negative),
                )


class ActualFileIsNonEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {empty}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)),
                    self.configuration.arrangement_for_contents(
                        'contents that makes the file non-empty',
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY),
                    Expectation(main_result=self.maybe_not.fail__if_positive__pass_if_negative),
                )


class ActualFileIsEmptyAfterTransformation(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = NameAndValue('the_transformer',
                                         StringTransformerConstant(
                                             DeleteEverythingStringTransformer()))

        original_file_contents = 'some\ntext'

        symbols = SymbolTable({
            named_transformer.name: container(named_transformer.value)
        })

        expected_symbol_reference_to_transformer = is_reference_to_string_transformer(named_transformer.name)

        expected_symbol_usages = asrt.matches_sequence([expected_symbol_reference_to_transformer])

        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{transform_option} {the_transformer} {maybe_not} {empty}',
                     the_transformer=named_transformer.name,
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative)),
            self.configuration.arrangement_for_contents(
                original_file_contents,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols),
            Expectation(
                main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_usages),
        )


class DeleteEverythingStringTransformer(StringTransformer):
    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(lambda x: '', lines)
