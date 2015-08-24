import enum
import filecmp
import pathlib
import shlex

from shellcheck_lib.general import line_source
from shellcheck_lib.instructions.assert_phase.utils import InstructionWithValidationOfRegularFileRelHomeBase
from shellcheck_lib.test_case import instructions as i
from shellcheck_lib.instructions.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException
from . import utils
from shellcheck_lib.test_case.instructions import AssertPhaseInstruction


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


FILE_TYPES = {
    "symlink": FileType.SYMLINK,
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
        elif self._expected_file_type is FileType.SYMLINK:
            if not file_path.is_symlink():
                return i.new_pfh_fail('Not a symlink: ' + self._file_name_relative_current_directory)
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


class InstructionForFileContentsRelHome(InstructionWithValidationOfRegularFileRelHomeBase):
    def __init__(self,
                 target_file_name: str,
                 file_name_relative_home: str):
        super().__init__(file_name_relative_home)
        self._target_file_name = target_file_name

    def main(self, global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        target_path = pathlib.Path(self._target_file_name)
        if not target_path.exists():
            return i.new_pfh_fail('File does not exist: ' + self._target_file_name)
        if not target_path.is_file():
            return i.new_pfh_fail('Not a regular file: ' + self._target_file_name)
        if not filecmp.cmp(str(self.file_rel_home_path), self._target_file_name, shallow=False):
            return i.new_pfh_fail('Unexpected content: ' + self._target_file_name)
        return i.new_pfh_pass()


class InstructionForFileContentsRelCwd(utils.InstructionWithoutValidationBase):
    def __init__(self,
                 target_file_name: str,
                 comparison_file_name: str):
        self._target_file_name = target_file_name
        self._comparison_file_name = comparison_file_name

    def main(self, global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> i.PassOrFailOrHardError:
        target_path = pathlib.Path(self._target_file_name)
        comparison_path = pathlib.Path(self._comparison_file_name)
        res = self._is_valid_file(target_path)
        if res.status is not i.PassOrFailOrHardErrorEnum.PASS:
            return res
        res = self._is_valid_file(comparison_path)
        if res.status is not i.PassOrFailOrHardErrorEnum.PASS:
            return res
        if not filecmp.cmp(str(comparison_path), str(target_path), shallow=False):
            return i.new_pfh_fail('Unexpected content: ' + str(target_path))
        return i.new_pfh_pass()

    @staticmethod
    def _is_valid_file(path: pathlib.Path) -> i.PassOrFailOrHardError:
        if not path.exists():
            return i.new_pfh_fail('File does not exist: ' + str(path))
        if not path.is_file():
            return i.new_pfh_fail('Not a regular file: ' + str(path))
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
        if arguments[0] == 'contents':
            return self._parse_contents(file_argument, arguments[1:])
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
    def _parse_contents(file_name: str,
                        arguments: list) -> AssertPhaseInstruction:
        if len(arguments) != 2:
            msg_header = 'file/contents: Invalid number of arguments (expecting two): '
            raise SingleInstructionInvalidArgumentException(msg_header + str(arguments))
        if arguments[0] == '--rel-home':
            return InstructionForFileContentsRelHome(file_name, arguments[1])
        elif arguments[0] == '--rel-cwd':
            return InstructionForFileContentsRelCwd(file_name, arguments[1])
        msg_header = 'file/contents: Invalid argument: '
        raise SingleInstructionInvalidArgumentException(msg_header + arguments[0])

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
