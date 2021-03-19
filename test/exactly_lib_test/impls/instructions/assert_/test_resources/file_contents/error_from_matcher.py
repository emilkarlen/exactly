import unittest

from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import ExecutionExpectation, \
    MultiSourceExpectation
from exactly_lib_test.impls.types.matcher.test_resources import matchers
from exactly_lib_test.impls.types.string_matcher.test_resources import validation_cases
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.symbol_context import StringMatcherSymbolContext


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        ValidationErrorFromMatcher(configuration),
        HardErrorFromMatcher(configuration),
    ])


class ValidationErrorFromMatcher(TestWithConfigurationBase):
    def runTest(self):
        for validation_case in validation_cases.failing_validation_cases():
            invalid_matcher = validation_case.value.symbol_context
            self.configuration.checker.check__abs_stx__source_variants(
                self,
                self.configuration.syntax_for_matcher(invalid_matcher.abstract_syntax),
                self.configuration.arrangement_for_contents(
                    '',
                    post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                    symbols=invalid_matcher.symbol_table,
                ).as_arrangement_2(),
                MultiSourceExpectation(
                    symbol_usages=invalid_matcher.usages_assertion,
                    execution=ExecutionExpectation.validation_corresponding_to__post_sds_as_hard_error(
                        validation_case.value.actual,
                    )
                ),
            )


class HardErrorFromMatcher(TestWithConfigurationBase):
    def runTest(self):
        error_message = 'the error message'
        matcher_that_raises_hard_error = StringMatcherSymbolContext.of_primitive(
            'STRING_MATCHER',
            matchers.MatcherThatReportsHardError(error_message)
        )
        self.configuration.checker.check__abs_stx__source_variants(
            self,
            self.configuration.syntax_for_matcher(matcher_that_raises_hard_error.abstract_syntax),
            self.configuration.arrangement_for_contents(
                '',
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                symbols=matcher_that_raises_hard_error.symbol_table,
            ).as_arrangement_2(),
            MultiSourceExpectation(
                symbol_usages=matcher_that_raises_hard_error.usages_assertion,
                execution=ExecutionExpectation(
                    main_result=pfh_assertions.is_hard_error(
                        asrt_text_doc.is_string_for_test_that_equals(error_message)
                    ),
                )
            ),
        )
