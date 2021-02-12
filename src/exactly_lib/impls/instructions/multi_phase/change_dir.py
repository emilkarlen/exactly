import os
from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription, \
    invokation_variant_from_args
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import concepts, syntax_elements
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils import instruction_part_utils
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import InstructionPartsParser
from exactly_lib.impls.types.path import path_err_msgs, parse_path, relative_path_options_documentation
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPostSds
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


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
        return self._tp.format('Sets the {cwd_concept}')

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY,
                         _DIR_ARGUMENT),
            ]),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return relative_path_options_documentation.path_elements(
            _DIR_ARGUMENT.name,
            self.relativity_options.options)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO,
        ])


class InstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[Optional[TextRenderer]]):
    def __init__(self, destination: PathSdv):
        self.destination = destination

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.destination.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> Optional[TextRenderer]:
        return self.custom_main(environment.path_resolving_environment)

    def custom_main(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        """
        :return: None iff success. Otherwise an error message.
        """

        path = self.destination.resolve(environment.symbols).value_post_sds__d(environment.sds)

        def error(header: str) -> TextRenderer:
            return path_err_msgs.line_header__primitive(
                header,
                path.describer,
            )

        try:
            os.chdir(str(path.primitive))
        except FileNotFoundError:
            return error('Directory does not exist')
        except NotADirectoryError:
            return error('Not a directory')
        return None


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[Optional[TextRenderer]]):
    def __init__(self, is_after_act_phase: bool):
        self.is_after_act_phase = is_after_act_phase
        self._path_parser = parse_path.PathParser(relativity_options(is_after_act_phase))

    def _parse_from_tokens(self, token_parser: TokenParser) -> InstructionEmbryo:
        path = self._path_parser.parse_from_token_parser(token_parser)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        return InstructionEmbryo(path)


def parts_parser(is_after_act_phase: bool) -> InstructionPartsParser:
    return instruction_part_utils.PartsParserFromEmbryoParser(
        EmbryoParser(is_after_act_phase),
        instruction_part_utils.MainStepResultTranslatorForTextRendererAsHardError()
    )


_DIR_ARGUMENT = syntax_elements.PATH_SYNTAX_ELEMENT.argument


def relativity_options(is_after_act_phase: bool) -> RelOptionArgumentConfiguration:
    accepted = [RelOptionType.REL_ACT,
                RelOptionType.REL_TMP,
                RelOptionType.REL_CWD]
    if is_after_act_phase:
        accepted.append(RelOptionType.REL_RESULT)
    variants = PathRelativityVariants(set(accepted), True)
    return RelOptionArgumentConfiguration(RelOptionsConfiguration(variants,
                                                                  RelOptionType.REL_CWD),
                                          _DIR_ARGUMENT.name,
                                          True)
