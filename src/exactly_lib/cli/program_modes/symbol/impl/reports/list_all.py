import functools
from typing import Callable, List, Iterator

from exactly_lib.cli.program_modes.symbol.impl.reports.report_environment import Environment
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.string import lines_content, inside_parens


class _SingleDefinitionReportInfo:
    def __init__(self,
                 name: str,
                 value_type: ValueType,
                 num_refs: int):
        self._name = name
        self._value_type = value_type
        self._num_refs = num_refs
        self._num_refs_str = format_num_refs_info(num_refs)
        self._type_identifier = ANY_TYPE_INFO_DICT[self.value_type()].identifier

    def name(self) -> str:
        return self._name

    def name_length(self) -> int:
        return len(self._name)

    def value_type(self) -> ValueType:
        return self._value_type

    def type_identifier(self) -> str:
        return self._type_identifier

    def type_identifier_length(self) -> int:
        return len(self._type_identifier)

    def num_refs_str(self) -> str:
        return self._num_refs_str

    def num_refs_str_length(self) -> int:
        return len(self._num_refs_str)


def mk_single_def_report_info(definition: SymbolDefinitionInfo) -> _SingleDefinitionReportInfo:
    return _SingleDefinitionReportInfo(definition.name(),
                                       definition.value_type(),
                                       len(definition.references))


def format_num_refs_info(num_refs: int) -> str:
    return inside_parens(num_refs)


class ReportGenerator:
    def __init__(self, environment: Environment):
        self._output = environment.output
        self._completion_reporter = environment.completion_reporter
        self.definitions_resolver = environment.definitions_resolver

    def generate(self) -> int:
        definitions = self.definitions_resolver.definitions()
        def_report_infos = map(mk_single_def_report_info, definitions)

        output_lines = _get_list_lines(def_report_infos)

        self._output.out.write(lines_content(output_lines))
        return self._completion_reporter.report_success()


def _get_list_lines(symbols: Iterator[_SingleDefinitionReportInfo]) -> List[str]:
    symbol_list = list(symbols)
    symbol_line_formatter = _symbol_line_formatter(symbol_list)
    return [
        symbol_line_formatter(symbol)
        for symbol in symbol_list
    ]


def _symbol_line_formatter(symbols: List[_SingleDefinitionReportInfo]
                           ) -> Callable[[_SingleDefinitionReportInfo], str]:
    max_type_identifier_len = functools.reduce(_max_int,
                                               map(_SingleDefinitionReportInfo.type_identifier_length,
                                                   symbols),
                                               0)
    max_num_refs_len = functools.reduce(_max_int,
                                        map(_SingleDefinitionReportInfo.num_refs_str_length, symbols),
                                        0)

    type_formatting_string = '%-{}s %-{}s'.format(max_type_identifier_len,
                                                  max_num_refs_len)

    def ret_val(symbol: _SingleDefinitionReportInfo) -> str:
        return (type_formatting_string % (symbol.type_identifier(),
                                          symbol.num_refs_str()) +
                ' ' +
                symbol.name()
                )

    return ret_val


def _max_int(x: int, y: int) -> int:
    return max(x, y)
