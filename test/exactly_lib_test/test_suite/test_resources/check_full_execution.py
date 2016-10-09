import pathlib
import tempfile
import unittest

from exactly_lib import program_info
from exactly_lib.processing import processors as case_processing
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_case.instruction_setup import InstructionsSetup
from exactly_lib.test_suite.enumeration import DepthFirstEnumerator
from exactly_lib.test_suite.execution import Executor
from exactly_lib.test_suite.suite_hierarchy_reading import Reader, Environment
from exactly_lib.util.file_utils import resolved_path
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.str_std_out_files import null_output_files
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingReporterFactory, \
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
        suite_reading_environment = Environment(test_case_handling_setup.preprocessor,
                                                test_case_handling_setup.default_act_phase_setup)
        hierarchy_reader = Reader(suite_reading_environment)
        reporter_factory = ExecutionTracingReporterFactory()
        executor = Executor(_default_case_configuration(test_case_handling_setup),
                            null_output_files(),
                            hierarchy_reader,
                            reporter_factory,
                            DepthFirstEnumerator(),
                            case_processing.new_processor_that_is_allowed_to_pollute_current_process,
                            setup.root_suite_based_at(tmp_dir_path))
        exit_code = executor.execute()
        setup.assertions(put,
                         reporter_factory.complete_suite_reporter,
                         exit_code)


def _default_case_configuration(test_case_handling_setup: TestCaseHandlingSetup) -> case_processing.Configuration:
    return case_processing.Configuration(white_space_name_and_argument_splitter,
                                         INSTRUCTION_SETUP,
                                         test_case_handling_setup,
                                         False)


def white_space_name_and_argument_splitter(s: str) -> list:
    return s.strip().split()


INSTRUCTION_SETUP = InstructionsSetup(
    {},
    {},
    {},
    {},
    {})
