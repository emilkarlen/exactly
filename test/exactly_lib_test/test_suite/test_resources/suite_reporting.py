import enum
import pathlib

from exactly_lib.cli.cli_environment.exit_value import ExitValue
from exactly_lib.test_case import test_case_processing
from exactly_lib.test_case.test_case_doc import TestCase
from exactly_lib.test_case.test_case_processing import TestCaseSetup
from exactly_lib.test_suite import reporting, structure
from exactly_lib.util import std
from exactly_lib.util.std import FilePrinter


class ExecutionTracingReporterFactory(reporting.RootSuiteReporterFactory):
    def __init__(self):
        self.complete_suite_reporter = ExecutionTracingRootSuiteReporter()

    def new_reporter(self,
                     std_output_files: std.StdOutputFiles,
                     root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        return self.complete_suite_reporter


class ExecutionTracingRootSuiteReporter(reporting.RootSuiteReporter):
    VALID_SUITE_EXIT_CODE = 72
    INVALID_SUITE_EXIT_CODE = 87

    def __init__(self):
        self.sub_suite_reporters = []
        self.num_report_final_result_invocations = 0

    def new_sub_suite_reporter(self, sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        reporter = reporting.SubSuiteReporter(ExecutionTracingSubSuiteProgressReporter(sub_suite))
        self.sub_suite_reporters.append(reporter)
        return reporter

    def report_final_results_for_invalid_suite(self, text_output_file: FilePrinter) -> ExitValue:
        return ExitValue(self.INVALID_SUITE_EXIT_CODE, 'invalid suite')

    def report_final_results_for_valid_suite(self, text_output_file: FilePrinter) -> ExitValue:
        self.num_report_final_result_invocations += 1
        return ExitValue(self.VALID_SUITE_EXIT_CODE, 'valid suite')


class EventType(enum.Enum):
    """
    Type for tracking sequence of invocations of methods of SubSuiteReporter.
    """
    SUITE_BEGIN = 1
    CASE_BEGIN = 2
    CASE_END = 3
    SUITE_END = 4


class CaseEndInfo(tuple):
    def __new__(cls,
                case: TestCaseSetup,
                result: test_case_processing.Result):
        return tuple.__new__(cls, (case, result))

    @property
    def case(self) -> TestCaseSetup:
        return self[0]

    @property
    def result(self) -> test_case_processing.Result:
        return self[1]


class ExecutionTracingSubSuiteProgressReporter(reporting.SubSuiteProgressReporter):
    def __init__(self,
                 sub_suite: structure.TestSuite):
        self.sub_suite = sub_suite
        self.event_type_list = []
        self.case_begin_list = []
        self.case_end_list = []

    def suite_begin(self):
        self.event_type_list.append(EventType.SUITE_BEGIN)

    def suite_end(self):
        self.event_type_list.append(EventType.SUITE_END)

    def case_begin(self, case: TestCase):
        self.event_type_list.append(EventType.CASE_BEGIN)
        self.case_begin_list.append(case)

    def case_end(self,
                 case: TestCaseSetup,
                 result: test_case_processing.Result):
        self.event_type_list.append(EventType.CASE_END)
        self.case_end_list.append(CaseEndInfo(case, result))
