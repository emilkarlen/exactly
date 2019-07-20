from typing import Optional

from exactly_lib.common import result_reporting as reporting
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.processing import test_case_processing, exit_values
from exactly_lib.processing.standalone.settings import ReportingOption
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.test_suite.file_reading.exception import SuiteParseError
from exactly_lib.util.file_printer import FilePrinter, file_printer_with_color_if_terminal
from exactly_lib.util.std import StdOutputFiles


class ResultReporter:
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def __init__(self, output_files: StdOutputFiles):
        self._std = output_files
        self._out_printer = file_printer_with_color_if_terminal(output_files.out)
        self._err_printer = file_printer_with_color_if_terminal(output_files.err)


class TestSuiteParseErrorReporter(ResultReporter):
    def report(self, ex: SuiteParseError) -> int:
        from exactly_lib.test_suite import error_reporting
        return error_reporting.report_suite_parse_error(ex,
                                                        self._out_printer,
                                                        self._err_printer)


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

    def _exit_identifier_printer(self) -> FilePrinter:
        raise NotImplementedError('abstract method')

    def execute_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        return None

    def _report_execution(self,
                          exit_value: ExitValue,
                          result: FullExeResult) -> int:
        raise NotImplementedError('abstract method')

    def _report_full_exe_result(self,
                                exit_value: ExitValue,
                                result: FullExeResult) -> int:
        self._exit_identifier_printer().write_colored_line(exit_value.exit_identifier,
                                                           exit_value.color)
        reporting.print_error_message_for_full_result(self._err_printer, result)
        return exit_value.exit_code

    def __report_unable_to_execute(self,
                                   exit_value: ExitValue,
                                   error_info: ErrorInfo) -> int:
        self._exit_identifier_printer().write_colored_line(exit_value.exit_identifier,
                                                           exit_value.color)
        reporting.print_error_info(self._err_printer, error_info)
        return exit_value.exit_code


class _ResultReporterForNormalOutput(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return False

    def _exit_identifier_printer(self) -> FilePrinter:
        return self._out_printer

    def _report_execution(self,
                          exit_value: ExitValue,
                          result: FullExeResult) -> int:
        return self._report_full_exe_result(exit_value, result)


class _ResultReporterForPreserveAndPrintSandboxDir(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return True

    def _exit_identifier_printer(self) -> FilePrinter:
        return self._err_printer

    def _report_execution(self,
                          exit_value: ExitValue,
                          result: FullExeResult) -> int:
        if result.has_sds:
            self._out_printer.write_line(str(result.sds.root_dir))

        return self._report_full_exe_result(exit_value, result)


class _ResultReporterForActPhaseOutput(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return False

    def _exit_identifier_printer(self) -> FilePrinter:
        return self._err_printer

    def execute_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        return self._std

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
