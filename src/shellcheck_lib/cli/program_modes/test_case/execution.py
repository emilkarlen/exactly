import pathlib
import shutil

from shellcheck_lib.cli.cli_environment.program_modes.test_case import exit_values
from shellcheck_lib.cli.program_modes.test_case.settings import Output, TestCaseExecutionSettings
from shellcheck_lib.cli.util.error_message_printing import output_location
from shellcheck_lib.default.program_modes.test_case import processing
from shellcheck_lib.execution import full_execution
from shellcheck_lib.execution.result import FailureInfoVisitor, PhaseFailureInfo, InstructionFailureInfo
from shellcheck_lib.test_case import error_description
from shellcheck_lib.test_case import test_case_processing
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.test_case.test_case_processing import ErrorInfo
from shellcheck_lib.util.std import StdOutputFiles, FilePrinter


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
        output_location(self._err_printer,
                        error_info.file,
                        error_info.maybe_section_name,
                        error_info.line)
        _ErrorDescriptionDisplayer(self._err_printer).visit(error_info.description)

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

        copy_file(full_result.execution_directory_structure.result.stdout_file, self._std.out)
        copy_file(full_result.execution_directory_structure.result.stderr_file, self._std.err)
        exit_code = act_phase_exit_code(full_result.execution_directory_structure.result.exitcode_file)
        shutil.rmtree(str(full_result.execution_directory_structure.root_dir))
        return exit_code

    def _report_full_result(self, the_full_result: full_execution.FullResult):
        self._print_output_to_stdout_for_full_result(the_full_result)
        self._print_output_to_stderr_for_full_result(the_full_result)

    def _print_output_to_stdout_for_full_result(self, the_full_result: full_execution.FullResult):
        if self._settings.output is Output.STATUS_CODE:
            self._out_printer.write_line(the_full_result.status.name)
        elif self._settings.output is Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT:
            self._out_printer.write_line(str(the_full_result.execution_directory_structure.root_dir))

    def _print_output_to_stderr_for_full_result(self, the_full_result: full_execution.FullResult):
        if the_full_result.is_failure:
            failure_info = the_full_result.failure_info
            _SourceDisplayer(self._err_printer).visit(failure_info)
            if failure_info.failure_details.is_error_message:
                ed = error_description.of_message(failure_info.failure_details.failure_message)
            else:
                ed = error_description.of_exception(failure_info.failure_details.exception)
            _ErrorDescriptionDisplayer(self._err_printer).visit(ed)

    def _process(self,
                 is_keep_eds: bool) -> test_case_processing.Result:
        configuration = processing.Configuration(self._split_line_into_name_and_argument_function,
                                                 self._instruction_setup,
                                                 self._settings.act_phase_setup,
                                                 self._settings.preprocessor,
                                                 is_keep_eds,
                                                 self._settings.execution_directory_root_name_prefix)
        processor = processing.new_processor_that_is_allowed_to_pollute_current_process(configuration)
        return processor.apply(test_case_processing.TestCaseSetup(self._settings.file_path))


class _ErrorDescriptionDisplayer(error_description.ErrorDescriptionVisitor):
    def __init__(self,
                 out: FilePrinter):
        self.out = out

    def _visit_message(self, ed: error_description.ErrorDescriptionOfMessage):
        self.out.write_line_if_present(ed.message)

    def _visit_exception(self, ed: error_description.ErrorDescriptionOfException):
        self.out.write_line_if_present(ed.message)
        self.out.write_line('Exception:')
        self.out.write_line(str(ed.exception))

    def _visit_external_process_error(self, ed: error_description.ErrorDescriptionOfExternalProcessError):
        self.out.write_line_if_present(ed.message)
        self.out.write_line('Exit code: ' + str(ed.external_process_error.exit_code))
        if ed.external_process_error.stderr_output:
            self.out.write_line(ed.external_process_error.stderr_output)


class _SourceDisplayer(FailureInfoVisitor):
    def __init__(self,
                 out: FilePrinter):
        self.out = out

    def _visit_phase_failure(self, failure_info: PhaseFailureInfo):
        output_location(self.out,
                        None,
                        failure_info.phase_step.phase.identifier,
                        None)

    def _visit_instruction_failure(self, failure_info: InstructionFailureInfo):
        output_location(self.out,
                        None,
                        failure_info.phase_step.phase.identifier,
                        failure_info.source_line)
