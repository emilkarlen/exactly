from exactly_lib.common.instruction_documentation import InvokationVariant
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils import documentation_text as dt
from exactly_lib.instructions.utils.destination_path import *
from exactly_lib.instructions.utils.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.utils.parse_here_document import parse_as_last_argument
from exactly_lib.instructions.utils.parse_utils import split_arguments_list_string
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist_and_is_a_directory, write_new_text_file
from exactly_lib.util.string import lines_content
from exactly_lib.util.textformat.structure import structures as docs


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str):
        super().__init__(name, {})
        self.path_arg = dt.PATH_ARGUMENT

    def single_line_description(self) -> str:
        return 'Creates a file'

    def main_description_rest(self) -> list:
        pwd_concept_name = formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular)
        return (dt.default_relativity(self.path_arg.name,
                                      pwd_concept_name) +
                dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = [a.Single(a.Multiplicity.OPTIONAL, dt.RELATIVITY_ARGUMENT),
                     a.Single(a.Multiplicity.MANDATORY, self.path_arg), ]
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              docs.paras('Creates an empty file.')),
            InvokationVariant(self._cl_syntax(a.CommandLine(arguments,
                                                            suffix=dt.HERE_DOC_SUFFIX)),
                              docs.paras('Creates a file with contents given by a here document.')),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            dt.relativity_syntax_element_description(self.path_arg,
                                                     ALL_OPTIONS),
        ]

    def see_also(self) -> list:
        return [
            PRESENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
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
