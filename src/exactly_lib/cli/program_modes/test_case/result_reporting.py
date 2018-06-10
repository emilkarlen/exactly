import pathlib
import shutil

from exactly_lib.cli.program_modes.test_case.settings import ReportingOption
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.result_reporting import print_error_message_for_full_result, print_error_info
from exactly_lib.execution.full_execution.result import FullResultStatus, FullResult
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

    def handle(self, result: FullResult):
        status = result.status
        if status in _FULL_EXECUTION__SKIPPED:
            return self.skipped(result)
        elif status in _FULL_EXECUTION__VALIDATE:
            return self.validation(result)
        elif status in _FULL_EXECUTION__COMPLETE:
            return self.complete(result)
        else:
            return self.hard_error_or_implementation_error(result)

    def complete(self, result: FullResult) -> int:
        raise NotImplementedError('abstract method')

    def skipped(self, result: FullResult) -> int:
        return self._default_non_complete_execution(result)

    def validation(self, result: FullResult) -> int:
        return self._default_non_complete_execution(result)

    def hard_error_or_implementation_error(self, result: FullResult) -> int:
        return self._default_non_complete_execution(result)

    def _default_non_complete_execution(self, result: FullResult) -> int:
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

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: FullResult) -> int:
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
                              result: FullResult) -> int:
        self._out_printer.write_colored_line(result.status.name,
                                             exit_value.color)
        print_error_message_for_full_result(self._err_printer, result)
        return exit_value.exit_code


class _ResultReporterForPreserveAndPrintSandboxDir(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return True

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: FullResult) -> int:
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
    def complete(self, result: FullResult) -> int:
        def copy_file(input_file_path: pathlib.Path,
                      output_file):
            with input_file_path.open() as f:
                for data in f:
                    output_file.write(data)

        copy_file(result.sds.result.stdout_file, self._std.out)
        copy_file(result.sds.result.stderr_file, self._std.err)
        exit_code = result.action_to_check_outcome.exit_code
        shutil.rmtree(str(result.sds.root_dir))
        return exit_code


class _ResultReporterForActPhaseOutput(TestCaseResultReporter):
    def depends_on_result_in_sandbox(self) -> bool:
        return True

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: FullResult) -> int:
        handler = _FullExecutionHandlerForActPhaseOutput(exit_value,
                                                         self._std,
                                                         self._out_printer,
                                                         self._err_printer)
        return handler.handle(result)


RESULT_REPORTERS = {
    ReportingOption.STATUS_CODE: _ResultReporterForNormalOutput,
    ReportingOption.SANDBOX_DIRECTORY_STRUCTURE_ROOT: _ResultReporterForPreserveAndPrintSandboxDir,
    ReportingOption.ACT_PHASE_OUTPUT: _ResultReporterForActPhaseOutput,
}

_FULL_EXECUTION__SKIPPED = {FullResultStatus.SKIPPED}

_FULL_EXECUTION__VALIDATE = {FullResultStatus.VALIDATION_ERROR}

_FULL_EXECUTION__COMPLETE = {FullResultStatus.PASS,
                             FullResultStatus.FAIL,
                             FullResultStatus.XPASS,
                             FullResultStatus.XFAIL,
                             }
