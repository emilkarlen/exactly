from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.utils.destination_path import *
from shellcheck_lib.instructions.utils.parse_here_document import parse_as_last_argument
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.instruction_description import InvokationVariant, Description
from shellcheck_lib.util.file_utils import ensure_parent_directory_does_exist_and_is_a_directory, write_new_text_file
from shellcheck_lib.util.string import lines_content
from shellcheck_lib.util.textformat.structure.paragraph import single_para


class TheDescription(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Creates a file.'

    def main_description_rest(self) -> list:
        return single_para('Uses Posix syntax for paths. I.e. directories are separated by /. ')

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    '[{}] FILENAME'.format('|'.join(OPTIONS)),
                    single_para('Creates a new file in the given directory.')),
        ]


class FileInfo(tuple):
    def __new__(cls,
                destination_path: DestinationPath,
                contents: str):
        return tuple.__new__(cls, (destination_path, contents))

    @property
    def destination_path(self) -> DestinationPath:
        return self[0]

    @property
    def contents(self) -> str:
        return self[1]


def parse(source: SingleInstructionParserSource) -> FileInfo:
    arguments = split_arguments_list_string(source.instruction_argument)

    (destination_path, remaining_arguments) = parse_destination_path(DestinationType.REL_CWD, True, arguments)
    contents = ''
    if remaining_arguments:
        lines = parse_as_last_argument(False, remaining_arguments, source)
        contents = lines_content(lines)
    return FileInfo(destination_path, contents)


def create_file(file_info: FileInfo,
                eds: ExecutionDirectoryStructure) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    file_path = file_info.destination_path.resolved_path(eds)
    try:
        if file_path.exists():
            return 'File does already exist: {}'.format(file_path)
    except NotADirectoryError:
        return 'Part of path exists, but perhaps one in-the-middle-component is not a directory: %s' % str(file_path)
    failure_message = ensure_parent_directory_does_exist_and_is_a_directory(file_path)
    if failure_message is not None:
        return failure_message
    try:
        write_new_text_file(file_path, file_info.contents)
    except IOError:
        return 'Cannot create file: {}'.format(file_path)
    return None
