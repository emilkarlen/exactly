import unittest
from typing import Sequence

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.setup import run as sut
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib_test.impls.instructions.multi_phase.run_program.test_resources.instruction_test import \
    suite_for, \
    Configuration
from exactly_lib_test.impls.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.impls.instructions.setup.test_resources.instruction_check import Expectation
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_because_specified_file_under_sds_is_missing(
            self,
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
    ):
        return Expectation(main_result=asrt_sh.is_hard_error(),
                           symbol_usages=symbol_usages)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
