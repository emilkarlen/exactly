import datetime
import pathlib
from typing import Tuple, List

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.process_result_reporter import Environment
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.test_case_processing import TestCaseFileReference
from . import structure


class TestCaseProcessingInfo(tuple):
    def __new__(cls,
                result: test_case_processing.Result,
                duration: datetime.timedelta):
        return tuple.__new__(cls, (result, duration))

    @property
    def result(self) -> test_case_processing.Result:
        return self[0]

    @property
    def duration(self) -> datetime.timedelta:
        return self[1]


class SubSuiteProgressReporter:
    """
    An object that receives test case execution events and may report these to the user.
    """

    def suite_begin(self):
        """
        Called once.
        """
        raise NotImplementedError()

    def suite_end(self):
        """
        Called once.
        """
        raise NotImplementedError()

    def case_begin(self,
                   case: test_case_processing.TestCaseFileReference):
        raise NotImplementedError()

    def case_end(self,
                 case: test_case_processing.TestCaseFileReference,
                 processing_info: TestCaseProcessingInfo):
        raise NotImplementedError()


class SubSuiteReporter:
    def __init__(self,
                 suite: structure.TestSuiteHierarchy,
                 listener: SubSuiteProgressReporter):
        self._suite = suite
        self._listener = listener
        self._result = []
        self._start_time = datetime.datetime.now()

    @property
    def progress_reporter(self) -> SubSuiteProgressReporter:
        return self._listener

    def case_end(self,
                 case: test_case_processing.TestCaseFileReference,
                 execution_info: TestCaseProcessingInfo):
        self._result.append((case, execution_info))

    @property
    def suite(self) -> structure.TestSuiteHierarchy:
        return self._suite

    @property
    def start_time(self) -> datetime.datetime:
        return self._start_time

    def result(self) -> List[Tuple[TestCaseFileReference, TestCaseProcessingInfo]]:
        return self._result


class RootSuiteReporter:
    """
    Reports the test process to the outside world.
    """

    def root_suite_begin(self):
        pass

    def root_suite_end(self):
        pass

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuiteHierarchy) -> SubSuiteReporter:
        raise NotImplementedError()

    def report_final_results(self) -> int:
        """
        Gives the number that shall be the exit code of the main program.
        Called after all sub suites have been executed and reported.
        :return: The exit code from the main program.
        """
        raise NotImplementedError()


class RootSuiteProcessingReporter:
    def report_invalid_suite(self,
                             exit_value: ExitValue,
                             reporting_environment: Environment,
                             ):
        raise NotImplementedError('abstract method')

    def execution_reporter(self,
                           root_suite: structure.TestSuiteHierarchy,
                           reporting_environment: Environment,
                           root_suite_file: pathlib.Path) -> RootSuiteReporter:
        raise NotImplementedError()
