import pathlib
import tempfile
import unittest

from exactly_lib import program_info
from exactly_lib.default.program_modes import test_suite
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.processing import processors as case_processing
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case import os_services
from exactly_lib.test_suite.enumeration import DepthFirstEnumerator
from exactly_lib.test_suite.execution import Processor
from exactly_lib.test_suite.file_reading.suite_hierarchy_reading import Reader, Environment
from exactly_lib.util.file_utils import resolved_path
from exactly_lib_test.processing.test_resources.test_case_setup import instruction_set_with_no_instructions
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.files.str_std_out_files import null_output_files
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingProcessingReporter, \
    ExecutionTracingRootSuiteReporter


class Setup:
    def root_suite_based_at(self, root_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def file_structure_to_read(self, root_path: pathlib.Path) -> DirContents:
        raise NotImplementedError()

    def test_case_handling_setup(self) -> TestCaseHandlingSetup:
        raise NotImplementedError()

    def assertions(self,
                   put: unittest.TestCase,
                   reporter: ExecutionTracingRootSuiteReporter,
                   actual_exit_code: int):
        raise NotImplementedError()


def check(setup: Setup,
          put: unittest.TestCase):
    with tempfile.TemporaryDirectory(prefix=program_info.PROGRAM_NAME + '-test-') as tmp_dir:
        tmp_dir_path = resolved_path(tmp_dir)
        setup.file_structure_to_read(tmp_dir_path).write_to(tmp_dir_path)
        test_case_handling_setup = setup.test_case_handling_setup()
        suite_reading_environment = Environment(test_suite.new_parser(),
                                                _TEST_CASE_PARSING_SETUP,
                                                test_case_handling_setup)
        hierarchy_reader = Reader(suite_reading_environment)
        reporter = ExecutionTracingProcessingReporter()
        processor = Processor(_default_case_configuration(test_case_handling_setup),
                              hierarchy_reader,
                              reporter,
                              DepthFirstEnumerator(),
                              case_processing.new_processor_that_is_allowed_to_pollute_current_process)
        exit_code = processor.execute(setup.root_suite_based_at(tmp_dir_path), null_output_files())
        setup.assertions(put,
                         reporter.complete_suite_reporter,
                         exit_code)


def _default_case_configuration(test_case_handling_setup: TestCaseHandlingSetup) -> case_processing.Configuration:
    return case_processing.Configuration(_DEFAULT_TEST_CASE_DEFINITION,
                                         test_case_handling_setup,
                                         os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                                         False)


def white_space_name_and_argument_splitter(s: str) -> str:
    return s.split()[0]


INSTRUCTION_SETUP = instruction_set_with_no_instructions()

_TEST_CASE_PARSING_SETUP = TestCaseParsingSetup(white_space_name_and_argument_splitter,
                                                INSTRUCTION_SETUP,
                                                ActPhaseParser())

_DEFAULT_TEST_CASE_DEFINITION = TestCaseDefinition(_TEST_CASE_PARSING_SETUP,
                                                   PredefinedProperties({}),
                                                   )
