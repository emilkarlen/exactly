import os

from exactly_lib.common.instruction_documentation import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils import documentation_text
from exactly_lib.instructions.utils.destination_path import *
from exactly_lib.instructions.utils.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.utils.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.relative_path_options_documentation import RelOptionRenderer
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description import Description


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    PATH_ARG_NAME = 'DIR'

    def __init__(self, name: str):
        self.pwd_concept_name = formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular)
        super().__init__(name, {
            'pwd_concept': self.pwd_concept_name,
            'dir_argument': self.PATH_ARG_NAME,
        })
        self.dir_arg = a.Named(self.PATH_ARG_NAME)

    def description(self) -> Description:
        return Description(self._text('Sets the {pwd_concept}'),
                           documentation_text.default_relativity(self.PATH_ARG_NAME,
                                                                 self.pwd_concept_name) +
                           self._paragraphs(_NO_DIR_ARG_MEANING) +
                           documentation_text.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.OPTIONAL,
                         documentation_text.RELATIVITY_ARGUMENT),
                a.Single(a.Multiplicity.OPTIONAL,
                         self.dir_arg),
            ])),
        ]

    def syntax_element_descriptions(self) -> list:
        renderer = RelOptionRenderer(self.dir_arg.name)
        return [
            SyntaxElementDescription(documentation_text.RELATIVITY_ARGUMENT.name,
                                     [renderer.list_for(ALL_OPTIONS)]),
        ]

    def see_also(self) -> list:
        from exactly_lib.help.concepts.plain_concepts.sandbox import \
            SANDBOX_CONCEPT
        return [
            PRESENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
            SANDBOX_CONCEPT.cross_reference_target(),
        ]


_NO_DIR_ARG_MEANING = """\
Omitting the {dir_argument} is the same as giving ".".
"""


def parse(argument: str) -> DestinationPath:
    arguments = split_arguments_list_string(argument)

    (destination_path, remaining_arguments) = parse_destination_path(DestinationType.REL_CWD, False, arguments)
    if remaining_arguments:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(remaining_arguments))
    return destination_path


def change_dir(destination: DestinationPath,
               eds: ExecutionDirectoryStructure) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = destination.resolved_path(eds)
    try:
        os.chdir(str(dir_path))
    except FileNotFoundError:
        return 'Directory does not exist: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Not a directory: {}'.format(dir_path)
    return None


def execute_with_sh_result(destination: DestinationPath,
                           eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
    error_message = change_dir(destination, eds)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
