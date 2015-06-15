import os
import pathlib
import shutil
import sys

from shellcheck_lib.execution import full_execution
from shellcheck_lib.script_language.act_script_management import ScriptLanguageSetup
from shellcheck_lib.script_language import python3
from shellcheck_lib.general import line_source

from shellcheck_lib.test_case import test_case_struct
from shellcheck_lib.cli.execution_mode.test_case.argument_parsing import INTERPRETER_FOR_TEST
from shellcheck_lib.cli.execution_mode.test_case import argument_parsing, test_case_parser
from shellcheck_lib.cli import argument_parsing_utils
from shellcheck_lib.cli.execution_mode.test_case.settings import Output, TestCaseExecutionSettings
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings
from shellcheck_lib.cli.execution_mode.help.argument_parsing import parse as parse_help
from . import main_program


HELP_COMMAND = 'help'


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 stdout_file=sys.stdout,
                 stderr_file=sys.stderr):
        self._stdout_file = stdout_file
        self._stderr_file = stderr_file

    def execute(self, command_line_arguments: list) -> int:
        if len(command_line_arguments) > 0 and command_line_arguments[0] == HELP_COMMAND:
            return self._parse_and_execute_help(command_line_arguments[1:])
        return self._parse_and_execute_test_case(command_line_arguments)

    def _parse_and_execute_test_case(self, command_line_arguments: list) -> int:
        try:
            test_case_execution_settings = argument_parsing.parse(command_line_arguments)
            return self.execute_test_case(test_case_execution_settings)
        except argument_parsing_utils.ArgumentParsingError as ex:
            self._stderr_file.write(ex.error_message)
            self._stderr_file.write(os.linesep)
            return main_program.EXIT_INVALID_USAGE

    def _parse_and_execute_help(self, help_command_arguments: list) -> int:
        try:
            settings = parse_help(help_command_arguments)
            return self.execute_help(settings)
        except argument_parsing_utils.ArgumentParsingError as ex:
            self._stderr_file.write(ex.error_message)
            self._stderr_file.write(os.linesep)
            return main_program.EXIT_INVALID_USAGE

    def execute_test_case(self, settings: TestCaseExecutionSettings) -> int:
        test_case = parse_test_case_source(settings)
        script_language_setup = resolve_script_language(settings)
        if settings.output is Output.ACT_PHASE_OUTPUT:
            execute_act_phase(settings,
                              test_case,
                              script_language_setup)
        else:
            full_result = full_execution.execute(script_language_setup,
                                                 test_case,
                                                 settings.initial_home_dir_path,
                                                 settings.execution_directory_root_name_prefix,
                                                 settings.is_keep_execution_directory_root)
            print_output_to_stdout(self._stdout_file,
                                   settings,
                                   full_result)
            return full_result.status.value

    def execute_help(self, settings: HelpSettings) -> int:
        return 0


def execute_act_phase(the_cl_arguments: TestCaseExecutionSettings,
                      test_case: test_case_struct.TestCase,
                      script_language_setup: ScriptLanguageSetup):
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
                                         the_cl_arguments.initial_home_dir_path,
                                         the_cl_arguments.execution_directory_root_name_prefix,
                                         True)
    copy_file(full_result.execution_directory_structure.result.std.stdout_file, sys.stdout)
    copy_file(full_result.execution_directory_structure.result.std.stderr_file, sys.stderr)
    exit_code = act_phase_exit_code(full_result.execution_directory_structure.result.exitcode_file)
    shutil.rmtree(str(full_result.execution_directory_structure.root_dir))
    sys.exit(exit_code)


def resolve_script_language(cl_arguments: TestCaseExecutionSettings) -> ScriptLanguageSetup:
    if cl_arguments.interpreter and cl_arguments.interpreter == INTERPRETER_FOR_TEST:
        return python3.new_script_language_setup()
    return python3.new_script_language_setup()


def parse_test_case_source(cl_arguments: TestCaseExecutionSettings) -> test_case_struct.TestCase:
    file_parser = test_case_parser.new_parser()
    source = line_source.new_for_file(cl_arguments.file_path)
    return file_parser.apply(source)


def print_output_to_stdout(stdout_file,
                           cl_arguments: TestCaseExecutionSettings,
                           the_full_result: full_execution.FullResult):
    if cl_arguments.output is Output.STATUS_CODE:
        stdout_file.write(the_full_result.status.name)
        stdout_file.write(os.linesep)
    elif cl_arguments.output is Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT:
        stdout_file.write(str(the_full_result.execution_directory_structure.root_dir))
        stdout_file.write(os.linesep)
