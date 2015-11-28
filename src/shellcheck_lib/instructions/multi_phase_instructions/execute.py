import os
import shlex

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.general import file_utils
from shellcheck_lib.instructions.utils import executable_file
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.executable_file import ExecutableFile
from shellcheck_lib.test_case.sections.common import HomeAndEds


class Setup:
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile,
                 argument_list: list):
        self.instruction_source_info = instruction_source_info
        self._executable = executable
        self.argument_list = argument_list

    @property
    def executable(self) -> ExecutableFile:
        return self._executable

    def execute(self, home_and_eds: HomeAndEds) -> sub_process_execution.Result:
        cmd_and_args = [self.executable.path_string(home_and_eds)] + self.argument_list
        executor = sub_process_execution.ExecutorThatLogsResultUnderPhaseDir()
        return executor.apply(self.instruction_source_info,
                              home_and_eds.eds,
                              cmd_and_args)

    def execute_and_return_error_message_if_non_zero_exit_status(self, home_and_eds: HomeAndEds) -> str:
        """
        :return: None iff exit status was 0 from execute.
        """
        (exit_code, stderr_output) = self.execute(home_and_eds)
        if exit_code != 0:
            msg_tail = ''
            if stderr_output:
                msg_tail = os.linesep + stderr_output
            return 'Exit code {}{}'.format(exit_code, msg_tail)
        else:
            return None


class ResultAndStderr:
    def __init__(self,
                 result: sub_process_execution.Result,
                 stderr_contents: str):
        self.result = result
        self.stderr_contents = stderr_contents


def execute_setup_and_read_stderr_if_non_zero_exitcode(setup: Setup,
                                                       home_and_eds: HomeAndEds) -> ResultAndStderr:
    stderr_contents = None
    result = setup.execute(home_and_eds)
    if result.is_success and result.exit_code != 0:
        stderr_contents = file_utils.contents_of(result.output_dir_path / result.stderr_file_name)
    return ResultAndStderr(result, stderr_contents)


class SetupParser:
    def __init__(self,
                 instruction_meta_info: sub_process_execution.InstructionMetaInfo):
        self.instruction_meta_info = instruction_meta_info

    def apply(self, source: SingleInstructionParserSource) -> Setup:
        (the_executable_file, remaining_arguments_str) = executable_file.parse_as_first_space_separated_part(
            source.instruction_argument)
        return Setup(
            sub_process_execution.InstructionSourceInfo(self.instruction_meta_info,
                                                        source.line_sequence.first_line.line_number),
            the_executable_file,
            shlex.split(remaining_arguments_str))


class InstructionParser(SingleInstructionParser):
    def __init__(self,
                 instruction_meta_info: sub_process_execution.InstructionMetaInfo,
                 setup2instruction_function):
        self._setup2instruction_function = setup2instruction_function
        self.setup_parser = SetupParser(instruction_meta_info)

    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        setup = self.setup_parser.apply(source)
        return self._setup2instruction_function(setup)
