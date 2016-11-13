import pathlib

from exactly_lib.common.exit_value import ExitValue
from exactly_lib.processing import test_case_processing
from exactly_lib.util.std import StdOutputFiles, FilePrinter
from . import structure


class SubSuiteProgressReporter:
    """
    A listener that may reports the progress of the execution of the test cases
    in a single suite (TestSuite).
    """

    def suite_begin(self):
        raise NotImplementedError()

    def suite_end(self):
        raise NotImplementedError()

    def case_begin(self,
                   case: test_case_processing.TestCaseSetup):
        raise NotImplementedError()

    def case_end(self,
                 case: test_case_processing.TestCaseSetup,
                 result: test_case_processing.Result):
        raise NotImplementedError()


class SubSuiteReporter:
    def __init__(self,
                 listener: SubSuiteProgressReporter):
        self._listener = listener
        self._result = []

    def listener(self) -> SubSuiteProgressReporter:
        return self._listener

    def case_end(self,
                 case: test_case_processing.TestCaseSetup,
                 result: test_case_processing.Result):
        self._result.append((case, result))

    def result(self) -> list:
        """
        :rtype: [(TestCaseSetup, test_case_processing.Result)]
        """
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
                               sub_suite: structure.TestSuite) -> SubSuiteReporter:
        raise NotImplementedError()

    def report_final_results(self, text_output_file: FilePrinter) -> ExitValue:
        """
        Gives the number that shall be the exit code of the main program.
        Called after all sub suites have been executed and reported.
        :return: The exit code from the main program.
        """
        raise NotImplementedError()


class RootSuiteReporterFactory:
    def new_reporter(self,
                     std_output_files: StdOutputFiles,
                     root_suite_file: pathlib.Path) -> RootSuiteReporter:
        raise NotImplementedError()
