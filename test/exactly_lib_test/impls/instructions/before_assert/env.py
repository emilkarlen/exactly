import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.impls.instructions.before_assert import env as sut
from exactly_lib_test.impls.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.env_instruction_test import \
    suite_for


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())


class TheConfiguration(BeforeAssertConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')