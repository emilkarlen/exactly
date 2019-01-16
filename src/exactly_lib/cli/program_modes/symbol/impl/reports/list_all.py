import functools
from typing import Callable, List, Iterator

from exactly_lib.cli.program_modes.symbol.impl.reports.report_environment import Environment
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.string import lines_content


class _TypeReportingInfo:
    def __init__(self, value_type: ValueType):
        self.type_info = ANY_TYPE_INFO_DICT[value_type]
        self.identifier_length = len(self.type_info.identifier)
        self.identifier = self.type_info.identifier


class ReportGenerator:
    def __init__(self, environment: Environment):
        self._output = environment.output
        self._completion_reporter = environment.completion_reporter
        self.definitions_resolver = environment.definitions_resolver
        self._type_info_dict = {
            value_type: _TypeReportingInfo(value_type)
            for value_type in ValueType
        }

    def list(self) -> int:
        output_lines = self._get_list_lines(self.definitions_resolver.definitions())
        self._output.out.write(lines_content(output_lines))
        return self._completion_reporter.report_success()

    def _get_list_lines(self, symbols: Iterator[SymbolDefinitionInfo]) -> List[str]:
        symbol_list = list(symbols)
        symbol_line_formatter = self._symbol_line_formatter(symbol_list)
        return [
            symbol_line_formatter(symbol)
            for symbol in symbol_list
        ]

    def _symbol_line_formatter(self, symbols: List[SymbolDefinitionInfo]) -> Callable[[SymbolDefinitionInfo], str]:
        def get_identifier_length(symbol: SymbolDefinitionInfo) -> int:
            return self._type_info_dict[symbol.value_type()].identifier_length

        max_type_identifier_len = functools.reduce(_max_int,
                                                   map(get_identifier_length, symbols),
                                                   0)
        max_num_refs_len = functools.reduce(_max_int,
                                            map(SymbolDefinitionInfo.num_refs_str_length, symbols),
                                            0)

        type_formatting_string = '%-{}s %-{}s'.format(max_type_identifier_len,
                                                      max_num_refs_len)

        def ret_val(symbol: SymbolDefinitionInfo) -> str:
            return (type_formatting_string % (symbol.type_identifier(),
                                              symbol.num_refs_str()) +
                    ' ' +
                    symbol.name()
                    )

        return ret_val


def _max_int(x: int, y: int) -> int:
    return max(x, y)
