import os
import pathlib
import shutil

from shellcheck_lib.script_language.act_script_management import ScriptLanguageSetup
from shellcheck_lib.script_language import python3
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import test_case_struct
from shellcheck_lib.cli.execution_mode.test_case.argument_parsing import INTERPRETER_FOR_TEST
from shellcheck_lib.cli.execution_mode.test_case import test_case_parser
from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.instruction_setup import InstructionsSetup
from shellcheck_lib.execution import full_execution
from shellcheck_lib.cli.execution_mode.test_case.settings import Output, TestCaseExecutionSettings


class Executor:
    def __init__(self,
                 output: main_program.StdOutputFiles,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup,
                 settings: TestCaseExecutionSettings):
        self._std = output
        self._split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self._instruction_setup = instruction_setup
        self._settings = settings

    def execute(self) -> int:
        test_case = self._parse_test_case_source()
        script_language_setup = resolve_script_language(self._settings)
        if self._settings.output is Output.ACT_PHASE_OUTPUT:
            return self._execute_act_phase(test_case,
                                           script_language_setup)
        else:
            full_result = full_execution.execute(script_language_setup,
                                                 test_case,
                                                 self._settings.initial_home_dir_path,
                                                 self._settings.execution_directory_root_name_prefix,
                                                 self._settings.is_keep_execution_directory_root)
            self._print_output_to_stdout(full_result)
            return full_result.status.value

    def _execute_act_phase(self,
                           test_case: test_case_struct.TestCase,
                           script_language_setup: ScriptLanguageSetup) -> int:
        def copy_file(input_file_path: pathlib.Path,
                      output_file):
            with input_file_path.open() as f:
                for data in f:
                    output_file.write(data)

        def act_phase_exit_code(exit_code_file: pathlib.Path) -> int:
            with exit_code_file.open() as f:
                exit_code_string = f.read()
                return int(exit_code_string)

        full_result = full_execution.execute(script_language_setup,
                                             test_case,
                                             self._settings.initial_home_dir_path,
                                             self._settings.execution_directory_root_name_prefix,
                                             True)
        copy_file(full_result.execution_directory_structure.result.std.stdout_file, self._std.out)
        copy_file(full_result.execution_directory_structure.result.std.stderr_file, self._std.err)
        exit_code = act_phase_exit_code(full_result.execution_directory_structure.result.exitcode_file)
        shutil.rmtree(str(full_result.execution_directory_structure.root_dir))
        return exit_code

    def _print_output_to_stdout(self, the_full_result: full_execution.FullResult):
        if self._settings.output is Output.STATUS_CODE:
            self._std.out.write(the_full_result.status.name)
            self._std.out.write(os.linesep)
        elif self._settings.output is Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT:
            self._std.out.write(str(the_full_result.execution_directory_structure.root_dir))
            self._std.out.write(os.linesep)

    def _parse_test_case_source(self) -> test_case_struct.TestCase:
        file_parser = test_case_parser.new_parser(self._split_line_into_name_and_argument_function,
                                                  self._instruction_setup)
        source = line_source.new_for_file(self._settings.file_path)
        return file_parser.apply(source)


def resolve_script_language(cl_arguments: TestCaseExecutionSettings) -> ScriptLanguageSetup:
    if cl_arguments.interpreter and cl_arguments.interpreter == INTERPRETER_FOR_TEST:
        return python3.new_script_language_setup()
    return python3.new_script_language_setup()


