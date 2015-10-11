import enum
import pathlib
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.instructions.assert_phase.utils import instruction_utils
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.os_services import OsServices


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


FILE_TYPES = {
    "symlink": FileType.SYMLINK,
    "regular": FileType.REGULAR,
    "directory": FileType.DIRECTORY
}

DESCRIPTION = Description(
    'Tests the type of a file',
    """All tests fails if FILENAME does not exist.

    regular: Tests if FILENAME is a regular file or a sym-link to a regular file.
    directory: Tests if FILENAME is a regular file or a sym-link to a regular file.
    symlink: Tests if FILENAME is a sym-link.
    """,
    [
        InvokationVariant(
            'FILENAME type [{}]'.format('|'.join(FILE_TYPES.keys())),
            'File exists and has given type'),
    ])


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        if len(arguments) != 2:
            raise SingleInstructionInvalidArgumentException('Invalid syntax')
        file_argument = arguments[0]
        del arguments[0]
        return self._parse_type(file_argument, arguments)

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


class InstructionForFileType(instruction_utils.InstructionWithoutValidationBase):
    def __init__(self,
                 file_name_relative_current_directory: str,
                 expected_file_type: FileType):
        self._file_name_relative_current_directory = file_name_relative_current_directory
        self._expected_file_type = expected_file_type

    def main(self,
             environment: i.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        file_path = pathlib.Path(self._file_name_relative_current_directory)
        if not file_path.exists():
            return pfh.new_pfh_fail('File does not exist: ' + self._file_name_relative_current_directory)
        if self._expected_file_type is FileType.REGULAR:
            if not file_path.is_file():
                return pfh.new_pfh_fail('Not a regular file: ' + self._file_name_relative_current_directory)
        elif self._expected_file_type is FileType.DIRECTORY:
            if not file_path.is_dir():
                return pfh.new_pfh_fail('Not a directory: ' + self._file_name_relative_current_directory)
        elif self._expected_file_type is FileType.SYMLINK:
            if not file_path.is_symlink():
                return pfh.new_pfh_fail('Not a symlink: ' + self._file_name_relative_current_directory)
        return pfh.new_pfh_pass()
