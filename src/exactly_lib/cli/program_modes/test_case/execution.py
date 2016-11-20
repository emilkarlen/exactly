import pathlib
import shutil

from exactly_lib.cli.program_modes.test_case.settings import Output, TestCaseExecutionSettings
from exactly_lib.execution import full_execution, exit_values
from exactly_lib.execution.result_reporting import print_error_message_for_full_result, print_error_info
from exactly_lib.processing import test_case_processing, processors
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.test_case_processing import ErrorInfo
from exactly_lib.util.std import StdOutputFiles, FilePrinter


class Executor:
    def __init__(self,
                 output: StdOutputFiles,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup,
                 settings: TestCaseExecutionSettings):
        self._std = output
        self._out_printer = FilePrinter(output.out)
        self._err_printer = FilePrinter(output.err)
        self._split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self._instruction_setup = instruction_setup
        self._settings = settings

    def execute(self) -> int:
        if self._settings.output is Output.ACT_PHASE_OUTPUT:
            return self._execute_act_phase()
        else:
            return self._execute_normal()

    def _execute_normal(self) -> int:
        result = self._process(self._settings.is_keep_execution_directory_root)
        exit_value = exit_values.from_result(result)
        if result.status is test_case_processing.Status.EXECUTED:
            self._report_full_result(result.execution_result)
        else:
            self.__output_error_result(exit_value.exit_identifier,
                                       result.error_info)
        return exit_value.exit_code

    def __output_error_result(self,
                              stdout_error_code: str,
                              error_info: ErrorInfo):
        self._out_printer.write_line(stdout_error_code)
        print_error_info(self._err_printer, error_info)

    def _execute_act_phase(self) -> int:
        def copy_file(input_file_path: pathlib.Path,
                      output_file):
            with input_file_path.open() as f:
                for data in f:
                    output_file.write(data)

        def act_phase_exit_code(exit_code_file: pathlib.Path) -> int:
            with exit_code_file.open() as f:
                exit_code_string = f.read()
                return int(exit_code_string)

        result = self._process(True)
        full_result = result.execution_result

        copy_file(full_result.sandbox_directory_structure.result.stdout_file, self._std.out)
        copy_file(full_result.sandbox_directory_structure.result.stderr_file, self._std.err)
        exit_code = act_phase_exit_code(full_result.sandbox_directory_structure.result.exitcode_file)
        shutil.rmtree(str(full_result.sandbox_directory_structure.root_dir))
        return exit_code

    def _report_full_result(self, the_full_result: full_execution.FullResult):
        self._print_output_to_stdout_for_full_result(the_full_result)
        print_error_message_for_full_result(self._err_printer, the_full_result)

    def _print_output_to_stdout_for_full_result(self, the_full_result: full_execution.FullResult):
        if self._settings.output is Output.STATUS_CODE:
            self._out_printer.write_line(the_full_result.status.name)
        elif self._settings.output is Output.SANDBOX_DIRECTORY_STRUCTURE_ROOT:
            self._out_printer.write_line(str(the_full_result.sandbox_directory_structure.root_dir))

    def _process(self,
                 is_keep_sds: bool) -> test_case_processing.Result:
        configuration = processors.Configuration(self._split_line_into_name_and_argument_function,
                                                 self._instruction_setup,
                                                 self._settings.handling_setup,
                                                 is_keep_sds,
                                                 self._settings.execution_directory_root_name_prefix)
        processor = processors.new_processor_that_is_allowed_to_pollute_current_process(configuration)
        return processor.apply(test_case_processing.TestCaseSetup(self._settings.file_path))
