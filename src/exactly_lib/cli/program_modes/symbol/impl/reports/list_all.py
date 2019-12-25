import functools
from typing import Callable, List, Iterator, Sequence

from exactly_lib.cli.program_modes.symbol.impl.report import ReportGenerator, Report, ReportBlock
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SymbolDefinitionInfo, DefinitionsResolver
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.string import inside_parens


class ListReportGenerator(ReportGenerator):
    def generate(self, definitions_resolver: DefinitionsResolver) -> Report:
        return _ListReport(list(definitions_resolver.definitions()))


class SymbolListBlock(ReportBlock):
    def __init__(self, definitions: Sequence[SymbolDefinitionInfo]):
        self.definitions = definitions

    def render(self) -> MajorBlock:
        def_report_infos = map(mk_single_def_report_info, self.definitions)

        definition_lines = _get_list_lines(def_report_infos)

        return MajorBlock([
            structure.MinorBlock([
                structure.LineElement(
                    structure.StringLinesObject(definition_lines)
                )
            ])
        ])


class _ListReport(Report):
    def __init__(self, definitions: Sequence[SymbolDefinitionInfo]):
        self.definitions = definitions

    @property
    def is_success(self) -> bool:
        return True

    def blocks(self) -> Sequence[ReportBlock]:
        return [
            SymbolListBlock([
                definition
                for definition in self.definitions
                if definition.is_user_defined()
            ])
        ]


class _SingleDefinitionReportInfo:
    def __init__(self,
                 name: str,
                 value_type: ValueType,
                 num_refs: int):
        self._name = name
        self._value_type = value_type
        self._num_refs = num_refs
        self._num_refs_str = _format_num_refs_info(num_refs)
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


def _format_num_refs_info(num_refs: int) -> str:
    return inside_parens(num_refs)


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
