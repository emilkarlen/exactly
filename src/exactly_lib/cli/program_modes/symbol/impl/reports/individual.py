from typing import Optional

from exactly_lib.cli.program_modes.symbol.impl.completion_reporter import CompletionReporter
from exactly_lib.cli.program_modes.symbol.impl.reports.report_environment import Environment
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo
from exactly_lib.common import result_reporting
from exactly_lib.util.string import inside_parens


class _Presenter:
    def __init__(self,
                 completion_reporter: CompletionReporter,
                 definition: SymbolDefinitionInfo):
        self.printer = completion_reporter.out_printer
        self.phase = definition.phase
        self.definition = definition

    def present(self):
        self._single_line_info()
        self._rest()

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
        self._completion_reporter.err_printer.write_line('Symbol not found: ' + self._symbol_name)
        return self._completion_reporter.symbol_not_found()


class _DefinitionPresenter(_Presenter):
    def _rest(self):
        mb_source_location = self.definition.definition.resolver_container.source_location
        if mb_source_location is None:
            return
        result_reporting.output_location(self.printer,
                                         mb_source_location.source_location_path,
                                         self.phase.section_name,
                                         None,
                                         append_blank_line_if_any_output=False)


class _ReferencesPresenter(_Presenter):
    def _rest(self):
        num_refs = len(self.definition.references)
        if num_refs != 0:
            self.printer.write_line(str(num_refs))
