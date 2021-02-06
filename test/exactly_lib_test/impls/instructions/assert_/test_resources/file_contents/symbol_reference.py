import unittest

from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import \
    StringMatcherSymbolContextOfPrimitiveConstant


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        PassIffMatcherGivesTrue(configuration),
    ])


class PassIffMatcherGivesTrue(TestWithConfigurationBase):
    def runTest(self):
        # ARRANGE #
        for matcher_result in [False, True]:
            matcher = StringMatcherSymbolContextOfPrimitiveConstant('STRING_MATCHER', matcher_result)
            with self.subTest(matcher_result=matcher_result):
                # ACT & ASSERT #
                self.configuration.checker.check__abs_stx__source_variants(
                    self,
                    self.configuration.syntax_for_matcher(matcher.abstract_syntax),
                    self.configuration.arrangement_for_contents(
                        actual_contents='',
                        symbols=matcher.symbol_table,
                        post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                    ).as_arrangement_2(),
                    MultiSourceExpectation(
                        symbol_usages=matcher.usages_assertion,
                        execution=ExecutionExpectation(
                            main_result=asrt_pfh.is_non_hard_error(matcher.result_value),
                        ),
                    )
                )
