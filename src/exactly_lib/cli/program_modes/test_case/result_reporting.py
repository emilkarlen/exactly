import pathlib
import shutil

from exactly_lib.cli.program_modes.test_case.settings import Output
from exactly_lib.execution import full_execution
from exactly_lib.execution.result_reporting import print_error_message_for_full_result, print_error_info
from exactly_lib.processing import test_case_processing, exit_values
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.util.std import StdOutputFiles, FilePrinter


class ResultReporter:
    """Reports the result of the execution via exitcode, stdout, stderr."""

    def __init__(self,
                 output_files: StdOutputFiles,
                 output_type: Output):
        self._std = output_files
        self._out_printer = FilePrinter(output_files.out)
        self._err_printer = FilePrinter(output_files.err)
        self._output_type = output_type

    def report(self, result: test_case_processing.Result) -> int:
        if self._output_type is Output.ACT_PHASE_OUTPUT:
            return self.report_result_of_act_phase_execution(result)
        else:
            return self.report_result_of_normal_execution(result)

    def report_result_of_normal_execution(self, result: test_case_processing.Result) -> int:
        exit_value = exit_values.from_result(result)
        if result.status is test_case_processing.Status.EXECUTED:
            self._output_report_of_full_result(result.execution_result)
        else:
            self.__output_error_result(exit_value.exit_identifier,
                                       result.error_info)
        return exit_value.exit_code

    def report_result_of_act_phase_execution(self, result: test_case_processing.Result) -> int:
        def copy_file(input_file_path: pathlib.Path,
                      output_file):
            with input_file_path.open() as f:
                for data in f:
                    output_file.write(data)

        def act_phase_exit_code(exit_code_file: pathlib.Path) -> int:
            with exit_code_file.open() as f:
                exit_code_string = f.read()
                return int(exit_code_string)

        full_result = result.execution_result

        copy_file(full_result.sds.result.stdout_file, self._std.out)
        copy_file(full_result.sds.result.stderr_file, self._std.err)
        exit_code = act_phase_exit_code(full_result.sds.result.exitcode_file)
        shutil.rmtree(str(full_result.sds.root_dir))
        return exit_code

    def __output_error_result(self,
                              stdout_error_code: str,
                              error_info: ErrorInfo):
        self._out_printer.write_line(stdout_error_code)
        print_error_info(self._err_printer, error_info)

    def _output_report_of_full_result(self, the_full_result: full_execution.FullResult):
        self._print_output_to_stdout_for_full_result(the_full_result)
        print_error_message_for_full_result(self._err_printer, the_full_result)

    def _print_output_to_stdout_for_full_result(self, the_full_result: full_execution.FullResult):
        if self._output_type is Output.STATUS_CODE:
            self._out_printer.write_line(the_full_result.status.name)
        elif self._output_type is Output.SANDBOX_DIRECTORY_STRUCTURE_ROOT:
            self._out_printer.write_line(str(the_full_result.sds.root_dir))
