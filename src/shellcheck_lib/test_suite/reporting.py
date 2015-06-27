from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib.test_case import test_case_processing
from . import structure


class SubSuiteReporter:
    def suite_begin(self):
        raise NotImplementedError()

    def suite_end(self):
        raise NotImplementedError()

    def case_begin(self,
                   case: structure.TestCase):
        raise NotImplementedError()

    def case_end(self,
                 case: structure.TestCase,
                 result: test_case_processing.Result):
        raise NotImplementedError()


class CompleteSuiteReporter:
    """
    Reports the test process to the outside world.
    """

    def invalid_suite_exit_code(self) -> int:
        """
        Executed iff the suite is invalid, so that no test cases can be executed.
        Note that this does not include invalid test cases, since these should not
        prevent other test cases from being executed.
        :return: The exit code of the main program.
        """
        raise NotImplementedError()

    def valid_suite_exit_code(self) -> int:
        """
        Gives the number that shall be the exit code of the main program.
        Called after the whole suite has been executed and reported.
        :return: An integer in [0, 255]
        """
        raise NotImplementedError()

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuite) -> SubSuiteReporter:
        raise NotImplementedError()


class ReporterFactory:
    def new_reporter(self,
                     std_output_files: StdOutputFiles) -> CompleteSuiteReporter:
        raise NotImplementedError()
