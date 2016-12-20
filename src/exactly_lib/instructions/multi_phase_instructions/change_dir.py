import os

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.concepts.plain_concepts.current_working_directory import CURRENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.arg_parse.parse_destination_path import parse_destination_path
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.instructions.utils.destination_path import *
from exactly_lib.instructions.utils.documentation import documentation_text as dt, relative_path_options_documentation
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.cli_syntax.elements import argument as a


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        self.cwd_concept_name = formatting.concept(CURRENT_WORKING_DIRECTORY_CONCEPT.name().singular)
        super().__init__(name, {
            'cwd_concept': self.cwd_concept_name,
            'dir_argument': _DIR_ARGUMENT.name,
        },
                         is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._format('Sets the {cwd_concept}')

    def _main_description_rest_body(self) -> list:
        return (relative_path_options_documentation.default_relativity_for_rel_opt_type(
            _DIR_ARGUMENT.name,
            _RELATIVITY_OPTIONS.options.default_option) +
                self._paragraphs(_NO_DIR_ARG_MEANING) +
                dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                relative_path_options_documentation.OPTIONAL_RELATIVITY_ARGUMENT_USAGE,
                a.Single(a.Multiplicity.OPTIONAL,
                         _DIR_ARGUMENT),
            ])),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            relative_path_options_documentation.relativity_syntax_element_description(
                _DIR_ARGUMENT,
                _RELATIVITY_OPTIONS.options.accepted_options),
        ]

    def _see_also_cross_refs(self) -> list:
        from exactly_lib.help.concepts.plain_concepts.sandbox import \
            SANDBOX_CONCEPT
        concepts = rel_path_doc.see_also_concepts(_RELATIVITY_OPTIONS.options.accepted_options)
        rel_path_doc.add_concepts_if_not_listed(concepts,
                                                [CURRENT_WORKING_DIRECTORY_CONCEPT,
                                                 SANDBOX_CONCEPT])
        return [concept.cross_reference_target() for concept in concepts]


_NO_DIR_ARG_MEANING = """\
Omitting the {dir_argument} is the same as giving ".".
"""


def parse(argument: str) -> DestinationPath:
    arguments = split_arguments_list_string(argument)

    (destination_path, remaining_arguments) = parse_destination_path(_RELATIVITY_OPTIONS, False, arguments)
    if remaining_arguments:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(remaining_arguments))
    return destination_path


def change_dir(destination: DestinationPath,
               sds: SandboxDirectoryStructure) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path = destination.resolved_path_if_not_rel_home(sds)
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


_DIR_ARGUMENT = dt.DIR_ARGUMENT

_RELATIVITY_OPTIONS = argument_configuration_for_file_creation(_DIR_ARGUMENT.name)
