import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.before_assert import define_symbol as sut
from exactly_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.define_symbol_test import \
    suite_for


class TheConfiguration(BeforeAssertConfigurationBase):
    SETUP = sut.setup('instruction-name')

    def instruction_setup(self) -> SingleInstructionSetup:
        return self.SETUP


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
