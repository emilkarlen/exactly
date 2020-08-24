import unittest

from exactly_lib_test.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfigurationForContentsOrEquals, TestWithConfigurationBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as sm_args
from exactly_lib_test.test_case_file_structure.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY


def suite_for(configuration: InstructionTestConfigurationForContentsOrEquals) -> unittest.TestSuite:
    return unittest.TestSuite([
        StringMatcherShouldBeParsedAsFullExpression(configuration),
    ])


class StringMatcherShouldBeParsedAsFullExpression(TestWithConfigurationBase):
    def runTest(self):
        # ARRANGE #
        sm_1 = StringMatcherSymbolContextOfPrimitiveConstant('sm_1', True)
        sm_2 = StringMatcherSymbolContextOfPrimitiveConstant('sm_2', False)
        symbols = [sm_1, sm_2]
        arguments = sm_args.disjunction([sm_1.argument, sm_2.argument])
        is_pass = sm_1.result_value or sm_2.result_value
        # ACT & ASSERT #
        self._check_with_source_variants(
            self.configuration.arguments_for(arguments.as_str),
            self.configuration.arrangement_for_contents(
                actual_contents='',
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                post_sds_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
            ),
            Expectation(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(symbols),
                main_result=asrt_pfh.is_non_hard_error(is_pass),
            ),
        )
