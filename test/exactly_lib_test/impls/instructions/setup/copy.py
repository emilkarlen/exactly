import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.setup import copy as sut
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources import \
    copy_instruction_test
from exactly_lib_test.impls.instructions.setup.test_resources.configuration import SetupConfigurationBase


def suite() -> unittest.TestSuite:
    return copy_instruction_test.suite_for(TheConfiguration())


class TheConfiguration(SetupConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
