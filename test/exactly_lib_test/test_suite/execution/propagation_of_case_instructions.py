import pathlib
import unittest
from typing import List

from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.full_execution.configuration import PredefinedProperties
from exactly_lib.processing import processors
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.test_case import os_services
from exactly_lib.test_suite import enumeration
from exactly_lib.test_suite import execution as sut
from exactly_lib.test_suite import suite_hierarchy_reading
from exactly_lib.test_suite.execution import TestCaseProcessorConstructor
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.section_document.test_resources.element_parsers import SectionElementParserThatRaisesSourceError
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_suite.execution.test_resources import instruction_name_extractor, instruction_setup
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    test_case_handling_setup_with_identity_preprocessor
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingReporterFactory, \
    ExecutionTracingRootSuiteReporter


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


REGISTER_INSTRUCTION_NAME = 'register'

SETUP_INSTRUCTION_IN_CONTAINING_SUITE = 'containing suite'
SETUP_INSTRUCTION_IN_CASE_1 = 'case 1'
SETUP_INSTRUCTION_IN_CASE_2 = 'case 2'

CASE_THAT_REGISTERS_MARKER = """\
[setup]

register {marker}
"""

CASE_1_FILE = File('1.case',
                   CASE_THAT_REGISTERS_MARKER.format(marker=SETUP_INSTRUCTION_IN_CASE_1))

CASE_2_FILE = File('2.case',
                   CASE_THAT_REGISTERS_MARKER.format(marker=SETUP_INSTRUCTION_IN_CASE_2))

SUITE_WITH_CASES = """\
[cases]

{case_1_file}
{case_2_file}

[setup]

register {marker}
""".format(
    marker=SETUP_INSTRUCTION_IN_CONTAINING_SUITE,
    case_1_file=CASE_1_FILE.file_name,
    case_2_file=CASE_2_FILE.file_name,
)

SUITE_WITH_SETUP_BUT_WITH_JUST_A_SUITE = """\
[setup]

register {marker}

[suites]

{sub_suite_file_name}
"""


class Test(unittest.TestCase):
    def test_setup_instructions_in_containing_suite_SHOULD_be_executed_first_in_each_case(self):
        # ARRANGE #

        containing_suite_file = File('test.suite', SUITE_WITH_CASES)
        suite_and_case_files = DirContents([
            containing_suite_file,
            CASE_1_FILE,
            CASE_2_FILE,
        ])

        expected_instruction_recording = [
            # First test case
            SETUP_INSTRUCTION_IN_CONTAINING_SUITE,
            SETUP_INSTRUCTION_IN_CASE_1,

            # Second test case
            SETUP_INSTRUCTION_IN_CONTAINING_SUITE,
            SETUP_INSTRUCTION_IN_CASE_2,
        ]

        case_processors = [
            NameAndValue('processor_that_should_not_pollute_current_process',
                         processors.new_processor_that_should_not_pollute_current_process),
            NameAndValue('processor_that_is_allowed_to_pollute_current_process',
                         processors.new_processor_that_is_allowed_to_pollute_current_process),
        ]
        with tmp_dir(suite_and_case_files) as tmp_dir_path:
            suite_file_path = tmp_dir_path / containing_suite_file.file_name

            for case_processor_case in case_processors:
                with self.subTest(case_processor_case.name):
                    recorder = []
                    executor = new_executor(recorder,
                                            case_processor_case.value,
                                            suite_file_path)
                    # ACT #

                    return_value = executor.execute()

                    # ASSERT #

                    self.assertEqual(ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                     return_value,
                                     'Sanity check of result indicator')
                    self.assertEqual(expected_instruction_recording,
                                     recorder)

    def test_setup_instructions_in_non_containing_suite_SHOULD_not_be_executed_in_any_case(self):
        # ARRANGE #

        containing_suite_file = File('sub.suite', SUITE_WITH_CASES)
        non_containing_suite_file = File('main.suite',
                                         SUITE_WITH_SETUP_BUT_WITH_JUST_A_SUITE.format(
                                             marker='setup instruction that should not be executed',
                                             sub_suite_file_name=containing_suite_file.file_name,
                                         ))

        suite_and_case_files = DirContents([
            non_containing_suite_file,
            containing_suite_file,
            CASE_1_FILE,
            CASE_2_FILE,
        ])

        expected_instruction_recording = [
            # First test case
            SETUP_INSTRUCTION_IN_CONTAINING_SUITE,
            SETUP_INSTRUCTION_IN_CASE_1,

            # Second test case
            SETUP_INSTRUCTION_IN_CONTAINING_SUITE,
            SETUP_INSTRUCTION_IN_CASE_2,
        ]

        case_processors = [
            NameAndValue('processor_that_should_not_pollute_current_process',
                         processors.new_processor_that_should_not_pollute_current_process),
            NameAndValue('processor_that_is_allowed_to_pollute_current_process',
                         processors.new_processor_that_is_allowed_to_pollute_current_process),
        ]
        with tmp_dir(suite_and_case_files) as tmp_dir_path:
            suite_file_path = tmp_dir_path / containing_suite_file.file_name

            for case_processor_case in case_processors:
                with self.subTest(case_processor_case.name):
                    recorder = []
                    executor = new_executor(recorder,
                                            case_processor_case.value,
                                            suite_file_path)
                    # ACT #

                    return_value = executor.execute()

                    # ASSERT #

                    self.assertEqual(ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                     return_value,
                                     'Sanity check of result indicator')
                    self.assertEqual(expected_instruction_recording,
                                     recorder)


def new_executor(recorder: List[str],
                 test_case_processor_constructor: TestCaseProcessorConstructor,
                 suite_root_file_path: pathlib.Path) -> sut.Executor:
    test_case_definition = TestCaseDefinition(
        TestCaseParsingSetup(instruction_name_extractor,
                             instruction_setup(REGISTER_INSTRUCTION_NAME, recorder),
                             ActPhaseParser()),
        PredefinedProperties(empty_symbol_table()))
    default_configuration = processors.Configuration(test_case_definition,
                                                     test_case_handling_setup_with_identity_preprocessor(),
                                                     os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                                                     False,
                                                     sandbox_dir_resolving.mk_tmp_dir_with_prefix('test-suite-'))

    return sut.Executor(default_configuration,
                        StringStdOutFiles().stdout_files,
                        suite_hierarchy_reading.Reader(
                            suite_hierarchy_reading.Environment(
                                SectionElementParserThatRaisesSourceError(),
                                test_case_definition.parsing_setup,
                                default_configuration.default_handling_setup)
                        ),
                        ExecutionTracingReporterFactory(),
                        enumeration.DepthFirstEnumerator(),
                        test_case_processor_constructor,
                        suite_root_file_path,
                        )
