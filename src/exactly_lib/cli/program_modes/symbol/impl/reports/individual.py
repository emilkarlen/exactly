from abc import ABC
from typing import Optional, Sequence, List

from exactly_lib.cli.program_modes.symbol.impl.report import ReportGenerator, Report, ReportBlock
from exactly_lib.cli.program_modes.symbol.impl.reports import value_presentation
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo, ContextAnd, \
    DefinitionsResolver
from exactly_lib.common.report_rendering.parts import source_location
from exactly_lib.definitions.entity import concepts, all_entity_types
from exactly_lib.section_document.source_location import SourceLocationInfo, SourceLocationPath
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct import structure as struct
from exactly_lib.util.simple_textstruct.rendering import component_renderers as rend, blocks, line_objects
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock
from exactly_lib.util.str_.misc_formatting import inside_parens
from exactly_lib.util.symbol_table import SymbolTable

BUILTIN_SYMBOL_DEFINITION_SOURCE_LINE = all_entity_types.BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.name.singular


class IndividualReportGenerator(ReportGenerator):
    def __init__(self,
                 symbol_name: str,
                 list_references: bool,
                 builtin_symbols: SymbolTable,
                 ):
        self._symbol_name = symbol_name
        self._list_references = list_references
        self._builtin_symbols = builtin_symbols

    def generate(self, definitions_resolver: DefinitionsResolver) -> Report:
        definitions = list(definitions_resolver.definitions())

        mb_definition = self._lookup(definitions)

        if mb_definition is None:
            return _SymbolNotFoundReport(self._symbol_name)
        else:
            if self._list_references:
                return _ReferencesReport(mb_definition)
            else:
                return _DefinitionReport(mb_definition, definitions, self._builtin_symbols)

    def _lookup(self, definitions: List[SymbolDefinitionInfo]) -> Optional[SymbolDefinitionInfo]:
        name = self._symbol_name
        for definition in definitions:
            if name == definition.name():
                return definition

        return None


class SymbolNotFoundBlock(ReportBlock):
    def __init__(self,
                 symbol_name: str,
                 ):
        self._symbol_name = symbol_name

    def render(self) -> MajorBlock:
        header = ' '.join([concepts.SYMBOL_CONCEPT_INFO.singular_name.capitalize(),
                           'not in test case:',
                           self._symbol_name])
        return blocks.MajorBlockOfSingleLineObject(
            line_objects.StringLineObject(header)
        ).render()


class DefinitionShortInfoBlock(ReportBlock):
    def __init__(self, definition: SymbolDefinitionInfo):
        self.definition = definition

    def render(self) -> MajorBlock:
        return MajorBlock([
            MinorBlock([
                struct.LineElement(struct.StringLineObject(self._single_line_info_str())),
            ])
        ])

    def _single_line_info_str(self) -> str:
        definition = self.definition

        return ' '.join([
            definition.type_identifier(),
            inside_parens(len(definition.references)),
            definition.name(),
        ])


class DefinitionSourceBlock(ReportBlock):
    _RENDERER_OF_BUILTIN = blocks.MajorBlockOfSingleLineObject(
        line_objects.StringLineObject(BUILTIN_SYMBOL_DEFINITION_SOURCE_LINE)
    )

    def __init__(self,
                 phase_if_user_defined_symbol: Optional[Phase],
                 source_location: Optional[SourceLocationInfo],
                 ):
        self.phase_if_user_defined_symbol = phase_if_user_defined_symbol
        self.source_location = source_location

    def render(self) -> MajorBlock:
        renderer = (
            self._RENDERER_OF_BUILTIN
            if self.phase_if_user_defined_symbol is None
            else
            self._renderer_of_user_defined()
        )
        return renderer.render()

    def _renderer_of_user_defined(self) -> Renderer[MajorBlock]:
        return source_location.location_block_renderer(
            self._get_source_location_path(self.source_location),
            self.phase_if_user_defined_symbol.section_name,
            None,
        )

    @staticmethod
    def _get_source_location_path(sli: Optional[SourceLocationInfo]) -> Optional[SourceLocationPath]:
        return None if sli is None else sli.source_location_path


class ReferenceSourceLocationBlock(ReportBlock):
    def __init__(self,
                 reference: ContextAnd[SymbolReference],
                 ):
        self.reference = reference

    def render(self) -> MajorBlock:
        reference = self.reference
        source_info = reference.source_info()
        source_location_info = source_info.source_location_info
        if source_location_info is not None:
            return source_location.location_block_renderer(
                source_location_info.source_location_path,
                reference.phase().section_name,
                None,
            ).render()
        elif source_info.source_lines is not None:
            return rend.MajorBlockR(
                source_location.source_lines_in_section_block_renderer(
                    reference.phase().section_name,
                    source_info.source_lines,
                )).render()
        else:
            raise ValueError('inconsistency of source info: ' + str(source_info))


class _SymbolNotFoundReport(Report):
    def __init__(self,
                 symbol_name: str,
                 ):
        self._symbol_name = symbol_name

    @property
    def is_success(self) -> bool:
        return False

    def blocks(self) -> Sequence[ReportBlock]:
        return [
            SymbolNotFoundBlock(self._symbol_name)
        ]


class _SuccessfulReportBase(Report, ABC):
    def __init__(self, definition: SymbolDefinitionInfo):
        self.definition = definition

    @property
    def is_success(self) -> bool:
        return True


class _DefinitionReport(_SuccessfulReportBase):
    def __init__(self,
                 definition: SymbolDefinitionInfo,
                 all_definitions: List[SymbolDefinitionInfo],
                 builtin_symbols: SymbolTable,
                 ):
        super().__init__(definition)
        self._all_definitions = all_definitions
        self._builtin_symbols = builtin_symbols

    def blocks(self) -> Sequence[ReportBlock]:
        definition = self.definition
        return [
            DefinitionShortInfoBlock(definition),
            DefinitionSourceBlock(definition.phase,
                                  definition.definition.symbol_container.source_location),
            self._get_resolved_value_presentation(),
        ]

    def _get_resolved_value_presentation(self) -> value_presentation.ResolvedValuePresentationBlock:
        sdv = self.definition.definition.symbol_container.sdv
        definitions = [
            definition_info.definition
            for definition_info in self._all_definitions
        ]
        constructor = value_presentation.PresentationBlockConstructor(definitions, self._builtin_symbols)
        return constructor.block_for(sdv)


class _ReferencesReport(_SuccessfulReportBase):
    def blocks(self) -> Sequence[ReportBlock]:
        ret_val = []
        for reference in self.definition.references:
            ret_val += self._blocks_renderer(reference)

        return ret_val

    @staticmethod
    def _blocks_renderer(reference: ContextAnd[SymbolReference]) -> Sequence[ReportBlock]:
        source_info = reference.source_info()
        source_location_info = source_info.source_location_info
        if source_location_info is not None or source_info.source_lines is not None:
            return [
                ReferenceSourceLocationBlock(reference)
            ]
        else:
            return []
