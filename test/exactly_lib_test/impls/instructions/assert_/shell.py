import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.assert_ import shell as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.shell_instruction_test import \
    Configuration, suite_for
from exactly_lib_test.test_case.result.test_resources import pfh_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for(TheConfiguration()),
        suite_for_instruction_documentation(sut.TheDocumentation('instruction-name')),
    ])


class TheConfiguration(AssertConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        return Expectation(main_result=pfh_assertions.is_fail__with_arbitrary_message())

    def expectation_for_zero_exitcode(self) -> Expectation:
        return Expectation()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
