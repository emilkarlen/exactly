import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.setup import env as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.env_instruction_test import \
    suite_for
from shellcheck_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase


class TheConfiguration(SetupConfigurationBase):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def parser(self) -> SingleInstructionParser:
        return self.instruction_setup()

    def description(self) -> Description:
        return self.instruction_setup().description


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
