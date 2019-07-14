from abc import ABC, abstractmethod
from typing import Optional, Tuple, Sequence

from exactly_lib.cli.program_modes.symbol.impl.reports.report_environment import Environment
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo, ContextAnd
from exactly_lib.common import result_reporting
from exactly_lib.common import result_reporting2
from exactly_lib.common.err_msg.definitions import Blocks
from exactly_lib.common.report_rendering import combinators as comb
from exactly_lib.common.report_rendering.trace_doc import Renderer
from exactly_lib.definitions.entity import concepts
from exactly_lib.section_document.source_location import SourceLocationInfo, SourceLocationPath
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.simple_textstruct import structure as struct
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock
from exactly_lib.util.string import inside_parens


class _Presenter(ABC):
    def __init__(self, definition: SymbolDefinitionInfo):
        self.phase = definition.phase
        self.definition = definition

    @abstractmethod
    def present2(self) -> Renderer[Sequence[MajorBlock]]:
        pass

    def _single_line_info_str(self) -> str:
        definition = self.definition

        return ' '.join([
            definition.type_identifier(),
            inside_parens(len(definition.references)),
            definition.name(),
        ])


class ReportGenerator:
    def __init__(self,
                 environment: Environment,
                 symbol_name: str,
                 list_references: bool
                 ):
        self._symbol_name = symbol_name
        self._list_references = list_references
        self._output = environment.output
        self._completion_reporter = environment.completion_reporter
        self._definitions_resolver = environment.definitions_resolver

    def generate(self) -> int:
        mb_definition = self._lookup()

        if mb_definition is None:
            return self._not_found()
        else:
            result_reporting2.print_major_blocks(self._presenter(mb_definition).present2(),
                                                 self._completion_reporter.out_printer)

        return self._completion_reporter.report_success()

    def _presenter(self, definition: SymbolDefinitionInfo) -> _Presenter:
        if self._list_references:
            return _ReferencesPresenter(definition)
        else:
            return _DefinitionPresenter(definition)

    def _lookup(self) -> Optional[SymbolDefinitionInfo]:
        name = self._symbol_name
        for definition in self._definitions_resolver.definitions():
            if name == definition.name():
                return definition

        return None

    def _not_found(self) -> int:
        header = concepts.SYMBOL_CONCEPT_INFO.singular_name.capitalize() + ' not in test case: '
        self._completion_reporter.err_printer.write_line(header + self._symbol_name)
        return self._completion_reporter.symbol_not_found()


class _DefinitionPresenter(_Presenter):
    def present2(self) -> Renderer[Sequence[MajorBlock]]:
        major_block = comb.MajorBlockFromMinorBlocks(
            comb.Concatenation([
                comb.ASequence([self._single_line_info_minor_block()]),
                result_reporting2.location_minor_blocks_renderer(
                    self._get_source_location_path(self.definition.definition.resolver_container.source_location),
                    self.phase.section_name,
                    None,
                )])
        )
        return comb.ASequence([major_block])

    def _single_line_info_minor_block(self) -> Renderer[MinorBlock]:
        return comb.Constant(
            MinorBlock([struct.LineElement(struct.StringLineObject(self._single_line_info_str()))])
        )

    @staticmethod
    def _get_source_location_path(sli: Optional[SourceLocationInfo]) -> Optional[SourceLocationPath]:
        return None if sli is None else sli.source_location_path


class _ReferencesPresenter(_Presenter):
    def present2(self) -> Renderer[Sequence[MajorBlock]]:
        return comb.Concatenation([
            self._blocks_renderer(reference)
            for reference in self.definition.references
        ])

    @staticmethod
    def _blocks_renderer(reference: ContextAnd[SymbolReference]) -> Renderer[Sequence[MajorBlock]]:
        source_info = reference.source_info()
        source_location_info = source_info.source_location_info
        if source_location_info is not None:
            return result_reporting2.location_blocks_renderer(
                source_location_info.source_location_path,
                reference.phase().section_name,
                None,
            )
        elif source_info.source_lines is not None:
            return comb.ASequence([
                comb.MajorBlockFromMinorBlocks(
                    result_reporting2.source_lines_in_section_block_renderer(
                        reference.phase().section_name,
                        source_info.source_lines,
                    ))
            ])
        else:
            return comb.ASequence([])

    @staticmethod
    def _location_and_source_blocks(reference: ContextAnd[SymbolReference]) -> Tuple[Blocks, Blocks]:
        source_info = reference.source_info()
        if source_info.source_location_info is not None:
            return result_reporting.location_path_and_source_blocks(
                source_info.source_location_info.source_location_path)
        elif source_info.source_lines is not None:
            return [], result_reporting.source_lines_blocks(source_info.source_lines)
        else:
            return [], []
