import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.string_matcher.emptiness_matcher import EmptinessStringMatcher
from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvConstant
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources.string_matcher import string_matcher_sdv_constant_test_impl, \
    is_reference_to_string_matcher
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.arguments_building import args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.misc import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_transformer.test_resources import EveryLineEmptyStringTransformer


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        ParseShouldFailWhenThereAreSuperfluousArguments,
        ParseShouldFailWhenSymbolNameHasInvalidSyntax,

        ActualFileIsEmpty,
        ActualFileIsEmptyAfterTransformation,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


SYMBOL_FOR_EMPTINESS_MATCHER = NameAndValue(
    'SYMBOL_NAME',
    string_matcher_sdv_constant_test_impl(EmptinessStringMatcher(ExpectationType.POSITIVE))
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
                         symbol_reference=symbol_reference_syntax_for_name(SYMBOL_FOR_EMPTINESS_MATCHER.name)),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class ActualFileIsEmpty(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        symbols = SymbolTable({
            SYMBOL_FOR_EMPTINESS_MATCHER.name: container(SYMBOL_FOR_EMPTINESS_MATCHER.value),
        })
        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_matcher(SYMBOL_FOR_EMPTINESS_MATCHER.name),
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
        named_transformer = NameAndValue('the_transformer',
                                         StringTransformerSdvConstant(
                                             EveryLineEmptyStringTransformer()))

        original_file_contents = 'some\ntext'

        symbols = SymbolTable({
            named_transformer.name: container(named_transformer.value),
            SYMBOL_FOR_EMPTINESS_MATCHER.name: container(SYMBOL_FOR_EMPTINESS_MATCHER.value),
        })

        expected_symbol_references = asrt.matches_sequence([
            is_reference_to_string_transformer(named_transformer.name),
            is_reference_to_string_matcher(SYMBOL_FOR_EMPTINESS_MATCHER.name),
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
