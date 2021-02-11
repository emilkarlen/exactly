import unittest

from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    CHECKER
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import ExecutionExpectation, \
    Expectation2
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.program.test_resources import test_setups__proc_exe_set
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import \
    IntegerMatcherSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestTimeoutFromExecutionEnvIsPassedToCommandExecutor(),
        TestEnvironFromExecutionEnvIsPassedToCommandExecutor(),
    ])


class TestTimeoutFromExecutionEnvIsPassedToCommandExecutor(unittest.TestCase):
    def runTest(self):
        test_setup = test_setups__proc_exe_set.TimeoutTestSetup(self, expected_timeout=72)
        # ACT & ASSERT #
        CHECKER.check__abs_stx(
            self,
            InstructionArguments(
                test_setup.valid_program_wo_sym_refs(),
                CONST_TRUE_INT_MATCHER_SYMBOL.abstract_syntax,
            ),
            ArrangementPostAct2(
                symbols=CONST_TRUE_INT_MATCHER_SYMBOL.symbol_table,
                process_execution=test_setup.proc_exe_arr__w_settings_check,
            ),
            Expectation2(
                ParseExpectation(
                    symbol_usages=CONST_TRUE_INT_MATCHER_SYMBOL.usages_assertion
                ),
                ExecutionExpectation(
                    main_result=asrt_pfh.is_pass()
                ),
            )
        )


class TestEnvironFromExecutionEnvIsPassedToCommandExecutor(unittest.TestCase):
    def runTest(self):
        test_setup = test_setups__proc_exe_set.EnvironTestSetup(self, {
            'corona': 'please die',
            'covid-19': 'please end',
        })
        # ACT & ASSERT #
        CHECKER.check__abs_stx(
            self,
            InstructionArguments(
                test_setup.valid_program_wo_sym_refs(),
                CONST_TRUE_INT_MATCHER_SYMBOL.abstract_syntax,
            ),
            ArrangementPostAct2(
                symbols=CONST_TRUE_INT_MATCHER_SYMBOL.symbol_table,
                process_execution=test_setup.proc_exe_arr__w_settings_check,
            ),
            Expectation2(
                ParseExpectation(
                    symbol_usages=CONST_TRUE_INT_MATCHER_SYMBOL.usages_assertion
                ),
                ExecutionExpectation(
                    main_result=asrt_pfh.is_pass()
                ),
            )
        )


CONST_TRUE_INT_MATCHER_SYMBOL = IntegerMatcherSymbolContext.of_primitive_constant(
    'CONST_TRUE_INT_MATCHER',
    result=True,
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
