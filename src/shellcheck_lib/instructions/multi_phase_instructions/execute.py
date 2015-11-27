import os
import subprocess

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource
from shellcheck_lib.instructions.utils import executable_file
from shellcheck_lib.instructions.utils.executable_file import ExecutableFile
from shellcheck_lib.test_case.sections.common import HomeAndEds


class Setup(tuple):
    def __new__(cls,
                executable: ExecutableFile,
                arguments: str):
        return tuple.__new__(cls, (executable, arguments))

    @property
    def executable(self) -> ExecutableFile:
        return self[0]

    @property
    def arguments(self) -> str:
        return self[1]

    def execute(self, home_and_eds: HomeAndEds) -> (int, str):
        """
        :return: (Exit code from sub process, Output on stderr, or None)
        """
        args = self.executable.path_string(home_and_eds) + ' ' + self.arguments
        exit_code = subprocess.call(args,
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        return exit_code, None

    def execute_and_return_error_message_if_non_zero_exit_status(self, home_and_eds: HomeAndEds) -> str:
        """
        :return: None iff exit status was 0 from execute.
        """
        self.execute(home_and_eds)
        if exit_code != 0:
            msg_tail = ''
            if err_output:
                msg_tail = os.linesep + err_output
            return 'Exit code {}{}'.format(exit_code, msg_tail)
        else:
            return None


class Parser(SingleInstructionParser):
    def __init__(self,
                 setup2instruction_function):
        self._setup2instruction_function = setup2instruction_function

    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        (the_executable_file, remaining_arguments_str) = executable_file.parse_as_first_space_separated_part(
            source.instruction_argument)
        setup = Setup(the_executable_file, remaining_arguments_str)
        return self._setup2instruction_function(setup)
