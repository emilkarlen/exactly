import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.setup import execute as sut
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.execute_instruction_test import suite_for, \
    Configuration
from shellcheck_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from shellcheck_lib_test.instructions.setup.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.test_resources import sh_check


class TheConfiguration(SetupConfigurationBase, Configuration):
    def expect_failure_because_specified_file_under_eds_is_missing(self):
        return Expectation(main_result=sh_check.IsHardError())

    def parser(self) -> SingleInstructionParser:
        return sut.parser('instruction name')


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
