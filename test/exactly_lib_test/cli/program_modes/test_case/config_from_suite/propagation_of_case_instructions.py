import unittest

from exactly_lib.cli.main_program import TestCaseDefinitionForMainProgram
from exactly_lib.processing import exit_values
from exactly_lib_test.cli.program_modes.test_case.config_from_suite.test_resources import run_test_case, cli_args_for, \
    test_suite_definition_without_instructions
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_suite.execution.test_resources import instruction_name_extractor, instruction_setup
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    test_case_handling_setup_with_identity_preprocessor


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


REGISTER_INSTRUCTION_NAME = 'register'

SETUP_INSTRUCTION_IN_CONTAINING_SUITE = 'containing suite'
SETUP_INSTRUCTION_IN_CASE = 'case'

CASE_THAT_REGISTERS_MARKER = """\
[setup]

register {marker}
"""

SUITE_WITH_SETUP_INSTRUCTION = """\
[setup]

register {marker}
"""


class Test(unittest.TestCase):
    def test_setup_instructions_in_containing_suite_SHOULD_be_executed_first_in_the_case(self):
        # ARRANGE #

        expected_instruction_recording = [
            # First test case
            SETUP_INSTRUCTION_IN_CONTAINING_SUITE,
            SETUP_INSTRUCTION_IN_CASE,
        ]

        suite_file = File('test.suite',
                          SUITE_WITH_SETUP_INSTRUCTION.format(
                              marker=SETUP_INSTRUCTION_IN_CONTAINING_SUITE))

        case_file = File('test.case',
                         CASE_THAT_REGISTERS_MARKER.format(
                             marker=SETUP_INSTRUCTION_IN_CASE))

        suite_and_case_files = DirContents([
            suite_file,
            case_file,
        ])

        command_line_arguments = cli_args_for(
            suite_file=suite_file.name,
            case_file=case_file.name,
        )

        recorder = []

        test_case_definition = TestCaseDefinitionForMainProgram(instruction_name_extractor,
                                                                instruction_setup(REGISTER_INSTRUCTION_NAME, recorder),
                                                                [])
        test_case_handling_setup = test_case_handling_setup_with_identity_preprocessor()
        test_suite_definition = test_suite_definition_without_instructions()
        # ACT #
        actual_result = run_test_case(command_line_arguments,
                                      suite_and_case_files,
                                      test_case_definition,
                                      test_suite_definition,
                                      test_case_handling_setup)
        # ASSERT #

        self.assertEqual(exit_values.EXECUTION__PASS.exit_code,
                         actual_result.exitcode,
                         'Sanity check of result indicator')

        self.assertEqual(expected_instruction_recording,
                         recorder)
