import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.instructions.before_assert import env as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib_test.instructions.before_assert.test_resources.configuration import BeforeAssertConfigurationBase
from shellcheck_lib_test.instructions.multi_phase_instructions.test_resources.env_instruction_test import \
    suite_for


class TheConfiguration(BeforeAssertConfigurationBase):
    def description(self) -> Description:
        return sut.description('instruction name')

    def parser(self) -> SingleInstructionParser:
        return sut.PARSER


def suite() -> unittest.TestSuite:
    return suite_for(TheConfiguration())
