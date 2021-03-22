import unittest

from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.impls.types.string_matcher.test_resources.abstract_syntaxes import EmptyAbsStx, \
    StringMatcherNegationAbsStx
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.rich_abstract_syntaxes import HereDocAbsStx


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        ParseShouldFailWhenThereAreSuperfluousArguments(configuration),
        ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(configuration),
        ActualFileIsEmpty(configuration),
        ActualFileIsEmptyAndMatcherIsNegated(configuration),
        ActualFileIsNonEmpty(configuration),
    ])


class ParseShouldFailWhenThereAreSuperfluousArguments(TestWithConfigurationBase):
    def runTest(self):
        self.configuration.parse_checker.check_invalid_syntax__src_var_consume_last_line_abs_stx(
            self,
            self.configuration.syntax_for_matcher(
                SequenceAbsStx.followed_by_superfluous(
                    self.configuration.syntax_for_matcher(EmptyAbsStx()),
                )
            )
        )


class ParseShouldFailWhenThereAreSuperfluousArgumentsInFormOfValidHereDocument(TestWithConfigurationBase):
    def runTest(self):
        self.configuration.parse_checker.check_invalid_syntax__src_var_consume_last_line_abs_stx(
            self,
            self.configuration.syntax_for_matcher(
                SequenceAbsStx([
                    self.configuration.syntax_for_matcher(EmptyAbsStx()),
                    HereDocAbsStx('single line\n'),
                ])
            )
        )


class ActualFileIsEmpty(TestWithConfigurationBase):
    def runTest(self):
        self.configuration.checker.check__abs_stx__source_variants(
            self,
            self.configuration.syntax_for_matcher(EmptyAbsStx()),
            self.configuration.arrangement_for_contents(
                '',
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
            ).as_arrangement_2(),
            MultiSourceExpectation(
                execution=ExecutionExpectation(
                    main_result=asrt_pfh.is_pass(),
                )
            ),
        )


class ActualFileIsEmptyAndMatcherIsNegated(TestWithConfigurationBase):
    def runTest(self):
        self.configuration.checker.check__abs_stx__source_variants(
            self,
            self.configuration.syntax_for_matcher(
                StringMatcherNegationAbsStx(EmptyAbsStx())
            ),
            self.configuration.arrangement_for_contents(
                '',
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
            ).as_arrangement_2(),
            MultiSourceExpectation(
                execution=ExecutionExpectation(
                    main_result=asrt_pfh.is_fail(),
                )
            ),
        )


class ActualFileIsNonEmpty(TestWithConfigurationBase):
    def runTest(self):
        self.configuration.checker.check__abs_stx__source_variants(
            self,
            self.configuration.syntax_for_matcher(EmptyAbsStx()),
            self.configuration.arrangement_for_contents(
                'contents that makes the file non-empty',
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
            ).as_arrangement_2(),
            MultiSourceExpectation(
                execution=ExecutionExpectation(
                    main_result=asrt_pfh.is_fail(),
                )
            ),
        )
