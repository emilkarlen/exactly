import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.string_matcher.impl.emptiness import EmptinessStringMatcher
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.logic.test_resources.string_transformer.assertions import \
    is_reference_to_string_transformer__usage
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.string_matcher import is_reference_to_string_matcher__usage, \
    StringMatcherSymbolContext
from exactly_lib_test.symbol.test_resources.symbol_syntax import \
    NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    every_line_empty


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        ParseShouldFailWhenThereAreSuperfluousArguments,
        ParseShouldFailWhenSymbolNameHasInvalidSyntax,

        ActualFileIsEmpty,
        ActualFileIsEmptyAfterTransformation,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


SYMBOL_FOR_EMPTINESS_MATCHER = StringMatcherSymbolContext.of_primitive(
    'SYMBOL_NAME',
    EmptinessStringMatcher()
)


class ParseShouldFailWhenThereAreSuperfluousArguments(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {symbol_reference} superfluous-argument',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                         symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class ParseShouldFailWhenSymbolNameHasInvalidSyntax(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        parser = self.configuration.new_parser()
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                source = self.configuration.source_for(
                    args('{maybe_with_transformer_option} {maybe_not} {symbol_reference}',
                         maybe_with_transformer_option=maybe_with_transformer_option,
                         maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                         symbol_reference=NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class ActualFileIsEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        symbols = SYMBOL_FOR_EMPTINESS_MATCHER.symbol_table
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_matcher__usage(SYMBOL_FOR_EMPTINESS_MATCHER.name),
        ])

        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {symbol_reference}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                             symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                    self.configuration.arrangement_for_contents(
                        '',
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                        symbols=symbols),
                    Expectation(
                        main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                        symbol_usages=expected_symbol_references),
                )


class ActualFileIsEmptyAfterTransformation(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        # ARRANGE #
        named_transformer = StringTransformerSymbolContext.of_primitive('the_transformer',
                                                                        every_line_empty())

        original_file_contents = 'some\ntext'

        symbols = SymbolContext.symbol_table_of_contexts([
            named_transformer,
            SYMBOL_FOR_EMPTINESS_MATCHER,
        ])

        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer__usage(named_transformer.name),
            is_reference_to_string_matcher__usage(SYMBOL_FOR_EMPTINESS_MATCHER.name),
        ])

        self._check_with_source_variants(
            self.configuration.arguments_for(
                args('{transform_option} {the_transformer} {maybe_not} {symbol_reference}',
                     the_transformer=named_transformer.name,
                     maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                     symbol_reference=SYMBOL_FOR_EMPTINESS_MATCHER.name)),
            self.configuration.arrangement_for_contents(
                original_file_contents,
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=symbols),
            Expectation(
                main_result=self.maybe_not.pass__if_positive__fail__if_negative,
                symbol_usages=expected_symbol_references),
        )
