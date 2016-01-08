import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.before_assert import execute as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from shellcheck_lib_test.instructions.before_assert.test_resources.instruction_check import Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.execute_instruction_test import \
    suite_for, Configuration
from shellcheck_lib_test.instructions.test_resources import svh_check__va


class TheConfiguration(BeforeAssertConfigurationBase, Configuration):
    def description(self) -> Description:
        return sut.description('instruction name')

    def expect_failure_because_specified_file_under_eds_is_missing(self):
        return Expectation(validation_post_setup=svh_check__va.is_validation_error())

    def parser(self) -> SingleInstructionParser:
        return sut.parser('instruction name')


def suite():
    return suite_for(TheConfiguration())


if __name__ == '__main__':
    unittest.main()
