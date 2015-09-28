import enum
import shlex

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import Description, InvokationVariant
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction
from .utils import contents_utils

DESCRIPTION = Description(
    'Test the contents of a file.',
    '',
    [
        InvokationVariant(
            'FILENAME empty',
            'File exists, is a regular file, and is empty'),
        InvokationVariant(
            'FILENAME ! empty',
            'File exists, is a regular file, and is not empty'),
        InvokationVariant(
            'FILENAME --rel-home FILE',
            'Compares contents of FILENAME to contents of FILE (which is a path relative home)'),
        InvokationVariant(
            'FILENAME --rel-cwd FILE',
            'Compares contents of FILENAME to contents of FILE (which is a path relative current working directory)'),
    ])


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


FILE_TYPES = {
    "symlink": FileType.SYMLINK,
    "regular": FileType.REGULAR,
    "directory": FileType.DIRECTORY
}


class Parser(SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = shlex.split(source.instruction_argument)
        if not arguments:
            raise SingleInstructionInvalidArgumentException('At least one argument expected (file name)')
        file_argument = arguments[0]
        del arguments[0]
        comparison_target = contents_utils.ActComparisonTarget(file_argument)
        content_instruction = contents_utils.try_parse_content(comparison_target, arguments)
        if content_instruction is not None:
            return content_instruction
        raise SingleInstructionInvalidArgumentException('Invalid file instruction')
