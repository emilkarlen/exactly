import itertools

import functools
from typing import TypeVar, Sequence, Callable, Iterable, List

from exactly_lib.cli.program_modes.symbol.completion_reporter import CompletionReporter
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolUsage
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phases import assert_, before_assert, cleanup, setup
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.string import lines_content


class _SymbolDefinitionInfo:
    def __init__(self,
                 definition: SymbolDefinition):
        self.definition = definition

    def name(self) -> str:
        return self.definition.name

    def value_type(self) -> ValueType:
        return self.definition.resolver_container.resolver.value_type

    def type_identifier(self) -> str:
        return ANY_TYPE_INFO_DICT[self.value_type()].identifier


class _TypeReportingInfo:
    def __init__(self, value_type: ValueType):
        self.type_info = ANY_TYPE_INFO_DICT[value_type]
        self.identifier_length = len(self.type_info.identifier)
        self.identifier = self.type_info.identifier


class ReportGenerator:
    def __init__(self,
                 output: StdOutputFiles,
                 completion_reporter: CompletionReporter,
                 test_case: test_case_doc.TestCase):
        self._output = output
        self._completion_reporter = completion_reporter
        self._test_case = test_case
        self._test_case_instructions = test_case.as_test_case_of_instructions()
        self._type_info_dict = {
            value_type: _TypeReportingInfo(value_type)
            for value_type in ValueType
        }

    def list(self) -> int:
        output_lines = self._get_list_lines(self._get_definitions())
        self._output.out.write(lines_content(output_lines))
        return self._completion_reporter.report_success()

    def _get_definitions(self) -> Iterable[_SymbolDefinitionInfo]:
        return itertools.chain.from_iterable([
            _definitions_from(self._test_case_instructions.setup_phase, setup.get_symbol_usages),
            _definitions_from(self._test_case_instructions.before_assert_phase, before_assert.get_symbol_usages),
            _definitions_from(self._test_case_instructions.assert_phase, assert_.get_symbol_usages),
            _definitions_from(self._test_case_instructions.cleanup_phase, cleanup.get_symbol_usages),
        ])

    def _get_list_lines(self, symbols: Iterable[_SymbolDefinitionInfo]) -> List[str]:
        symbol_list = list(symbols)
        symbol_line_formatter = self._symbol_line_formatter(symbol_list)
        return [
            symbol_line_formatter(symbol)
            for symbol in symbol_list
        ]

    def _symbol_line_formatter(self, symbols: List[_SymbolDefinitionInfo]) -> Callable[[_SymbolDefinitionInfo], str]:
        def get_identifier_length(symbol: _SymbolDefinitionInfo) -> int:
            return self._type_info_dict[symbol.value_type()].identifier_length

        max_type_identifier_len = functools.reduce(_max,
                                                   map(get_identifier_length, symbols),
                                                   0)
        type_formatting_string = '%-{}s'.format(max_type_identifier_len)

        def ret_val(symbol: _SymbolDefinitionInfo) -> str:
            return (type_formatting_string % symbol.type_identifier() +
                    ' ' +
                    symbol.name())

        return ret_val


_A = TypeVar('_A')


def _definitions_from(elements: Sequence[_A],
                      symbol_usages_getter: Callable[[_A], Sequence[SymbolUsage]]) -> Iterable[_SymbolDefinitionInfo]:
    symbol_usages_sequence_list = [
        symbol_usages_getter(element)
        for element in elements
    ]
    return map(_mk_definition,
               filter(_is_symbol_definition,
                      itertools.chain.from_iterable(symbol_usages_sequence_list))
               )


def _mk_definition(symbol_definition: SymbolDefinition) -> _SymbolDefinitionInfo:
    return _SymbolDefinitionInfo(symbol_definition)


def _is_symbol_definition(symbol_usage: SymbolUsage) -> bool:
    return isinstance(symbol_usage, SymbolDefinition)


def _max(x: int, y: int) -> int:
    return max(x, y)
