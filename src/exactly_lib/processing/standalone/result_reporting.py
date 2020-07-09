from typing import Optional, Callable

from exactly_lib.common import process_result_reporter
from exactly_lib.common import result_reporting as reporting
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.process_result_reporter import Environment, ProcessResultReporter
from exactly_lib.common.process_result_reporters import ProcessResultReporterWithInitialExitValueOutput
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.processing import test_case_processing, exit_values
from exactly_lib.processing.standalone.settings import ReportingOption
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


class ResultReporter:
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def __init__(self, reporting_environment: process_result_reporter.Environment):
        self._reporting_environment = reporting_environment


class TestSuiteParseErrorReporter(ResultReporter):
    def report(self, ex: SuiteParseError) -> int:
        file_printers = self._reporting_environment.std_file_printers
        from exactly_lib.test_suite import error_reporting
        return error_reporting.report_suite_parse_error(ex,
                                                        file_printers.out,
                                                        file_printers.err)


class TestCaseResultReporter(ResultReporter):
    def report(self, result: test_case_processing.Result) -> int:
        exit_value = exit_values.from_result(result)
        if result.status is test_case_processing.Status.EXECUTED:
            return self._report_execution(exit_value, result.execution_result)
        else:
            return self.__report_unable_to_execute(exit_value,
                                                   result.error_info)

    def depends_on_result_in_sandbox(self) -> bool:
        raise NotImplementedError('abstract method')

    def _exit_identifier_printer(self) -> ProcOutputFile:
        raise NotImplementedError('abstract method')

    def execute_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        return None

    def _process_reporter_with_exit_value_output(self,
                                                 exit_value: ExitValue,
                                                 output_rest: Callable[[Environment], None]) -> ProcessResultReporter:
        return ProcessResultReporterWithInitialExitValueOutput(
            exit_value,
            self._exit_identifier_printer(),
            output_rest,
        )

    def _report_with_exit_value_output(self,
                                       exit_value: ExitValue,
                                       output_rest: Callable[[Environment], None]) -> int:
        reporter = self._process_reporter_with_exit_value_output(exit_value, output_rest)
        return reporter.report(self._reporting_environment)

    def _report_execution(self,
                          exit_value: ExitValue,
                          result: FullExeResult) -> int:
        raise NotImplementedError('abstract method')

    def _report_full_exe_result(self,
                                exit_value: ExitValue,
                                result: FullExeResult) -> int:
        def output_rest(reporting_environment: Environment):
            reporting.print_error_message_for_full_result(reporting_environment.std_file_printers.err,
                                                          result)

        return self._report_with_exit_value_output(exit_value, output_rest)

    def __report_unable_to_execute(self,
                                   exit_value: ExitValue,
                                   error_info: ErrorInfo) -> int:
        reporter = reporter_of_unable_to_execute(
            self._exit_identifier_printer(),
            exit_value,
            error_info,
        )

        return reporter.report(self._reporting_environment)


def reporter_of_unable_to_execute(
        exit_value_printer: ProcOutputFile,
        exit_value: ExitValue,
        error_info: ErrorInfo) -> ProcessResultReporter:
    def output_rest(reporting_environment: Environment):
        reporting.print_error_info(reporting_environment.std_file_printers.err,
                                   error_info)

    return ProcessResultReporterWithInitialExitValueOutput(
        exit_value,
        exit_value_printer,
        output_rest,
    )


class _ResultReporterForNormalOutput(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return False

    def _exit_identifier_printer(self) -> ProcOutputFile:
        return ProcOutputFile.STDOUT

    def _report_execution(self,
                          exit_value: ExitValue,
                          result: FullExeResult) -> int:
        return self._report_full_exe_result(exit_value, result)


class _ResultReporterForPreserveAndPrintSandboxDir(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return True

    def _exit_identifier_printer(self) -> ProcOutputFile:
        return ProcOutputFile.STDERR

    def _report_execution(self,
                          exit_value: ExitValue,
                          result: FullExeResult) -> int:
        if result.has_sds:
            self._reporting_environment.std_file_printers.out.write_line(str(result.sds.root_dir))

        return self._report_full_exe_result(exit_value, result)


class _ResultReporterForActPhaseOutput(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return False

    def _exit_identifier_printer(self) -> ProcOutputFile:
        return ProcOutputFile.STDERR

    def execute_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        return self._reporting_environment.std_files

    def _report_execution(self,
                          exit_value: ExitValue,
                          result: FullExeResult) -> int:
        return (
            result.action_to_check_outcome.exit_code
            if result.status in _FULL_EXECUTION__COMPLETE
            else self._report_full_exe_result(exit_value, result)
        )


RESULT_REPORTERS = {
    ReportingOption.STATUS_CODE: _ResultReporterForNormalOutput,
    ReportingOption.SANDBOX_DIRECTORY_STRUCTURE_ROOT: _ResultReporterForPreserveAndPrintSandboxDir,
    ReportingOption.ACT_PHASE_OUTPUT: _ResultReporterForActPhaseOutput,
}

_FULL_EXECUTION__COMPLETE = {FullExeResultStatus.PASS,
                             FullExeResultStatus.FAIL,
                             FullExeResultStatus.XPASS,
                             FullExeResultStatus.XFAIL,
                             }
