from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, \
    InvokationVariant
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import file_types
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils import instruction_part_utils
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.impls.types.files_source import documentation as _fs_doc
from exactly_lib.impls.types.files_source import parse as _parse_fs
from exactly_lib.impls.types.files_source.file_maker import FileMakerSdv
from exactly_lib.impls.types.files_source.impl import parse_file_list
from exactly_lib.impls.types.path import parse_path, relative_path_options_documentation as rel_path_doc
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.sdv_structure import SymbolUsage, references_from_objects_with_symbol_references
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import SdvValidator
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import argument_configuration_for_file_creation
from exactly_lib.util.symbol_table import SymbolTable


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, _FORMAT_MAP, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._tp.format('Creates or modifies {dir_file_type:a}')

    def invokation_variants(self) -> List[InvokationVariant]:
        rendering_env = _fs_doc.FileSpecRenderingEnvironment(
            syntax_elements.PATH_SYNTAX_ELEMENT.single_mandatory,
            False,
            self._tp,
        )
        return [
            file_spec_form.invokation_variant(rendering_env)
            for file_spec_form in _fs_doc.file_spec_forms__dir()
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            rel_path_doc.path_element(
                _PATH_ARGUMENT.name,
                RELATIVITY_VARIANTS.options,
                custom_paragraphs_after=self._tp.fnap(_fs_doc.INTERMEDIATE_DIRS_ARE_CREATED)
            )
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return name_and_cross_ref.cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.FILES_SOURCE_SYNTAX_ELEMENT,
        ])


class TheInstructionEmbryo(embryo.PhaseAgnosticInstructionEmbryo[Optional[TextRenderer]]):
    def __init__(self,
                 dir_path_sdv: PathSdv,
                 file_maker: FileMakerSdv,
                 ):
        self._dir_path_sdv = dir_path_sdv
        self._file_maker = file_maker
        self._references = references_from_objects_with_symbol_references([dir_path_sdv, file_maker])

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._references

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.SdvValidatorFromDdvValidator(self._get_ddv_validator)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             ) -> Optional[TextRenderer]:
        destination_path = (
            self._dir_path_sdv.resolve(environment.symbols)
                .value_of_any_dependency__d(environment.tcds)
        )
        app_env = ApplicationEnvironment(os_services,
                                         environment.proc_exe_settings,
                                         environment.tmp_dir__path_access.paths_access,
                                         environment.mem_buff_size)
        file_maker = (
            self._file_maker.resolve(environment.symbols)
                .value_of_any_dependency(environment.tcds)
                .primitive(app_env)
        )
        return file_maker.make__translate_hard_error(destination_path)

    def _get_ddv_validator(self, symbols: SymbolTable) -> DdvValidator:
        return self._file_maker.resolve(symbols).validator


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[Optional[TextRenderer]]):
    def __init__(self):
        self._path_parser = parse_path.PathParser(RELATIVITY_VARIANTS)
        self._file_maker_parser = parse_file_list.ParserOfFileMaker.of_directory_maker(
            _parse_fs.FullFilesSourceParser()
        )

    def _parse_from_tokens(self, token_parser: TokenParser) -> TheInstructionEmbryo:
        path = self._path_parser.parse_from_token_parser(token_parser)
        file_maker = self._file_maker_parser.parse(token_parser)
        token_parser.report_superfluous_arguments_if_not_at_eol()
        return TheInstructionEmbryo(path, file_maker)


_PATH_ARGUMENT = syntax_elements.PATH_SYNTAX_ELEMENT.argument
RELATIVITY_VARIANTS = argument_configuration_for_file_creation(_PATH_ARGUMENT.name)

PARTS_PARSER = instruction_part_utils.PartsParserFromEmbryoParser(
    EmbryoParser(),
    instruction_part_utils.MainStepResultTranslatorForTextRendererAsHardError(),
)

_FORMAT_MAP = {
    'FILE_NAME': syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
    'dir_file_type': file_types.DIRECTORY,
    'dir_contents_type': syntax_elements.FILES_SOURCE_SYNTAX_ELEMENT.singular_name,
}
