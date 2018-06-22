from typing import Optional

from exactly_lib.cli.program_modes.test_case.settings import ReportingOption
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.result_reporting import print_error_message_for_full_result, print_error_info
from exactly_lib.execution.full_execution.result import FullExeResultStatus, FullExeResult
from exactly_lib.processing import test_case_processing, exit_values
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.test_suite.instruction_set.parse import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles, FilePrinter, file_printer_with_color_if_terminal


class _FullExecutionHandler:
    """Helper class for handling some different cases of result of test case execution."""

    def __init__(self,
                 exit_value: ExitValue,
                 output_files: StdOutputFiles,
                 out_printer: FilePrinter,
                 err_printer: FilePrinter,
                 ):
        self.exit_value = exit_value
        self._std = output_files
        self._out_printer = FilePrinter(output_files.out)
        self._err_printer = FilePrinter(output_files.err)
        self._out_printer = out_printer
        self._err_printer = err_printer

    def handle(self, result: FullExeResult):
        status = result.status
        if status in _FULL_EXECUTION__SKIPPED:
            return self.skipped(result)
        elif status in _FULL_EXECUTION__VALIDATE:
            return self.validation(result)
        elif status in _FULL_EXECUTION__COMPLETE:
            return self.complete(result)
        else:
            return self.hard_error_or_implementation_error(result)

    def complete(self, result: FullExeResult) -> int:
        raise NotImplementedError('abstract method')

    def skipped(self, result: FullExeResult) -> int:
        return self._default_non_complete_execution(result)

    def validation(self, result: FullExeResult) -> int:
        return self._default_non_complete_execution(result)

    def hard_error_or_implementation_error(self, result: FullExeResult) -> int:
        return self._default_non_complete_execution(result)

    def _default_non_complete_execution(self, result: FullExeResult) -> int:
        self._out_printer.write_line(result.status.name)
        print_error_message_for_full_result(self._err_printer, result)
        return self.exit_value.exit_code


class ResultReporter:
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def __init__(self, output_files: StdOutputFiles):
        self._std = output_files
        self._out_printer = file_printer_with_color_if_terminal(output_files.out)
        self._err_printer = file_printer_with_color_if_terminal(output_files.err)


class TestSuiteSyntaxErrorReporter(ResultReporter):
    def report(self, ex: SuiteSyntaxError) -> int:
        from exactly_lib.test_suite.error_reporting import report_suite_read_error
        return report_suite_read_error(ex,
                                       self._out_printer,
                                       self._err_printer,
                                       exit_values.NO_EXECUTION__SYNTAX_ERROR)


class TestCaseResultReporter(ResultReporter):
    def report(self, result: test_case_processing.Result) -> int:
        exit_value = exit_values.from_result(result)
        if result.status is test_case_processing.Status.EXECUTED:
            return self.report_full_execution(exit_value, result.execution_result)
        else:
            return self._report_unable_to_execute(exit_value,
                                                  result.error_info)

    def depends_on_result_in_sandbox(self) -> bool:
        raise NotImplementedError('abstract method')

    def execute_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        return None

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: FullExeResult) -> int:
        raise NotImplementedError('abstract method')

    def _report_unable_to_execute(self,
                                  exit_value: ExitValue,
                                  error_info: ErrorInfo) -> int:
        self._out_printer.write_colored_line(exit_value.exit_identifier, exit_value.color)
        print_error_info(self._err_printer, error_info)
        return exit_value.exit_code


class _ResultReporterForNormalOutput(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return False

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: FullExeResult) -> int:
        self._out_printer.write_colored_line(result.status.name,
                                             exit_value.color)
        print_error_message_for_full_result(self._err_printer, result)
        return exit_value.exit_code


class _ResultReporterForPreserveAndPrintSandboxDir(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return True

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: FullExeResult) -> int:
        if result.has_sds:
            self._out_printer.write_line(str(result.sds.root_dir))

        self._err_printer.write_colored_line(exit_value.exit_identifier, exit_value.color)
        print_error_message_for_full_result(self._err_printer, result)

        return exit_value.exit_code

    def _report_unable_to_execute(self,
                                  exit_value: ExitValue,
                                  error_info: ErrorInfo) -> int:
        self._err_printer.write_colored_line(exit_value.exit_identifier, exit_value.color)
        print_error_info(self._err_printer, error_info)
        return exit_value.exit_code


class _FullExecutionHandlerForActPhaseOutput(_FullExecutionHandler):
    def complete(self, result: FullExeResult) -> int:
        return result.action_to_check_outcome.exit_code

    def _default_non_complete_execution(self, result: FullExeResult) -> int:
        self._err_printer.write_colored_line(self.exit_value.exit_identifier, self.exit_value.color)
        print_error_message_for_full_result(self._err_printer, result)
        return self.exit_value.exit_code


class _ResultReporterForActPhaseOutput(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return False

    def execute_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        return self._std

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: FullExeResult) -> int:
        handler = _FullExecutionHandlerForActPhaseOutput(exit_value,
                                                         self._std,
                                                         self._out_printer,
                                                         self._err_printer)
        return handler.handle(result)

    def _report_unable_to_execute(self,
                                  exit_value: ExitValue,
                                  error_info: ErrorInfo) -> int:
        self._err_printer.write_colored_line(exit_value.exit_identifier, exit_value.color)
        print_error_info(self._err_printer, error_info)
        return exit_value.exit_code


RESULT_REPORTERS = {
    ReportingOption.STATUS_CODE: _ResultReporterForNormalOutput,
    ReportingOption.SANDBOX_DIRECTORY_STRUCTURE_ROOT: _ResultReporterForPreserveAndPrintSandboxDir,
    ReportingOption.ACT_PHASE_OUTPUT: _ResultReporterForActPhaseOutput,
}

_FULL_EXECUTION__SKIPPED = {FullExeResultStatus.SKIPPED}

_FULL_EXECUTION__VALIDATE = {FullExeResultStatus.VALIDATION_ERROR}

_FULL_EXECUTION__COMPLETE = {FullExeResultStatus.PASS,
                             FullExeResultStatus.FAIL,
                             FullExeResultStatus.XPASS,
                             FullExeResultStatus.XFAIL,
                             }
