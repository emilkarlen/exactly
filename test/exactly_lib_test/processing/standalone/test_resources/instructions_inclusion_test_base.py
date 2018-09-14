import unittest
from pathlib import Path

from exactly_lib.cli.main_program import TestSuiteDefinition
from exactly_lib.processing import exit_values
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.section_document.test_resources.misc import space_separator_instruction_name_extractor
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_suite.test_resources.list_recording_instructions import \
    instruction_setup_with_setup_instructions, Recording
from exactly_lib_test.test_suite.test_resources.processing_utils import \
    test_case_handling_setup_with_identity_preprocessor
from exactly_lib_test.test_suite.test_resources.test_suite_definition import test_suite_definition_without_instructions

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


class TestCaseRunner:
    def run(self,
            parsing_setup: TestCaseParsingSetup,
            test_case_handling_setup: TestCaseHandlingSetup,
            test_suite_definition: TestSuiteDefinition,
            case_file: Path,
            suite_file: Path) -> SubProcessResult:
        raise NotImplementedError('abstract method')


class TestInclusionOfCaseContentsFromSuiteTestBase(unittest.TestCase):
    def _setup_instructions_in_containing_suite_SHOULD_be_executed_first_in_the_case(self,
                                                                                     test_case_runner: TestCaseRunner):
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

        recording_media = []

        test_case_parsing_setup = TestCaseParsingSetup(
            space_separator_instruction_name_extractor,
            instruction_setup_with_setup_instructions(REGISTER_INSTRUCTION_NAME,
                                                      recording_media),
            ActPhaseParser())
        test_case_handling_setup = test_case_handling_setup_with_identity_preprocessor()

        test_suite_definition = test_suite_definition_without_instructions()
        # ACT #
        with tmp_dir_as_cwd(suite_and_case_files):
            actual_result = test_case_runner.run(test_case_parsing_setup,
                                                 test_case_handling_setup,
                                                 test_suite_definition,
                                                 case_file.name_as_path,
                                                 suite_file.name_as_path)
        # ASSERT #

        self.assertEqual(exit_values.EXECUTION__PASS.exit_code,
                         actual_result.exitcode,
                         'Sanity check of result indicator')

        recordings = list(map(Recording.string.fget, recording_media))
        self.assertEqual(expected_instruction_recording,
                         recordings)
