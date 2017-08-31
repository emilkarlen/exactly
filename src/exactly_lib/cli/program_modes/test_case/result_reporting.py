import pathlib
import shutil

from exactly_lib.cli.program_modes.test_case.settings import Output
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.execution import full_execution
from exactly_lib.execution.result_reporting import print_error_message_for_full_result, print_error_info
from exactly_lib.processing import test_case_processing, exit_values
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.util.std import StdOutputFiles, FilePrinter


class ResultReporter:
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def __init__(self, output_files: StdOutputFiles):
        self._std = output_files
        self._out_printer = FilePrinter(output_files.out)
        self._err_printer = FilePrinter(output_files.err)

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
                              result: full_execution.FullResult) -> int:
        raise NotImplementedError('abstract method')

    def _report_unable_to_execute(self,
                                  exit_value: ExitValue,
                                  error_info: ErrorInfo) -> int:
        self._out_printer.write_line(exit_value.exit_identifier)
        print_error_info(self._err_printer, error_info)
        return exit_value.exit_code


class ResultReporterWithExitCodeFromExitValue(ResultReporter):
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def depends_on_result_in_sandbox(self) -> bool:
        return False

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: full_execution.FullResult) -> int:
        self._print_output_to_stdout_for_full_result(result)
        print_error_message_for_full_result(self._err_printer, result)
        return exit_value.exit_code

    def _print_output_to_stdout_for_full_result(self, the_full_result: full_execution.FullResult):
        raise NotImplementedError('abstract method')


class ResultReporterForNormalOutput(ResultReporterWithExitCodeFromExitValue):
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def _print_output_to_stdout_for_full_result(self, the_full_result: full_execution.FullResult):
        self._out_printer.write_line(the_full_result.status.name)


class ResultReporterForPreserveAndPrintSandboxDir(ResultReporterWithExitCodeFromExitValue):
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def _print_output_to_stdout_for_full_result(self, the_full_result: full_execution.FullResult):
        self._out_printer.write_line(str(the_full_result.sds.root_dir))


class ResultReporterForActPhaseOutput(ResultReporter):
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def depends_on_result_in_sandbox(self) -> bool:
        return True

    def report_full_execution(self,
                              exit_value: ExitValue,
                              result: full_execution.FullResult) -> int:
        def copy_file(input_file_path: pathlib.Path,
                      output_file):
            with input_file_path.open() as f:
                for data in f:
                    output_file.write(data)

        def act_phase_exit_code(exit_code_file: pathlib.Path) -> int:
            with exit_code_file.open() as f:
                exit_code_string = f.read()
                return int(exit_code_string)

        copy_file(result.sds.result.stdout_file, self._std.out)
        copy_file(result.sds.result.stderr_file, self._std.err)
        exit_code = act_phase_exit_code(result.sds.result.exitcode_file)
        shutil.rmtree(str(result.sds.root_dir))
        return exit_code


RESULT_REPORTERS = {
    Output.STATUS_CODE: ResultReporterForNormalOutput,
    Output.SANDBOX_DIRECTORY_STRUCTURE_ROOT: ResultReporterForPreserveAndPrintSandboxDir,
    Output.ACT_PHASE_OUTPUT: ResultReporterForActPhaseOutput,
}
