import pathlib

from exactly_lib.common.instruction_documentation import InvokationVariant
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string, \
    ensure_is_not_option_argument
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.cli_syntax.elements import argument as a


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, additional_format_map: dict = None, is_in_assert_phase: bool = False):
        format_map = {
            'pwd': formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular),
        }
        if additional_format_map is not None:
            format_map.update(additional_format_map)
        super().__init__(name, format_map, is_in_assert_phase)
        self.path_arg = dt.PATH_ARGUMENT

    def single_line_description(self) -> str:
        return self._format('Creates a directory in the {pwd}')

    def _main_description_rest_body(self) -> list:
        text = """\
            Creates parent directories if needed.


            Does nothing if the given directory already exists.
            """
        return self._paragraphs(text) + dt.paths_uses_posix_syntax()

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.MANDATORY,
                         self.path_arg)]),
                []),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            dt.a_path_that_is_relative_the(self.path_arg,
                                           PRESENT_WORKING_DIRECTORY_CONCEPT),
        ]

    def see_also(self) -> list:
        return [
            PRESENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
        ]


def parse(argument: str) -> str:
    arguments = split_arguments_list_string(argument)
    if len(arguments) != 1:
        raise SingleInstructionInvalidArgumentException('Usage: PATH')
    directory_argument = arguments[0]
    ensure_is_not_option_argument(directory_argument)
    return directory_argument


def make_dir_in_current_dir(directory_components: str) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = pathlib.Path() / directory_components
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


def execute_and_return_sh(directory_components: str) -> sh.SuccessOrHardError:
    error_message = make_dir_in_current_dir(directory_components)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
