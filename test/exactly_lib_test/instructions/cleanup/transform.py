import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.cleanup import transform as sut
from exactly_lib_test.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources import \
    transform_instruction_test


def suite() -> unittest.TestSuite:
    return transform_instruction_test.suite_for(TheConfiguration())


class TheConfiguration(CleanupConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
