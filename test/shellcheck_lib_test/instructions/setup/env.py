import unittest

from shellcheck_lib.instructions.setup import env as sut
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.env_instruction_test import \
    suite_for
from shellcheck_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase


class TheConfiguration(SetupConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
