from typing import Optional

from exactly_lib.cli.program_modes.symbol.impl.reports.report_environment import Environment
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo


class ReportGenerator:
    def __init__(self,
                 environment: Environment,
                 symbol_name: str,
                 ):
        self._symbol_name = symbol_name
        self._output = environment.output
        self._completion_reporter = environment.completion_reporter
        self._definitions_resolver = environment.definitions_resolver

    def generate(self) -> int:
        mb_definition = self._lookup()
        if mb_definition is None:
            return self._not_found()
        else:
            self._present(mb_definition)
        return self._completion_reporter.report_success()

    def _lookup(self) -> Optional[SymbolDefinitionInfo]:
        name = self._symbol_name
        for definition in self._definitions_resolver.definitions():
            if name == definition.name():
                return definition

        return None

    def _present(self, definition: SymbolDefinitionInfo):
        output = ' '.join([
            definition.type_identifier(),
            str(len(definition.references)),
            definition.name(),
        ])
        self._completion_reporter.out_printer.write_line(output)

    def _not_found(self) -> int:
        self._completion_reporter.err_printer.write_line('Symbol not found: ' + self._symbol_name)
        return self._completion_reporter.symbol_not_found()
