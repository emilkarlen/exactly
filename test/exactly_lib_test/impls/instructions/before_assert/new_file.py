import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.before_assert import new_file as sut
from exactly_lib_test.impls.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import phase_instruction_test


def suite() -> unittest.TestSuite:
    return phase_instruction_test.suite_for(TheConfiguration())


class TheConfiguration(BeforeAssertConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
