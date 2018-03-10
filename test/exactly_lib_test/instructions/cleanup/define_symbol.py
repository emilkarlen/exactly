import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.cleanup import define_symbol as sut
from exactly_lib_test.instructions.cleanup.test_resources.configuration import CleanupConfigurationBase
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.define_symbol_test import \
    suite_for


class TheConfiguration(CleanupConfigurationBase):
    SETUP = sut.setup('instruction-name')

    def instruction_setup(self) -> SingleInstructionSetup:
        return self.SETUP


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())
