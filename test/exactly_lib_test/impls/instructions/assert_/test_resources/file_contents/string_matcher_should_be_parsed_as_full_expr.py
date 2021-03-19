import unittest

from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    TestWithConfigurationBase, InstructionTestConfiguration
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.impls.types.string_matcher.test_resources.abstract_syntaxes import StringMatcherInfixOpAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.symbol_context import \
    StringMatcherSymbolContextOfPrimitiveConstant


def suite_for(configuration: InstructionTestConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        StringMatcherShouldBeParsedAsFullExpression(configuration),
    ])


class StringMatcherShouldBeParsedAsFullExpression(TestWithConfigurationBase):
    def runTest(self):
        # ARRANGE #
        sm_1 = StringMatcherSymbolContextOfPrimitiveConstant('sm_1', True)
        sm_2 = StringMatcherSymbolContextOfPrimitiveConstant('sm_2', False)
        symbols = [sm_1, sm_2]
        matcher_syntax = StringMatcherInfixOpAbsStx.disjunction([
            sm_1.abstract_syntax,
            sm_2.abstract_syntax,
        ])
        is_pass = sm_1.result_value or sm_2.result_value
        # ACT & ASSERT #
        self.configuration.checker.check__abs_stx__source_variants(
            self,
            self.configuration.syntax_for_matcher(matcher_syntax),
            self.configuration.arrangement_for_contents(
                actual_contents='',
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
            ).as_arrangement_2(),
            MultiSourceExpectation(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(symbols),
                execution=ExecutionExpectation(
                    main_result=asrt_pfh.is_non_hard_error(is_pass),
                ),
            )
        )
