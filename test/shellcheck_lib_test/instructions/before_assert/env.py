import unittest

from exactly_lib.instructions.before_assert import env as sut
from exactly_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.env_instruction_test import \
    suite_for


class TheConfiguration(BeforeAssertConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())
