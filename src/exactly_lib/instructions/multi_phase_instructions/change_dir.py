import os

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help_texts import instruction_arguments, formatting
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import concepts, syntax_elements
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResultAsHardError
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import InstructionPartsParser
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation
from exactly_lib.instructions.utils.parse.token_stream_parse import TokenParserExtra
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.util.cli_syntax.elements import argument as a


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str,
                 is_after_act_phase: bool,
                 is_in_assert_phase: bool = False):
        self.is_after_act_phase = is_after_act_phase
        self.relativity_options = relativity_options(is_after_act_phase)
        self.cwd_concept_name = formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO)
        super().__init__(name, {
            'cwd_concept': self.cwd_concept_name,
            'dir_argument': _DIR_ARGUMENT.name,
        },
                         is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._format('Sets the {cwd_concept}')

    def _main_description_rest_body(self) -> list:
        return self._paragraphs(_NO_DIR_ARG_MEANING)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(self._cl_syntax_for_args([
                a.Single(a.Multiplicity.OPTIONAL,
                         _DIR_ARGUMENT),
            ])),
        ]

    def syntax_element_descriptions(self) -> list:
        return relative_path_options_documentation.path_elements(
            _DIR_ARGUMENT.name,
            self.relativity_options.options)

    def see_also_targets(self) -> list:
        return cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO,
        ])


_NO_DIR_ARG_MEANING = """\
Omitting the {dir_argument} is the same as giving ".".
"""


class InstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self, destination: FileRefResolver):
        self.destination = destination

    @property
    def symbol_usages(self) -> list:
        return self.destination.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        return self.custom_main(environment.path_resolving_environment)

    def custom_main(self, environment: PathResolvingEnvironmentPostSds) -> str:
        """
        :return: None iff success. Otherwise an error message.
        """
        dir_path_ref = self.destination.resolve(environment.symbols)
        dir_path = dir_path_ref.value_post_sds(environment.sds)
        try:
            os.chdir(str(dir_path))
        except FileNotFoundError:
            return 'Directory does not exist: {}'.format(dir_path_ref)
        except NotADirectoryError:
            return 'Not a directory: {}'.format(dir_path_ref)
        return None


class EmbryoParser(embryo.InstructionEmbryoParserThatConsumesCurrentLine):
    def __init__(self, is_after_act_phase: bool):
        self.is_after_act_phase = is_after_act_phase

    def _parse(self, rest_of_line: str) -> InstructionEmbryo:
        rel_opt_arg_conf = relativity_options(self.is_after_act_phase)
        tokens = TokenParserExtra(TokenStream(rest_of_line))

        target_file_ref = tokens.consume_file_ref(rel_opt_arg_conf)
        tokens.report_superfluous_arguments_if_not_at_eol()
        return InstructionEmbryo(target_file_ref)


def parts_parser(is_after_act_phase: bool) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(EmbryoParser(is_after_act_phase),
                                       MainStepResultTranslatorForErrorMessageStringResultAsHardError())


_DIR_ARGUMENT = instruction_arguments.PATH_ARGUMENT


def relativity_options(is_after_act_phase: bool) -> RelOptionArgumentConfiguration:
    accepted = [RelOptionType.REL_ACT,
                RelOptionType.REL_TMP]
    if is_after_act_phase:
        accepted.append(RelOptionType.REL_RESULT)
    variants = PathRelativityVariants(set(accepted), True)
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(variants,
                                                                  RelOptionType.REL_CWD),
                                          _DIR_ARGUMENT.name,
                                          False)
