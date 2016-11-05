import os

from exactly_lib.common.instruction_documentation import InvokationVariant
from exactly_lib.help.concepts.plain_concepts.present_working_directory import PRESENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.arg_parse.parse_destination_path import parse_destination_path, ALL_OPTIONS
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.destination_path import *
from exactly_lib.instructions.utils.documentation import documentation_text as dt, relative_path_options_documentation
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util.cli_syntax.elements import argument as a


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        self.pwd_concept_name = formatting.concept(PRESENT_WORKING_DIRECTORY_CONCEPT.name().singular)
        self.dir_arg = dt.DIR_ARGUMENT
        super().__init__(name, {
            'pwd_concept': self.pwd_concept_name,
            'dir_argument': self.dir_arg.name,
        },
                         is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._format('Sets the {pwd_concept}')

    def _main_description_rest_body(self) -> list:
        return (relative_path_options_documentation.default_relativity_for_rel_opt_type(
            self.dir_arg.name,
            relative_path_options_documentation.RelOptionType.REL_PWD) +
                self._paragraphs(_NO_DIR_ARG_MEANING) +
                dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                relative_path_options_documentation.OPTIONAL_RELATIVITY_ARGUMENT_USAGE,
                a.Single(a.Multiplicity.OPTIONAL,
                         self.dir_arg),
            ])),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            relative_path_options_documentation.relativity_syntax_element_description(self.dir_arg,
                                                                                      ALL_OPTIONS),
        ]

    def see_also(self) -> list:
        from exactly_lib.help.concepts.plain_concepts.sandbox import \
            SANDBOX_CONCEPT
        return [
            PRESENT_WORKING_DIRECTORY_CONCEPT.cross_reference_target(),
            SANDBOX_CONCEPT.cross_reference_target(),
        ]


_NO_DIR_ARG_MEANING = """\
Omitting the {dir_argument} is the same as giving "." (TODO is this correct??).
"""


def parse(argument: str) -> DestinationPath:
    arguments = split_arguments_list_string(argument)

    (destination_path, remaining_arguments) = parse_destination_path(DestinationType.REL_CWD, False, arguments)
    if remaining_arguments:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(remaining_arguments))
    return destination_path


def change_dir(destination: DestinationPath,
               sds: SandboxDirectoryStructure) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = destination.resolved_path(sds)
    try:
        os.chdir(str(dir_path))
    except FileNotFoundError:
        return 'Directory does not exist: {}'.format(dir_path)
    except NotADirectoryError:
        return 'Not a directory: {}'.format(dir_path)
    return None


def execute_with_sh_result(destination: DestinationPath,
                           sds: SandboxDirectoryStructure) -> sh.SuccessOrHardError:
    error_message = change_dir(destination, sds)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)
