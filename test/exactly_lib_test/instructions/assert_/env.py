import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_ import env as sut
from exactly_lib_test.instructions.assert_.test_resources.configuration import AssertConfigurationBase
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.env_instruction_test import \
    suite_for


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(AssertConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
