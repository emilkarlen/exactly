from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.concepts.plain_concepts.current_working_directory import CURRENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.instructions.utils.arg_parse.parse_destination_path import parse_destination_path
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.instructions.utils.destination_path import DestinationPath
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, additional_format_map: dict = None, is_in_assert_phase: bool = False):
        super().__init__(name, additional_format_map, is_in_assert_phase)
        self.path_arg = _PATH_ARGUMENT

    def single_line_description(self) -> str:
        return self._format('Creates a directory')

    def _main_description_rest_body(self) -> list:
        text = """\
            Creates parent directories if needed.


            Does nothing if the given directory already exists.
            """
        return (self._paragraphs(text) +
                rel_path_doc.default_relativity_for_rel_opt_type(_PATH_ARGUMENT.name,
                                                                 RELATIVITY_OPTIONS.options.default_option) +
                dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = rel_path_doc.mandatory_path_with_optional_relativity(_PATH_ARGUMENT)
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              []),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            rel_path_doc.relativity_syntax_element_description(_PATH_ARGUMENT,
                                                               RELATIVITY_OPTIONS.options.accepted_options),
        ]

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(RELATIVITY_OPTIONS.options.accepted_options)
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT])
        return [concept.cross_reference_target() for concept in concepts]


def parse(argument: str) -> DestinationPath:
    arguments = split_arguments_list_string(argument)
    (destination_path, remaining_arguments) = parse_destination_path(RELATIVITY_OPTIONS, True, arguments)

    if remaining_arguments:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: ' + str(remaining_arguments))
    return destination_path


def make_dir_in_current_dir(sds: SandboxDirectoryStructure, destination_path: DestinationPath) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = destination_path.resolved_path_if_not_rel_home(sds)
    try:
        if dir_path.is_dir():
            return None
    except NotADirectoryError:
        return 'Part of path exists, but is not a directory: %s' % str(dir_path)
    try:
        dir_path.mkdir(parents=True)
    except FileExistsError:
        return 'Path exists, but is not a directory: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Clash with existing file: {}'.format(dir_path)
    return None


def execute_and_return_sh(sds: SandboxDirectoryStructure, destination_path: DestinationPath) -> sh.SuccessOrHardError:
    error_message = make_dir_in_current_dir(sds, destination_path)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)


_PATH_ARGUMENT = dt.PATH_ARGUMENT

RELATIVITY_OPTIONS = argument_configuration_for_file_creation(_PATH_ARGUMENT.name)
