import os
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.general import file_utils
from shellcheck_lib.instructions.utils import executable_file
from shellcheck_lib.instructions.utils import parse_file_ref
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.executable_file import ExecutableFile
from shellcheck_lib.instructions.utils.file_ref import FileRef
from shellcheck_lib.instructions.utils.relative_path_options import REL_HOME_OPTION
from shellcheck_lib.test_case.sections.common import HomeAndEds

INTERPRET_OPTION = '--interpret'


def description(single_line_description: str):
    return Description(single_line_description,
                       '',
                       [InvokationVariant('EXECUTABLE [--] ARGUMENT...',
                                          """Executes the given executable with the given command line arguments.
                                          The arguments are splitted according to shell syntax."""),
                        ],
                       [SyntaxElementDescription('EXECUTABLE',
                                                 'Specifies an executable program',
                                                 [
                                                     InvokationVariant('ABSOLUTE-PATH', ''),
                                                     InvokationVariant('{} PATH'.format(REL_HOME_OPTION), ''),
                                                 ]),
                        ]
                       )


class SetupForExecutableWithArguments:
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile):
        self.instruction_source_info = instruction_source_info
        self._executable = executable

    @property
    def executable(self) -> ExecutableFile:
        return self._executable

    def execute(self, home_and_eds: HomeAndEds) -> sub_process_execution.Result:
        cmd_and_args = [self.executable.path_string(home_and_eds)] + self._arguments(home_and_eds)
        executor = sub_process_execution.ExecutorThatLogsResultUnderPhaseDir()
        return executor.apply(self.instruction_source_info,
                              home_and_eds.eds,
                              cmd_and_args)

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        raise NotImplementedError()


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


class SetupForExecute(SetupForExecutableWithArguments):
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile,
                 argument_list: list):
        super().__init__(instruction_source_info, executable)
        self.argument_list = argument_list

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        return self.argument_list


class SetupForInterpret(SetupForExecutableWithArguments):
    def __init__(self,
                 instruction_source_info: sub_process_execution.InstructionSourceInfo,
                 executable: ExecutableFile,
                 file_to_interpret: FileRef,
                 argument_list: list):
        super().__init__(instruction_source_info, executable)
        self.file_to_interpret = file_to_interpret
        self.argument_list = argument_list

    def _arguments(self, home_and_eds: HomeAndEds) -> list:
        return [str(self.file_to_interpret.file_path_post_eds(home_and_eds))] + self.argument_list


class ResultAndStderr:
    def __init__(self,
                 result: sub_process_execution.Result,
                 stderr_contents: str):
        self.result = result
        self.stderr_contents = stderr_contents


def execute_setup_and_read_stderr_if_non_zero_exitcode(setup: SetupForExecutableWithArguments,
                                                       home_and_eds: HomeAndEds) -> ResultAndStderr:
    stderr_contents = None
    result = setup.execute(home_and_eds)
    if result.is_success and result.exit_code != 0:
        stderr_contents = file_utils.contents_of(result.output_dir_path / result.stderr_file_name)
    return ResultAndStderr(result, stderr_contents)


def failure_message_for_nonzero_status(result_and_err: ResultAndStderr) -> str:
    msg_tail = ''
    if result_and_err.stderr_contents:
        msg_tail = os.linesep + result_and_err.stderr_contents
    return 'Exit code {}{}'.format(result_and_err.result.exit_code, msg_tail)


class SetupParser:
    def __init__(self,
                 instruction_meta_info: sub_process_execution.InstructionMetaInfo):
        self.instruction_meta_info = instruction_meta_info

    def apply(self, source: SingleInstructionParserSource) -> SetupForExecutableWithArguments:
        (the_executable_file, remaining_arguments_str) = executable_file.parse_as_first_space_separated_part(
            source.instruction_argument)
        first_token_and_remaining_arguments_str = remaining_arguments_str.split(maxsplit=1)
        if not first_token_and_remaining_arguments_str:
            return self._execute(source, the_executable_file, remaining_arguments_str)
        first_token = first_token_and_remaining_arguments_str[0]
        if first_token == INTERPRET_OPTION:
            return self._interpret(source, the_executable_file, first_token_and_remaining_arguments_str[1])
        return self._execute(source, the_executable_file, remaining_arguments_str)

    def _execute(self,
                 source: SingleInstructionParserSource,
                 exe_file: ExecutableFile,
                 remaining_arguments_str: str) -> SetupForExecutableWithArguments:
        return SetupForExecute(
            sub_process_execution.InstructionSourceInfo(self.instruction_meta_info,
                                                        source.line_sequence.first_line.line_number),
            exe_file,
            shlex.split(remaining_arguments_str))

    def _interpret(self,
                   source: SingleInstructionParserSource,
                   exe_file: ExecutableFile,
                   remaining_arguments_str: str) -> SetupForExecutableWithArguments:
        remaining_arguments = shlex.split(remaining_arguments_str)
        (file_to_interpret, remaining_arguments) = parse_file_ref.parse_relative_file_argument(remaining_arguments)
        return SetupForInterpret(
            sub_process_execution.InstructionSourceInfo(self.instruction_meta_info,
                                                        source.line_sequence.first_line.line_number),
            exe_file,
            file_to_interpret,
            remaining_arguments)


class InstructionParser(SingleInstructionParser):
    def __init__(self,
                 instruction_meta_info: sub_process_execution.InstructionMetaInfo,
                 setup2instruction_function):
        self._setup2instruction_function = setup2instruction_function
        self.setup_parser = SetupParser(instruction_meta_info)

    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        setup = self.setup_parser.apply(source)
        return self._setup2instruction_function(setup)
