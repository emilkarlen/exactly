import unittest

from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationAndNegationArgumentBase, \
    suite_for__conf__not_argument
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSymbolContext, \
    is_reference_to_string_matcher__usage
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.string_matcher.test_resources.arguments_building import args
from exactly_lib_test.test_case_file_structure.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case_utils.string_matcher.test_resources.transformations import \
    TRANSFORMER_OPTION_ALTERNATIVES
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    test_cases = [
        HardErrorFromMatcher,
    ]
    return suite_for__conf__not_argument(configuration, test_cases)


class HardErrorFromMatcher(TestWithConfigurationAndNegationArgumentBase):
    def runTest(self):
        hard_error_message = 'the error message'
        matcher_that_raises_hard_error = StringMatcherSymbolContext.of_primitive(
            'STRING_MATCHER',
            matchers.MatcherThatReportsHardError(hard_error_message)
        )
        for maybe_with_transformer_option in TRANSFORMER_OPTION_ALTERNATIVES:
            with self.subTest(maybe_with_transformer_option=maybe_with_transformer_option):
                self._check_with_source_variants(
                    self.configuration.arguments_for(
                        args('{maybe_with_transformer_option} {maybe_not} {matcher}',
                             maybe_with_transformer_option=maybe_with_transformer_option,
                             maybe_not=self.maybe_not.nothing__if_positive__not_option__if_negative,
                             matcher=matcher_that_raises_hard_error.name__sym_ref_syntax)),
                    self.configuration.arrangement_for_contents(
                        '',
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                        symbols=matcher_that_raises_hard_error.symbol_table,
                    ),
                    Expectation(
                        symbol_usages=asrt.matches_singleton_sequence(
                            is_reference_to_string_matcher__usage(matcher_that_raises_hard_error.name)
                        ),
                        main_result=pfh_assertions.is_hard_error(
                            asrt_text_doc.is_string_for_test_that_equals(hard_error_message)
                        ),
                    ),
                )
