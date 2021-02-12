from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, \
    invokation_variant_from_args, InvokationVariant
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils import instruction_part_utils
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.impls.types.path import path_err_msgs, parse_path, relative_path_options_documentation as rel_path_doc
from exactly_lib.impls.types.path.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPostSds
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, {}, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._tp.format('Creates a directory')

    def _notes__specific(self) -> List[ParagraphItem]:
        return self._tp.fnap(_NOTES)

    def invokation_variants(self) -> List[InvokationVariant]:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            RELATIVITY_VARIANTS.path_suffix_is_required)
        return [
            invokation_variant_from_args(arguments,
                                         []),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            rel_path_doc.path_element(_PATH_ARGUMENT.name,
                                      RELATIVITY_VARIANTS.options,
                                      docs.paras(the_path_of('a non-existing file.')))
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)


class TheInstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[Optional[TextRenderer]]):
    def __init__(self, dir_path_sdv: PathSdv):
        self.dir_path_sdv = dir_path_sdv

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.dir_path_sdv.references

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
        described_path = (
            self.dir_path_sdv.resolve(environment.symbols)
                .value_post_sds__d(environment.sds)
        )

        def error(header: str) -> TextRenderer:
            return path_err_msgs.line_header__primitive(
                header,
                described_path.describer,
            )

        path = described_path.primitive
        try:
            if path.is_dir():
                return None
        except NotADirectoryError:
            return error('Part of PATH exists, but is not a directory')
        try:
            path.mkdir(parents=True)
        except FileExistsError:
            return error('PATH exists, but is not a directory')
        except NotADirectoryError:
            return error('Clash with existing file')
        return None


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[Optional[TextRenderer]]):
    def __init__(self):
        self._path_parser = parse_path.PathParser(RELATIVITY_VARIANTS)

    def _parse_from_tokens(self, token_parser: TokenParser) -> TheInstructionEmbryo:
        path = self._path_parser.parse_from_token_parser(token_parser)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        return TheInstructionEmbryo(path)


_PATH_ARGUMENT = syntax_elements.PATH_SYNTAX_ELEMENT.argument
RELATIVITY_VARIANTS = argument_configuration_for_file_creation(_PATH_ARGUMENT.name)

PARTS_PARSER = instruction_part_utils.PartsParserFromEmbryoParser(
    EmbryoParser(),
    instruction_part_utils.MainStepResultTranslatorForTextRendererAsHardError(),
)

_NOTES = """\
Intermediate directories as created, if required.


If the directory already exists, nothing is done.
"""
