import os

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.concepts.plain_concepts.current_working_directory import CURRENT_WORKING_DIRECTORY_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.instructions.utils.arg_parse.parse_file_ref import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.documentation import documentation_text as dt, relative_path_options_documentation
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.value_definition.concrete_values import FileRefResolver


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str,
                 is_after_act_phase: bool,
                 is_in_assert_phase: bool = False):
        self.is_after_act_phase = is_after_act_phase
        self.relativity_options = _relativity_options(is_after_act_phase)
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
            self.relativity_options.options.default_option) +
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
        return relative_path_options_documentation.relativity_syntax_element_descriptions(
            _DIR_ARGUMENT,
            self.relativity_options.options)

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(self.relativity_options.options)
        from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
        from exactly_lib.help.concepts.names_and_cross_references import SANDBOX_CONCEPT_INFO
        rel_path_doc.add_concepts_if_not_listed(concepts,
                                                [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO,
                                                 SANDBOX_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


_NO_DIR_ARG_MEANING = """\
Omitting the {dir_argument} is the same as giving ".".
"""


def parse(argument: str, is_after_act_phase: bool) -> FileRefResolver:
    relativity_options = _relativity_options(is_after_act_phase)
    source = TokenStream2(argument)
    destination_path = parse_file_ref(source, relativity_options)
    if not source.is_null:
        raise SingleInstructionInvalidArgumentException('Superfluous arguments: {}'.format(source.remaining_source))
    return destination_path


def change_dir(destination: FileRefResolver,
               environment: PathResolvingEnvironmentPostSds) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """
    dir_path_ref = destination.resolve(environment.value_definitions)
    dir_path = dir_path_ref.file_path_post_sds(environment.sds)
    try:
        os.chdir(str(dir_path))
    except FileNotFoundError:
        return 'Directory does not exist: {}'.format(dir_path_ref)
    except NotADirectoryError:
        return 'Not a directory: {}'.format(dir_path_ref)
    return None


def execute_with_sh_result(destination: FileRefResolver,
                           environment: PathResolvingEnvironmentPostSds) -> sh.SuccessOrHardError:
    error_message = change_dir(destination, environment)
    return sh.new_sh_success() if error_message is None else sh.new_sh_hard_error(error_message)


_DIR_ARGUMENT = dt.DIR_ARGUMENT


def _relativity_options(is_after_act_phase: bool) -> RelOptionArgumentConfiguration:
    accepted = [RelOptionType.REL_ACT,
                RelOptionType.REL_TMP]
    if is_after_act_phase:
        accepted.append(RelOptionType.REL_RESULT)
    variants = PathRelativityVariants(set(accepted), True)
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(variants,
                                                                  True,
                                                                  RelOptionType.REL_CWD),
                                          _DIR_ARGUMENT.name,
                                          False)
