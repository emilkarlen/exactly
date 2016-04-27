import unittest

from exactly_lib.instructions.assert_phase import env as sut
from exactly_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.assert_phase.test_resources.configuration import AssertConfigurationBase
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.env_instruction_test import \
    suite_for


class TheConfiguration(AssertConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
