from abc import ABC
from typing import Optional, Sequence

from exactly_lib.cli.program_modes.symbol.impl.report import ReportGenerator, Report, ReportBlock
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo, ContextAnd, \
    DefinitionsResolver
from exactly_lib.common.report_rendering.parts import source_location
from exactly_lib.definitions.entity import concepts
from exactly_lib.section_document.source_location import SourceLocationInfo, SourceLocationPath
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.util.simple_textstruct import structure as struct
from exactly_lib.util.simple_textstruct.rendering import component_renderers as rend, blocks, line_objects
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock
from exactly_lib.util.string import inside_parens


class IndividualReportGenerator(ReportGenerator):
    def __init__(self,
                 symbol_name: str,
                 list_references: bool
                 ):
        self._symbol_name = symbol_name
        self._list_references = list_references

    def generate(self, definitions_resolver: DefinitionsResolver) -> Report:
        mb_definition = self._lookup(definitions_resolver)

        if mb_definition is None:
            return _SymbolNotFoundReport(self._symbol_name)
        else:
            if self._list_references:
                return _ReferencesReport(mb_definition)
            else:
                return _DefinitionReport(mb_definition)

    def _lookup(self, definitions_resolver: DefinitionsResolver) -> Optional[SymbolDefinitionInfo]:
        name = self._symbol_name
        for definition in definitions_resolver.definitions():
            if name == definition.name():
                return definition

        return None


class SymbolNotFoundBlock(ReportBlock):
    def __init__(self,
                 symbol_name: str,
                 ):
        self._symbol_name = symbol_name

    def render(self) -> MajorBlock:
        header = concepts.SYMBOL_CONCEPT_INFO.singular_name.capitalize() + ' not in test case: '
        s = header + self._symbol_name
        return blocks.MajorBlockOfSingleLineObject(
            line_objects.StringLineObject(s)
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
    def __init__(self,
                 phase: Phase,
                 source_location: Optional[SourceLocationInfo],
                 ):
        self.phase = phase
        self.source_location = source_location

    def render(self) -> MajorBlock:
        renderer = source_location.location_block_renderer(
            self._get_source_location_path(self.source_location),
            self.phase.section_name,
            None,
        )
        return renderer.render()

    @staticmethod
    def _get_source_location_path(sli: Optional[SourceLocationInfo]) -> Optional[SourceLocationPath]:
        return None if sli is None else sli.source_location_path


class SourceLocationBlock(ReportBlock):
    def __init__(self,
                 definition: SymbolDefinitionInfo,
                 reference: ContextAnd[SymbolReference],
                 ):
        self.phase = definition.phase
        self.definition = definition
        self._reference = reference

    def render(self) -> MajorBlock:
        reference = self._reference
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
            raise ValueError('inconsistency')


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
    def blocks(self) -> Sequence[ReportBlock]:
        definition = self.definition
        return [
            DefinitionShortInfoBlock(definition),
            DefinitionSourceBlock(definition.phase,
                                  definition.definition.resolver_container.source_location),
        ]


class _ReferencesReport(_SuccessfulReportBase):
    def blocks(self) -> Sequence[ReportBlock]:
        ret_val = []
        for reference in self.definition.references:
            ret_val += self._blocks_renderer(reference)

        return ret_val

    def _blocks_renderer(self, reference: ContextAnd[SymbolReference]) -> Sequence[ReportBlock]:
        source_info = reference.source_info()
        source_location_info = source_info.source_location_info
        if source_location_info is not None or source_info.source_lines is not None:
            return [
                SourceLocationBlock(self.definition, reference)
            ]
        else:
            return []
