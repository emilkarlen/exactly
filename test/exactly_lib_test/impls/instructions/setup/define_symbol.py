import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.setup import define_symbol as sut
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.define_symbol_test import \
    suite_for
from exactly_lib_test.impls.instructions.setup.test_resources.configuration import SetupConfigurationBase


class TheConfiguration(SetupConfigurationBase):
    SETUP = sut.setup('instruction-name')

    def instruction_setup(self) -> SingleInstructionSetup:
        return self.SETUP


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
