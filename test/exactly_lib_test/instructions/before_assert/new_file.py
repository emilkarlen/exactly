import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert import new_file as sut
from exactly_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources import \
    new_file_instruction_test


def suite() -> unittest.TestSuite:
    return new_file_instruction_test.suite_for(TheConfiguration())


class TheConfiguration(BeforeAssertConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
