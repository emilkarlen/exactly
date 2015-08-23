import enum
import pathlib
import shlex

from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.instructions.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException
from . import utils
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction


class FileType(enum.Enum):
    REGULAR = 1
    DIRECTORY = 2


FILE_TYPES = {
    "regular": FileType.REGULAR,
    "directory": FileType.DIRECTORY
}


class InstructionForFileType(utils.InstructionWithoutValidationBase):
    def __init__(self,
                 file_name_relative_current_directory: str,
                 expected_file_type: FileType):
        """
        :param expected_file_type: None means testing for existence - any file type
         is accepted.
        """
        self._file_name_relative_current_directory = file_name_relative_current_directory
        self._expected_file_type = expected_file_type

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        file_path = pathlib.Path(self._file_name_relative_current_directory)
        if not file_path.exists():
            return i.new_pfh_fail('File does not exist: ' + self._file_name_relative_current_directory)
        if self._expected_file_type is FileType.REGULAR:
            if not file_path.is_file():
                return i.new_pfh_fail('Not a regular file: ' + self._file_name_relative_current_directory)
        elif self._expected_file_type is FileType.DIRECTORY:
            if not file_path.is_dir():
                return i.new_pfh_fail('Not a directory: ' + self._file_name_relative_current_directory)
        return i.new_pfh_pass()


class Parser(SingleInstructionParser):
    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> AssertPhaseInstruction:
        arguments = shlex.split(instruction_argument)
        if not arguments:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (file name)')
        file_argument = arguments[0]
        del arguments[0]
        if not arguments:
            return InstructionForFileType(file_argument, None)
        if arguments[0] == 'type':
            return self._parse_type(file_argument, arguments[1:])
        raise NotImplementedError()

    def _parse_type(self,
                    file_name: str,
                    arguments: list) -> AssertPhaseInstruction:
        num_arguments = len(arguments)
        if num_arguments == 0:
            raise SingleInstructionInvalidArgumentException('file/type expects a type argument')
        if num_arguments > 1:
            raise SingleInstructionInvalidArgumentException('file/type expects a single type argument')
        try:
            return InstructionForFileType(file_name, FILE_TYPES[arguments[0]])
        except KeyError:
            raise SingleInstructionInvalidArgumentException('Invalid file type: ' + arguments[0])
