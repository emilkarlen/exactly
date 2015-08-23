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


class InstructionForFileEmptinessBase(utils.InstructionWithoutValidationBase):
    def __init__(self,
                 file_name_relative_current_directory: str):
        self._file_name_relative_current_directory = file_name_relative_current_directory

    def main(self,
             global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        file_path = pathlib.Path(self._file_name_relative_current_directory)
        return all_of(file_path,
                      (self._file_must_be_a_regular_file,
                       self._file_must_have_expected_emptiness_status))

    def _file_must_be_a_regular_file(self, file_path: pathlib.Path) -> i.PassOrFailOrHardError:
        if not file_path.is_file():
            return i.new_pfh_fail('Not a regular file: ' + self._file_name_relative_current_directory)
        return i.new_pfh_pass()

    def _file_must_have_expected_emptiness_status(self, file_path: pathlib.Path) -> i.PassOrFailOrHardError:
        raise NotImplementedError()


class InstructionForFileContentsEmpty(InstructionForFileEmptinessBase):
    def __init__(self,
                 file_name_relative_current_directory: str):
        super().__init__(file_name_relative_current_directory)

    def _file_must_have_expected_emptiness_status(self, file_path: pathlib.Path) -> i.PassOrFailOrHardError:
        size = file_path.stat().st_size
        if size != 0:
            return i.new_pfh_fail('File is not empty: Size (in bytes): ' + str(size))
        return i.new_pfh_pass()


class InstructionForFileContentsNonEmpty(InstructionForFileEmptinessBase):
    def __init__(self,
                 file_name_relative_current_directory: str):
        super().__init__(file_name_relative_current_directory)

    def _file_must_have_expected_emptiness_status(self, file_path: pathlib.Path) -> i.PassOrFailOrHardError:
        size = file_path.stat().st_size
        if size == 0:
            return i.new_pfh_fail('File is empty')
        return i.new_pfh_pass()


def all_of(arg, checker_for_arg) -> i.PassOrFailOrHardError:
    for f in checker_for_arg:
        result = f(arg)
        if result.status is not i.PassOrFailOrHardErrorEnum.PASS:
            return result
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
        elif arguments[0] == 'empty':
            return self._parse_empty(file_argument, arguments[1:])
        elif arguments[:2] == ['!', 'empty']:
            return self._parse_non_empty(file_argument, arguments[2:])
        raise SingleInstructionInvalidArgumentException('Invalid file instruction')

    @staticmethod
    def _parse_empty(file_name: str,
                     arguments: list) -> AssertPhaseInstruction:
        if arguments:
            raise SingleInstructionInvalidArgumentException('file/empty: Extra arguments: ' + str(arguments))
        return InstructionForFileContentsEmpty(file_name)

    @staticmethod
    def _parse_non_empty(file_name: str,
                         arguments: list) -> AssertPhaseInstruction:
        if arguments:
            raise SingleInstructionInvalidArgumentException('file/!empty: Extra arguments: ' + str(arguments))
        return InstructionForFileContentsNonEmpty(file_name)

    @staticmethod
    def _parse_type(file_name: str,
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
