import os
import pathlib
import shutil

from shellcheck_lib.cli.utils import resolve_script_language
from shellcheck_lib.general.output import StdOutputFiles
from shellcheck_lib.default.execution_mode.test_case import processing
from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.cli.execution_mode.test_case.settings import Output, TestCaseExecutionSettings
from shellcheck_lib.execution import full_execution
from shellcheck_lib.test_case import test_case_processing

NO_EXECUTION_EXIT_CODE = 3

class Executor:
    def __init__(self,
                 output: StdOutputFiles,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup,
                 settings: TestCaseExecutionSettings):
        self._std = output
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
        if result.status is not test_case_processing.Status.EXECUTED:
            if result.status is test_case_processing.Status.INTERNAL_ERROR:
                self._out_line(result.status.name)
            else:
                self._out_line(result.error_type.name)
            return NO_EXECUTION_EXIT_CODE
        else:
            full_result = result.execution_result
            self._print_output_to_stdout_for_full_result(full_result)
            return full_result.status.value

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

        copy_file(full_result.execution_directory_structure.result.std.stdout_file, self._std.out)
        copy_file(full_result.execution_directory_structure.result.std.stderr_file, self._std.err)
        exit_code = act_phase_exit_code(full_result.execution_directory_structure.result.exitcode_file)
        shutil.rmtree(str(full_result.execution_directory_structure.root_dir))
        return exit_code

    def _print_output_to_stdout_for_full_result(self, the_full_result: full_execution.FullResult):
        if self._settings.output is Output.STATUS_CODE:
            self._out_line(the_full_result.status.name)
        elif self._settings.output is Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT:
            self._out_line(str(the_full_result.execution_directory_structure.root_dir))

    def _out_line(self, s: str):
        self._std.out.write(s)
        self._std.out.write(os.linesep)

    def _process(self,
                 is_keep_eds: bool) -> test_case_processing.Result:
        configuration = processing.Configuration(self._split_line_into_name_and_argument_function,
                                                 self._instruction_setup,
                                                 resolve_script_language(self._settings.interpreter),
                                                 self._settings.preprocessor,
                                                 is_keep_eds,
                                                 self._settings.execution_directory_root_name_prefix)
        processor = processing.new_processor_that_is_allowed_to_pollute_current_process(configuration)
        return processor.apply(test_case_processing.TestCaseSetup(self._settings.file_path))
