import unittest

from exactly_lib.instructions.setup import env as sut
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.env_instruction_test import \
    suite_for
from exactly_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase


class TheConfiguration(SetupConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
