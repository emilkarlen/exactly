import enum
import pathlib
from typing import List

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.test_case_processing import TestCaseFileReference
from exactly_lib.test_case.test_case_doc import TestCase
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite.reporting import TestCaseProcessingInfo
from exactly_lib.test_suite.structure import TestSuiteHierarchy
from exactly_lib.util import std
from exactly_lib.util.std import StdOutputFiles


class ExecutionTracingProcessingReporter(reporting.RootSuiteProcessingReporter):
    def __init__(self):
        self.complete_suite_reporter = ExecutionTracingRootSuiteReporter()
        self._report_invalid_suite_invocations = []

    def report_invalid_suite(self,
                             exit_value: ExitValue,
                             output: StdOutputFiles,
                             ):
        self._report_invalid_suite_invocations.append(exit_value)

    def execution_reporter(self,
                           root_suite: TestSuiteHierarchy,
                           std_output_files: std.StdOutputFiles,
                           root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        return self.complete_suite_reporter

    @property
    def report_invalid_suite_invocations(self) -> List[ExitValue]:
        return self._report_invalid_suite_invocations


class ProcessingReporterThatDoesNothing(reporting.RootSuiteProcessingReporter):
    VALID_SUITE_EXIT_CODE = -1

    def report_invalid_suite(self,
                             exit_value: ExitValue,
                             output: StdOutputFiles,
                             ):
        pass

    def execution_reporter(self,
                           root_suite: TestSuiteHierarchy,
                           std_output_files: std.StdOutputFiles,
                           root_suite_file: pathlib.Path) -> reporting.RootSuiteReporter:
        return RootSuiteReporterThatDoesNothing()


class ExecutionTracingRootSuiteReporter(reporting.RootSuiteReporter):
    VALID_SUITE_EXIT_CODE = 72

    def __init__(self):
        self.sub_suite_reporters = []
        self.num_report_final_result_invocations = 0

    def new_sub_suite_reporter(self, sub_suite: TestSuiteHierarchy) -> reporting.SubSuiteReporter:
        reporter = reporting.SubSuiteReporter(sub_suite, ExecutionTracingSubSuiteProgressReporter(sub_suite))
        self.sub_suite_reporters.append(reporter)
        return reporter

    def report_final_results(self) -> int:
        self.num_report_final_result_invocations += 1
        return self.VALID_SUITE_EXIT_CODE


class RootSuiteReporterThatDoesNothing(reporting.RootSuiteReporter):
    def new_sub_suite_reporter(self, sub_suite: TestSuiteHierarchy) -> reporting.SubSuiteReporter:
        return reporting.SubSuiteReporter(sub_suite, SubSuiteProgressReporterThatDoesNothing())

    def report_final_results(self) -> int:
        return ProcessingReporterThatDoesNothing.VALID_SUITE_EXIT_CODE


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
                case: TestCaseFileReference,
                result: test_case_processing.Result):
        return tuple.__new__(cls, (case, result))

    @property
    def case(self) -> TestCaseFileReference:
        return self[0]

    @property
    def result(self) -> test_case_processing.Result:
        return self[1]


class ExecutionTracingSubSuiteProgressReporter(reporting.SubSuiteProgressReporter):
    def __init__(self, sub_suite: TestSuiteHierarchy):
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
                 case: TestCaseFileReference,
                 processing_info: TestCaseProcessingInfo):
        self.event_type_list.append(EventType.CASE_END)
        self.case_end_list.append(CaseEndInfo(case, processing_info.result))


class SubSuiteProgressReporterThatDoesNothing(reporting.SubSuiteProgressReporter):
    def suite_begin(self):
        pass

    def suite_end(self):
        pass

    def case_begin(self, case: TestCase):
        pass

    def case_end(self,
                 case: TestCaseFileReference,
                 processing_info: TestCaseProcessingInfo):
        pass
