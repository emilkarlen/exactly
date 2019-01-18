from abc import ABC, abstractmethod
from typing import Optional, Tuple

from exactly_lib.cli.program_modes.symbol.impl.completion_reporter import CompletionReporter
from exactly_lib.cli.program_modes.symbol.impl.reports.report_environment import Environment
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo, ContextAnd
from exactly_lib.common import result_reporting
from exactly_lib.common.err_msg.definitions import Blocks
from exactly_lib.definitions.entity import concepts
from exactly_lib.section_document.source_location import SourceLocationInfo, SourceLocationPath
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.util.string import inside_parens


class _Presenter(ABC):
    def __init__(self,
                 completion_reporter: CompletionReporter,
                 definition: SymbolDefinitionInfo):
        self.printer = completion_reporter.out_printer
        self.phase = definition.phase
        self.definition = definition

    @abstractmethod
    def present(self):
        pass

    def _single_line_info(self):
        definition = self.definition

        output = ' '.join([
            definition.type_identifier(),
            inside_parens(len(definition.references)),
            definition.name(),
        ])
        self.printer.write_line(output)

    def _rest(self):
        pass


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
            self._presenter(mb_definition).present()

        return self._completion_reporter.report_success()

    def _presenter(self, definition: SymbolDefinitionInfo) -> _Presenter:
        if self._list_references:
            return _ReferencesPresenter(self._completion_reporter, definition)
        else:
            return _DefinitionPresenter(self._completion_reporter, definition)

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
    def present(self):
        self._single_line_info()
        self._rest()

    def _rest(self):
        result_reporting.output_location(
            self.printer,
            self._get_source_location_path(self.definition.definition.resolver_container.source_location),
            self.phase.section_name,
            None,
            append_blank_line_if_any_output=False)

    @staticmethod
    def _get_source_location_path(sli: Optional[SourceLocationInfo]) -> Optional[SourceLocationPath]:
        return None if sli is None else sli.source_location_path


class _ReferencesPresenter(_Presenter):
    def present(self):
        first = True
        for reference in self.definition.references:
            if first:
                first = False
            else:
                self.printer.write_line('')
            location, source = self._location_and_source_blocks(reference)
            result_reporting.output_location_with_source_block(
                self.printer,
                location,
                source,
                reference.phase().section_name,
                None,
                append_blank_line_if_any_output=False
            )

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
