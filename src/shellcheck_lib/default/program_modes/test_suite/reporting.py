import os

from shellcheck_lib.cli.cli_environment.program_modes.test_suite import exit_values
from shellcheck_lib.execution.result import FullResultStatus
from shellcheck_lib.test_case import test_case_processing
from shellcheck_lib.test_case.test_case_processing import Status
from shellcheck_lib.test_suite import reporting, structure
from shellcheck_lib.util.std import StdOutputFiles

SUCCESS_STATUSES = {FullResultStatus.PASS,
                    FullResultStatus.SKIPPED,
                    FullResultStatus.XFAIL
                    }


class DefaultSubSuiteProgressReporter(reporting.SubSuiteProgressReporter):
    def __init__(self,
                 output_file,
                 suite: structure.TestSuite):
        self.output_file = output_file
        self.suite = suite

    def suite_begin(self):
        self._write_ln('SUITE ' + str(self.suite.source_file) + ': BEGIN')

    def suite_end(self):
        self._write_ln('SUITE ' + str(self.suite.source_file) + ': END')

    def case_begin(self, case: test_case_processing.TestCaseSetup):
        self.output_file.write('CASE  ' + str(case.file_path) + ': ')

    def case_end(self,
                 case: test_case_processing.TestCaseSetup,
                 result: test_case_processing.Result):
        if result.status is not test_case_processing.Status.EXECUTED:
            if result.status is test_case_processing.Status.INTERNAL_ERROR:
                self._write_ln(result.status.name)
            else:
                self._write_ln(result.access_error_type.name)
        else:
            status = result.execution_result.status
            self._write_ln(status.name)

    def _write_ln(self, s: str):
        self.output_file.write(s)
        self.output_file.write(os.linesep)


class DefaultRootSuiteReporterFactory(reporting.RootSuiteReporterFactory):
    def new_reporter(self,
                     std_output_files: StdOutputFiles) -> reporting.RootSuiteReporter:
        return DefaultRootSuiteReporter(std_output_files)


class DefaultRootSuiteReporter(reporting.RootSuiteReporter):
    def __init__(self,
                 std_output_files: StdOutputFiles):
        self._line_printer = std_output_files.out
        self._sub_reporters = []

    def new_sub_suite_reporter(self,
                               sub_suite: structure.TestSuite) -> reporting.SubSuiteReporter:
        reporter = reporting.SubSuiteReporter(DefaultSubSuiteProgressReporter(self._line_printer, sub_suite))
        self._sub_reporters.append(reporter)
        return reporter

    def report_final_results_for_invalid_suite(self) -> int:
        return self._print_and_return_exit_code(exit_values.INVALID_SUITE)

    def report_final_results_for_valid_suite(self) -> int:
        exit_value = self._valid_suite_exit_value()
        return self._print_and_return_exit_code(exit_value)

    def _valid_suite_exit_value(self) -> exit_values.ExitValue:
        for suite_reporter in self._sub_reporters:
            assert isinstance(suite_reporter, reporting.SubSuiteReporter)
            for case, result in suite_reporter.result():
                if result.status is not Status.EXECUTED:
                    return exit_values.FAILED_TESTS
                if result.execution_result.status not in SUCCESS_STATUSES:
                    return exit_values.FAILED_TESTS
        return exit_values.ALL_PASS

    def _print_and_return_exit_code(self, exit_value: exit_values.ExitValue) -> int:
        self._line_printer.write(os.linesep)
        self._line_printer.write(exit_value.exit_identifier)
        self._line_printer.write(os.linesep)
        return exit_value.exit_code
